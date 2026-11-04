"""Rendu d'un épisode décrit par episode.yaml : plans, acteurs, répliques, effets, cartes, sous-titres, bruitages.

Sans voix, chaque réplique dure le temps de la lire et la bouche suit les lettres du texte.
Quand une voix existera (audio + minutage mot à mot), il suffira de fournir `minutage.json` à côté du fichier :
les durées et les bouches suivront alors l'audio (voir docs/EPISODES.md).
"""
import math, random, shutil, subprocess, tempfile
from bisect import bisect_right
from pathlib import Path

import yaml
from PIL import Image, ImageDraw

from . import cards, rig
from .config import FPS, H, NICHES, SFX, W
from .drawing import back_out, clamp, cover, ease_in_out, ease_out, font, rgb
from .face import visemes_for

READ_RATE = 2.7          # mots par seconde quand il n'y a pas de voix


def _h(s: str) -> int:
    return sum((i + 1) * ord(c) for i, c in enumerate(s))


# ── Effets ponctuels sur un acteur ───────────────────────────────────────────────────────────────────
def effect(name, s):
    """(dx, dy, squash, tilt, echelle) d'un effet, s secondes après son début."""
    if s < 0:
        return 0, 0, 0, 0, 1
    if name == 'hic':                    # sursaut : écrasé, puis projeté vers le haut, retombe
        k = math.exp(-s * 7)
        return 0, -90 * math.sin(min(s, .35) / .35 * math.pi) * (s < .35), -.9 * k * math.cos(s * 22), 4 * k * math.sin(s * 30), 1
    if name == 'saut':
        return 0, -160 * math.sin(clamp(s / .5) * math.pi), .4 * math.exp(-s * 6) * math.cos(s * 20), 0, 1
    if name == 'tremble':
        k = clamp(1 - s / .7)
        return 14 * k * math.sin(s * 70), 0, 0, 3 * k * math.sin(s * 55), 1
    if name == 'gonfle':
        return 0, 0, -.25 * ease_out(s / .4), 0, 1 + .12 * ease_out(s / .4)
    if name == 'apparait':
        return 0, 0, 0, 0, back_out(s / .4)
    if name == 'rot':                    # petit rebond de satisfaction
        return 0, -40 * math.sin(clamp(s / .3) * math.pi), .3 * math.exp(-s * 8), 0, 1
    return 0, 0, 0, 0, 1


DEFAULT_SFX = {'hic': 'boing', 'saut': 'swoosh', 'tremble': 'buzzer', 'apparait': 'pop', 'rot': 'pop'}

ACTION_DEFAULTS = {'dx': 0.0, 'dy': 0.0, 'angle': 0.0, 'echelle': 1.0}


def action_track(keys, label):
    """Compile les poses d'une piste en secondes locales au plan."""
    times, poses, curves = [0.0], [ACTION_DEFAULTS], ['douce']
    last = -1.0
    for key in keys:
        at = key.get('t')
        curve = key.get('courbe', 'douce')
        fields = {name: value for name, value in key.items() if name not in ('t', 'courbe')}
        if not isinstance(at, (int, float)) or not math.isfinite(at) or at < 0 or at <= last:
            raise ValueError(f'{label} : les temps de mouvement doivent être positifs ou nuls et strictement croissants')
        if curve not in ('douce', 'lineaire', 'maintien'):
            raise ValueError(f'{label} : courbe de mouvement inconnue : {curve}')
        for name, value in fields.items():
            if name not in ACTION_DEFAULTS or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f'{label} : valeur de mouvement invalide : {name}')
        pose = {**poses[-1], **fields}
        if pose['echelle'] <= 0:
            raise ValueError(f'{label} : l’échelle du mouvement doit être supérieure à zéro')
        if at == 0:
            poses[0] = pose
        else:
            times.append(at)
            poses.append(pose)
            curves.append(curve)
        last = at
    return times, poses, curves


def sample_action(track, t):
    times, poses, curves = track
    t = max(t, 0)
    right = bisect_right(times, t)
    left = right - 1
    if right == len(times) or curves[right] == 'maintien':
        return poses[left]
    q = (t - times[left]) / (times[right] - times[left])
    if curves[right] == 'douce':
        q = ease_in_out(q)
    return {name: value + (poses[right][name] - value) * q for name, value in poses[left].items()}


class Episode:
    def __init__(self, folder: Path, with_voice: bool | None = None):
        self.folder = Path(folder)
        self.cfg = yaml.safe_load((self.folder / 'episode.yaml').read_text())
        self.niche_dir = NICHES / self.cfg['niche']
        self.niche = yaml.safe_load((self.niche_dir / 'niche.yaml').read_text())
        self.palette = {**self.niche.get('palette', {}), **self.cfg.get('palette', {})}
        self.palette.setdefault('accent', '#FF5A5F')
        self.palette.setdefault('legende', '#FFD84D')
        self.with_voice = bool(self.cfg.get('voix')) if with_voice is None else with_voice
        self.actions = {
            (shot['id'], name): action_track(actor['mouvement'], f"{shot['id']}/{name}")
            for shot in self.cfg['plans']
            for name, actor in shot['acteurs'].items()
            if actor.get('mouvement')
        }
        self._timeline()
        for shot in self.shots:
            for name in shot['acteurs']:
                track = self.actions.get((shot['id'], name))
                if track and track[0][-1] > shot['t1'] - shot['t0'] + 1e-6:
                    raise ValueError(f"{shot['id']}/{name} : la dernière pose de mouvement dépasse la fin du plan")

    def path(self, rel):
        """Chemins relatifs : d'abord le dossier de l'épisode, puis celui de la niche."""
        for base in (self.folder, self.niche_dir):
            if (base / rel).exists():
                return base / rel
        raise FileNotFoundError(rel)

    def _timeline(self):
        t, self.lines, self.shots = 0.0, [], []
        for shot in self.cfg['plans']:
            s0 = t
            for ln in shot['repliques']:
                ln = dict(ln)
                words = len(ln.get('dit', '').split())
                d = ln.get('duree') or max(1.5, words / READ_RATE + .45)
                cast = self.cfg.get('voix') or {}
                if self.with_voice and ln.get('qui') in cast:      # la voix fixe la durée, les mots et les bouches
                    from . import voice
                    v = cast[ln['qui']]
                    v = v if isinstance(v, dict) else {'voix': v}
                    take = voice.tts(v['voix'], ln.get('jeu') or ln['dit'], v.get('stabilite'))
                    words_t, vis = voice.words_and_visemes(take['alignment'])
                    ln['audio'] = take['audio']
                    ln['mots'] = words_t
                    ln['visemes'] = vis
                    speak = words_t[-1][2] if words_t else voice.duration(take['audio'])
                    ln['parole'] = speak
                    d = max(ln.get('duree') or 0, voice.duration(take['audio']) + ln.get('pause', .35))
                self.lines.append({**ln, 'shot': shot['id'], 't0': t, 't1': t + d})
                t += d
            self.shots.append({**shot, 't0': s0, 't1': t})
        target = self.cfg.get('duree_cible')
        if target and not self.with_voice:                         # étirer ou resserrer pour coller à la durée voulue
            k = target / t
            for x in self.lines + self.shots:
                x['t0'] *= k; x['t1'] *= k
            t = target
        self.duration = t + .4

    # ── état de chaque acteur à l'instant t ──────────────────────────────────────────────────────────
    def actor_state(self, shot, name, spec, t, line, prev_lines):
        emo = spec.get('emotion', 'neutre')
        pose = spec.get('pose', 'defaut')
        for ln in prev_lines + [line]:     # la dernière émotion/pose donnée à cet acteur dans le plan
            if ln.get('qui') == name:
                emo, pose = ln.get('emotion', emo), ln.get('pose', pose)
            if name in (ln.get('reactions') or {}):
                emo = ln['reactions'][name]
            if name in (ln.get('poses') or {}):
                pose = ln['poses'][name]
        speaking = line.get('qui') == name
        mouth, talk = None, 0.0
        if speaking:
            talk = 1.0
            if line.get('visemes') is not None:
                vis = [(line['t0'] + tt, v) for tt, v in line['visemes']]
                end = line['t0'] + line.get('parole', 0) + .05
            else:
                vis = visemes_for(line.get('dit', ''), line['t0'] + .05, line['t1'] - .25)
                end = line['t1'] - .25
            cur = [v for tt, v in vis if tt <= t]
            mouth = cur[-1] if cur and t < end else None
            talk = 1.0 if t < end else 0.0
            if mouth == 'repos':
                mouth = 'M'
        # regard : vers celui qui parle, sinon droit devant ou cible donnée
        gaze = tuple(spec.get('regard', (0, 0)))
        if not speaking and line.get('qui') in shot['acteurs']:
            other = shot['acteurs'][line['qui']]
            dx, dy = other['x'] - spec['x'], other['y'] - spec['y']
            n = math.hypot(dx, dy) or 1
            gaze = (dx / n * .9, dy / n * .6)
        gaze = tuple((line.get('regards') or {}).get(name, gaze))
        rnd = random.Random(_h(name))
        period = 2.6 + rnd.random() * 1.8
        blink = (t + rnd.random() * period) % period < .1 and emo not in ('douleur', 'rire')
        fx = (0, 0, 0, 0, 1)
        for ln in prev_lines + [line]:
            e = (ln.get('effets') or {}).get(name)
            if e:
                fx = effect(e, t - ln['t0'] - ln.get('effet_delai', 0))
        return dict(emo=emo, pose=pose, mouth=mouth, talk=talk, gaze=gaze, blink=blink, fx=fx)

    # ── rendu ────────────────────────────────────────────────────────────────────────────────────────
    def render(self, out: Path | None = None, preview_every: int = 0):
        out = Path(out or self.folder / 'out' / f'{self.folder.name}.mp4')
        out.parent.mkdir(parents=True, exist_ok=True)
        decors = {s['id']: cover(Image.open(self.path(s['decor'])).convert('RGBA')) for s in self.shots}
        chars = {(s['id'], n): rig.load(self.path(a['perso'])) for s in self.shots for n, a in s['acteurs'].items()}
        self._chars = {n: c for (_, n), c in chars.items()}
        shade = _bottom_shade() if self.cfg.get('degrade_bas', True) else None
        tmp = Path(tempfile.mkdtemp())
        n_frames = int(self.duration * FPS)
        # les images partent directement dans ffmpeg (rien d'écrit sur le disque)
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                                '-i', '-', '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', str(tmp / 'v.mp4')], stdin=subprocess.PIPE)
        for f in range(n_frames):
            t = f / FPS
            si = next((i for i, s in enumerate(self.shots) if s['t0'] <= t < s['t1']), len(self.shots) - 1)
            shot = self.shots[si]
            lines = [l for l in self.lines if l['shot'] == shot['id']]
            li = next((i for i, l in enumerate(lines) if l['t0'] <= t < l['t1']), len(lines) - 1)
            line = lines[li]
            frame = decors[shot['id']].copy()
            placed = self._place_actors(shot, lines, li, line, t, chars)
            for a in placed:
                frame.alpha_composite(a['img'], a['pos'])
            frame, view = self._camera_frame(frame, shot, t)
            self._actor_labels(frame, shot, t, placed, view)
            # transition entre plans : le nouveau plan glisse depuis la droite
            if si > 0 and shot.get('transition') != 'coupe' and t - shot['t0'] < .3:
                q = ease_out((t - shot['t0']) / .3)
                prev = decors[self.shots[si - 1]['id']].copy()
                prev.alpha_composite(frame.crop((0, 0, int(W * q) or 1, H)), (int(W * (1 - q)), 0))
                frame = prev
            if shade is not None:
                frame.alpha_composite(shade)
            # carte de la réplique (ou gardée depuis une réplique précédente)
            card_line = next((l for l in reversed(lines[:li + 1]) if l.get('carte') and (l is line or l['carte'].get('garde'))), None)
            if card_line:
                c = card_line['carte']
                p = t - card_line['t0']
                img = cards.draw(c, p, card_line['t1'] - card_line['t0'], self.palette)
                s = back_out(p / .35)
                if s > .02:
                    img = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
                    cy = {'haut': 430, 'centre': 860, 'bas': 1250}[c.get('position', 'haut')]
                    frame.alpha_composite(img, (int(W / 2 - img.width / 2), int(cy - img.height / 2)))
            self._caption(frame, line, t)
            self._watermark(frame, t)
            enc.stdin.write(frame.convert('RGB').tobytes())
            if preview_every and f % preview_every == 0:
                print(f'  image {f}/{n_frames}', flush=True)
        enc.stdin.close()
        if enc.wait() != 0:
            raise RuntimeError('ffmpeg a échoué pendant l\'encodage des images')
        try:
            self._encode(tmp, out)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        return out

    def _camera_frame(self, frame, shot, t):
        z0, z1 = shot.get('zoom', (1.0, 1.04))
        z = z0 + (z1 - z0) * ease_in_out((t - shot['t0']) / max(.1, shot['t1'] - shot['t0']))
        if abs(z - 1) <= 1e-3:
            return frame, (0, 0, W, H)
        cx, cy = shot.get('centre', (W / 2, H / 2))
        w, h = W / z, H / z
        x, y = clamp(cx - w / 2, 0, W - w), clamp(cy - h / 2, 0, H - h)
        view = (int(x), int(y), int(x + w), int(y + h))
        return frame.crop(view).resize((W, H), Image.LANCZOS), view

    def _actor_labels(self, frame, shot, t, placed, view):
        """Les épisodes sous-titrés peuvent annoter les acteurs après le cadrage."""

    def _place_actors(self, shot, lines, li, line, t, chars):
        """Acteurs visibles à l'instant t, du fond vers l'avant (y croissant) : image, position, repère du visage à l'écran."""
        out = []
        for name, spec in sorted(shot['acteurs'].items(), key=lambda kv: kv[1]['y']):
            if spec.get('entre') is not None and li < spec['entre']:
                continue
            # entrée / sortie en glissant, déplacements demandés par les répliques
            ex, ey, walking, facing = self._motion(name, spec, lines, li, t)
            if ex is None:
                continue
            spec = {**spec, 'x': ex, 'y': ey}
            if facing and chars[(shot['id'], name)].limbs:
                spec['miroir'] = facing < 0
            st = self.actor_state(shot, name, spec, t, line, lines[:li])
            ch = chars[(shot['id'], name)]
            dx, dy, squash, tilt, k = st['fx']
            track = self.actions.get((shot['id'], name))
            if track:
                action = sample_action(track, t - shot['t0'])
                dx += action['dx']
                dy += action['dy']
                tilt += action['angle']
                k *= action['echelle']
            if spec.get('miroir'):           # image retournée : le regard aussi
                st['gaze'] = (-st['gaze'][0], st['gaze'][1])
            img, anchor = ch.render(st['pose'], st['emo'], st['gaze'], st['blink'], st['mouth'], t, st['talk'], squash, tilt,
                                    phase=_h(name) % 7, walk=walking, facing=-1 if spec.get('miroir') else 1,
                                    layer_angles=st.get('layer_angles'))
            sc = spec.get('echelle', 1.0) * ch.scale * k
            if sc <= .01:
                continue
            fx_, fy_, fr = ch.face_point()
            px = ch.layers[0]['pivot']
            face = (fx_ - px[0], fy_ - px[1])
            if spec.get('miroir') and not ch.limbs:    # avec membres, le rig gère lui-même l'orientation (corps symétrique)
                img = img.transpose(Image.FLIP_LEFT_RIGHT); anchor = (img.width - anchor[0], anchor[1]); face = (-face[0], face[1])
            img = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.LANCZOS)
            pos = (int(spec['x'] + dx - anchor[0] * sc), int(spec['y'] + dy - anchor[1] * sc))
            leaving = spec.get('sort') is not None and li >= spec['sort']
            out.append(dict(name=name, img=img, pos=pos, face=(spec['x'] + dx + face[0] * sc, spec['y'] + dy + face[1] * sc), face_r=fr * sc,
                            sortant=leaving))
        return out

    def _motion(self, name, spec, lines, li, t):
        """Position (x, y) de l'acteur à l'instant t, ou (None, None) s'il est déjà sorti.

        entre: n + arrivee: gauche|droite|bas|haut|pop ; sort: n + depart: … ; deplace: {acteur: [x, y]} dans une réplique."""
        x, y = spec['x'], spec['y']
        hop, moving, facing = 0.0, 0.0, 0
        for j, ln in enumerate(lines[:li + 1]):
            tgt = (ln.get('deplace') or {}).get(name)
            if tgt:
                dur = max(.4, abs(tgt[0] - x) / 520)          # ~420 px/s de marche
                q = clamp((t - ln['t0']) / dur) if j == li else 1.0
                e = ease_in_out(q) if not self._walks(name) else q
                if 0 < q < 1:
                    moving = 1.0
                    facing = 1 if tgt[0] >= x else -1
                    if not self._walks(name):
                        hop = -abs(math.sin(q * math.pi * 3)) * 25
                x, y = x + (tgt[0] - x) * e, y + (tgt[1] - y) * e
        dirs = {'gauche': (-900, 0), 'droite': (900, 0), 'bas': (0, 900), 'haut': (0, -1100)}
        if spec.get('entre') is not None and spec.get('arrivee', 'pop') in dirs and li >= spec['entre']:
            ox, oy = dirs[spec['arrivee']]
            walks = self._walks(name) and spec['arrivee'] in ('gauche', 'droite')
            dur = abs(ox) / 520 if walks else .5
            q = clamp((t - lines[spec['entre']]['t0']) / dur)
            q = q if walks else ease_out(q)
            if q < 1:
                moving, facing = (1.0, -1 if ox > 0 else 1) if walks else (moving, facing)
            x, y = x + ox * (1 - q), y + oy * (1 - q)
        if spec.get('sort') is not None and li >= spec['sort']:
            ox, oy = dirs.get(spec.get('depart', 'droite'), (900, 0))
            walks = self._walks(name) and spec.get('depart', 'droite') in ('gauche', 'droite')
            dur = abs(ox) / 520 if walks else .5
            q = clamp((t - lines[spec['sort']]['t0'] - spec.get('sort_delai', .3)) / dur)
            if q >= 1:
                return None, None, 0.0, 0
            if q > 0:
                moving, facing = (1.0, 1 if ox > 0 else -1) if walks else (moving, facing)
            e = q if walks else q * q
            x, y = x + ox * e, y + oy * e
        return x, y + hop, moving, facing

    def _walks(self, name):
        ch = self._chars.get(name)
        return bool(ch and ch.limbs.get('jambes'))

    def controle(self, out_dir: Path | None = None):
        """Contrôle de mise en scène, une image au milieu de chaque réplique : visages dans l'écran, pas cachés
        (ni par un autre acteur, ni par une carte, ni par les sous-titres), celui qui parle bien visible.
        Écrit une planche (une image par réplique) et renvoie la liste des problèmes."""
        import numpy as np
        out_dir = Path(out_dir or self.folder / 'out')
        out_dir.mkdir(parents=True, exist_ok=True)
        decors = {s['id']: cover(Image.open(self.path(s['decor'])).convert('RGBA')) for s in self.shots}
        chars = {(s['id'], n): rig.load(self.path(a['perso'])) for s in self.shots for n, a in s['acteurs'].items()}
        self._chars = {n: c for (_, n), c in chars.items()}
        problems, thumbs = [], []
        for n, line in enumerate(self.lines, 1):
            t = (line['t0'] + line['t1']) / 2
            shot = next(s for s in self.shots if s['id'] == line['shot'])
            lines = [l for l in self.lines if l['shot'] == shot['id']]
            li = lines.index(line)
            actors = self._place_actors(shot, lines, li, line, t, chars)
            frame = decors[shot['id']].copy()
            masks = []
            for a in actors:
                frame.alpha_composite(a['img'], a['pos'])
                m = np.zeros((H, W), bool)
                al = np.array(a['img'].getchannel('A')) > 128
                x, y = a['pos']
                x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + al.shape[1]), min(H, y + al.shape[0])
                if x1 > x0 and y1 > y0:
                    m[y0:y1, x0:x1] = al[y0 - y:y1 - y, x0 - x:x1 - x]
                masks.append(m)
            card_box = None
            card_line = next((l for l in reversed(lines[:li + 1]) if l.get('carte') and (l is line or l['carte'].get('garde'))), None)
            if card_line:
                img = cards.draw(card_line['carte'], t - card_line['t0'], card_line['t1'] - card_line['t0'], self.palette)
                cy = {'haut': 430, 'centre': 860, 'bas': 1250}[card_line['carte'].get('position', 'haut')]
                bb = img.getbbox() or (0, 0, 0, 0)
                card_box = (W / 2 - img.width / 2 + bb[0], cy - img.height / 2 + bb[1], W / 2 - img.width / 2 + bb[2], cy - img.height / 2 + bb[3])
                frame.alpha_composite(img, (int(W / 2 - img.width / 2), int(cy - img.height / 2)))
            d = ImageDraw.Draw(frame)
            cap_top = self.cfg.get('legendes_y', 1580) - 70
            for i, a in enumerate(actors):
                fx, fy, r = a['face'][0], a['face'][1], max(12, a['face_r'] * 1.6)
                tag = f"réplique {n} ({line.get('qui')}) — {a['name']}"
                if a.get('sortant'):          # en train de sortir de l'écran : normal qu'il soit coupé
                    continue
                if fx - r < 0 or fx + r > W or fy - r < 0:
                    problems.append(f'{tag} : visage coupé par le bord de l\'écran')
                if fy + r > cap_top:
                    problems.append(f'{tag} : visage dans la zone des sous-titres')
                if card_box and fx + r > card_box[0] and fx - r < card_box[2] and fy + r > card_box[1] and fy - r < card_box[3]:
                    problems.append(f'{tag} : visage caché par la carte')
                yy, xx = np.ogrid[:H, :W]
                disk = (xx - fx) ** 2 + (yy - fy) ** 2 < r * r
                over = np.zeros((H, W), bool)
                for m in masks[i + 1:]:
                    over |= m
                if disk.sum() and (disk & over).sum() / disk.sum() > .2:
                    problems.append(f'{tag} : visage caché par un autre personnage ({int(100 * (disk & over).sum() / disk.sum())} %)')
                if a['name'] == line.get('qui'):
                    vis = masks[i] & ~over
                    if masks[i].sum() and vis.sum() / masks[i].sum() < .6:
                        problems.append(f'{tag} : celui qui parle n\'est visible qu\'à {int(100 * vis.sum() / masks[i].sum())} %')
                d.ellipse((fx - r, fy - r, fx + r, fy + r), outline=(255, 0, 0, 255) if any(tag in p for p in problems) else (0, 220, 0, 255), width=5)
            d.text((20, 20), f'{n}. {line.get("qui", "")} : {line.get("dit", "")[:40]}', fill='white', font=font('Fredoka', 36),
                   stroke_width=3, stroke_fill='black')
            thumbs.append(frame.convert('RGB').resize((W // 3, H // 3)))
        cols = 6
        sheet = Image.new('RGB', (cols * (W // 3), ((len(thumbs) + cols - 1) // cols) * (H // 3)), 'black')
        for i, th in enumerate(thumbs):
            sheet.paste(th, ((i % cols) * (W // 3), (i // cols) * (H // 3)))
        sheet.save(out_dir / 'controle.jpg', quality=85)
        (out_dir / 'controle.txt').write_text('\n'.join(problems) or 'Aucun problème détecté.')
        return problems

    def _caption(self, frame, line, t):
        words = []
        for w in line.get('dit', '').split():      # la ponctuation seule reste collée au mot d'avant
            if words and not any(c.isalnum() for c in w):
                words[-1] += ' ' + w
            else:
                words.append(w)
        if not words or line.get('sans_legende'):
            return
        span = (line['t1'] - line['t0']) * .9
        if line.get('mots') and len(line['mots']) == len(words):      # minutage réel de la voix
            starts = [line['t0'] + w[1] for w in line['mots']]
            i = max(0, sum(1 for s0 in starts if s0 <= t) - 1)
            span = max(.01, line['t1'] - line['t0'])
        else:
            i = min(len(words) - 1, int((t - line['t0']) / span * len(words)))
        if self.cfg.get('legendes_mode') == 'mot_blanc':
            d = ImageDraw.Draw(frame)
            word = words[i].upper()
            f = font('LuckiestGuy', 60)
            while d.textlength(word, font=f) > W - 80 and f.size > 18:
                f = font('LuckiestGuy', f.size - 6)
            d.text((W // 2, self.cfg.get('legendes_y', 1460)), word, font=f, fill='white',
                   stroke_width=5, stroke_fill=(20, 14, 18), anchor='mm')
            return
        g0 = (i // 3) * 3
        group = words[g0:g0 + 3]
        d = ImageDraw.Draw(frame)
        f = font('LuckiestGuy', 84)
        texts = [w.upper().replace('«', '"').replace('»', '"') for w in group]   # la police n'a pas les guillemets français
        total = sum(d.textlength(x + ' ', font=f) for x in texts)
        while total > W - 80:
            f = font('LuckiestGuy', f.size - 6); total = sum(d.textlength(x + ' ', font=f) for x in texts)
        x = (W - total) / 2
        y = self.cfg.get('legendes_y', 1580)
        since = (t - line['t0']) - i * span / len(words)
        for j, wtxt in enumerate(texts):
            cur = g0 + j == i
            col = rgb(self.palette['legende']) if cur else (255, 255, 255, 255)
            yy = y - (10 * (1 - ease_out(since / .12)) if cur else 0)
            if g0 + j <= i:
                d.text((x, yy), wtxt, font=f, fill=col, stroke_width=9, stroke_fill=(20, 14, 18), anchor='lm')
            x += d.textlength(wtxt + ' ', font=f)

    def _watermark(self, frame, t):
        signature = self.niche.get('direction_artistique', {}).get('signature')
        txt = (signature or {}).get('texte') or self.cfg.get('filigrane', self.niche.get('filigrane'))
        if not txt:
            return
        if signature:
            if spots := signature.get('positions'):
                duration = signature['intervalle_s']
                step, elapsed = divmod(t, duration)
                i = int(step) % len(spots)
                q = ease_in_out(clamp((elapsed - duration + signature['trajet_s']) / signature['trajet_s']))
                x, y = spots[i]
                nx, ny = spots[(i + 1) % len(spots)]
                x = round(x + (nx - x) * q)
                y = round(y + (ny - y) * q)
                face = font('Fredoka', signature['taille'])
                width = math.ceil(face.getlength(txt))
                layer = Image.new('RGBA', (width + 8, face.size * 2))
                ImageDraw.Draw(layer).text((4, face.size), txt, font=face,
                                           fill=(255, 255, 255, signature['opacite']), anchor='lm')
                frame.alpha_composite(layer, (min(x, W - width - 108), y - face.size))
                return
            x, y = signature['position']
            face = font('Fredoka', 36)
            width = math.ceil(face.getlength(txt))
            moving = signature.get('periode_s')
            layer = Image.new('RGBA', frame.size)
            draw = ImageDraw.Draw(layer)
            if moving:
                travel = max(0, signature['bord_droit'] - width - x)
                x += round(travel * (.5 - .5 * math.cos(2 * math.pi * t / moving)))
                draw.rounded_rectangle((x - 12, y - 23, x + width + 12, y + 23),
                                       radius=18, fill=(24, 19, 19, 108))
                tone = (255, 249, 237)
            else:
                r, g, b = frame.getpixel((min(W - 1, x + width // 2), y))[:3]
                light_wall = .2126 * r + .7152 * g + .0722 * b > 165
                tone = (49, 47, 45) if light_wall else (255, 249, 237)
            # Composer le texte séparément pour conserver le fond sous l’encre semi-transparente.
            text_layer = Image.new('RGBA', (width + 4, 46))
            ImageDraw.Draw(text_layer).text((2, 23), txt, font=face,
                                            fill=(*tone, signature['opacite']), anchor='lm')
            layer.alpha_composite(text_layer, (x - 2, y - 23))
            frame.alpha_composite(layer)
            return
        spots = [(140, 260), (760, 300), (180, 1250), (800, 1180)]
        x, y = spots[int(t // 6) % len(spots)]
        layer = Image.new('RGBA', frame.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((x, y), txt, font=font('Fredoka', 34), fill=(255, 255, 255, 70), anchor='mm')
        frame.alpha_composite(layer)

    def _encode(self, tmp, out):
        video = tmp / 'v.mp4'
        sounds = []                                  # (fichier, instant, volume)
        lib = self.cfg.get('bruitages') or {}

        def snd(name):
            if name in lib:
                if lib[name].get('fichier'):
                    return self.path(lib[name]['fichier']), lib[name].get('volume', .8)
                from . import voice
                return voice.sfx(lib[name]['texte'], lib[name].get('duree', 1.5)), lib[name].get('volume', .8)
            return SFX / f'{name}.mp3', .5
        for l in self.lines:
            if l.get('audio'):
                sounds.append((l['audio'], l['t0'], 1.0))
            for item in l.get('sfx', []) or []:
                name, _, delay = str(item).partition('@')
                f, vol = snd(name)
                sounds.append((f, l['t0'] + float(delay or 0), vol))
            for e in (l.get('effets') or {}).values():
                if e in DEFAULT_SFX and not l.get('sfx'):
                    sounds.append((SFX / f'{DEFAULT_SFX[e]}.mp3', l['t0'] + l.get('effet_delai', 0), .5))
            if l.get('carte') and not l.get('sfx'):
                sounds.append((SFX / 'pop.mp3', l['t0'], .5))
        for s_ in self.shots[1:]:
            if s_.get('transition') != 'coupe':
                sounds.append((SFX / 'whoosh.mp3', s_['t0'], .5))
        inputs, parts = [], []
        for i, (f, at, vol) in enumerate(sounds):
            inputs += ['-i', str(f)]
            ms = int(at * 1000)
            parts.append(f'[{i + 1}:a]aresample=48000,adelay={ms}|{ms},volume={vol}[s{i}]')
        if sounds:
            mix = ''.join(f'[s{i}]' for i in range(len(sounds)))
            fc = f'{";".join(parts)};{mix}amix=inputs={len(sounds)}:normalize=0,apad,atrim=0:{self.duration},loudnorm=I=-14:TP=-1.5[a]'
            cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', str(video), *inputs, '-filter_complex', fc, '-map', '0:v', '-map', '[a]']
        else:
            cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', str(video), '-f', 'lavfi', '-i', f'anullsrc=r=48000:cl=stereo',
                   '-map', '0:v', '-map', '1:a']
        subprocess.run(cmd + ['-t', str(self.duration), '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                              '-movflags', '+faststart', str(out)], check=True)


def _bottom_shade():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(1400, H):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(140 * min(1, (y - 1400) / 260))))
    return im
