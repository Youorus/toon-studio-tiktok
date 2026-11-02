"""Rendu d'un épisode décrit par episode.yaml : plans, acteurs, répliques, effets, cartes, sous-titres, bruitages.

Sans voix, chaque réplique dure le temps de la lire et la bouche suit les lettres du texte.
Quand une voix existera (audio + minutage mot à mot), il suffira de fournir `minutage.json` à côté du fichier :
les durées et les bouches suivront alors l'audio (voir docs/EPISODES.md).
"""
import math, random, shutil, subprocess, tempfile
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


class Episode:
    def __init__(self, folder: Path):
        self.folder = Path(folder)
        self.cfg = yaml.safe_load((self.folder / 'episode.yaml').read_text())
        self.niche_dir = NICHES / self.cfg['niche']
        self.niche = yaml.safe_load((self.niche_dir / 'niche.yaml').read_text())
        self.palette = {**self.niche.get('palette', {}), **self.cfg.get('palette', {})}
        self.palette.setdefault('accent', '#FF5A5F')
        self.palette.setdefault('legende', '#FFD84D')
        self._timeline()

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
                words = len(ln.get('dit', '').split())
                d = ln.get('duree') or max(1.5, words / READ_RATE + .45)
                self.lines.append({**ln, 'shot': shot['id'], 't0': t, 't1': t + d})
                t += d
            self.shots.append({**shot, 't0': s0, 't1': t})
        target = self.cfg.get('duree_cible')
        if target:                         # étirer ou resserrer pour coller à la durée voulue
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
            vis = visemes_for(line.get('dit', ''), line['t0'] + .05, line['t1'] - .25)
            cur = [v for tt, v in vis if tt <= t]
            mouth = cur[-1] if cur and t < line['t1'] - .25 else None
            if mouth == 'repos':
                mouth = 'M'
        # regard : vers celui qui parle, sinon droit devant ou cible donnée
        gaze = tuple(spec.get('regard', (0, 0)))
        if not speaking and line.get('qui') in shot['acteurs']:
            other = shot['acteurs'][line['qui']]
            dx, dy = other['x'] - spec['x'], other['y'] - spec['y']
            n = math.hypot(dx, dy) or 1
            gaze = (dx / n * .9, dy / n * .6)
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
        shade = _bottom_shade()
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
            # acteurs, du fond vers l'avant (y croissant)
            for name, spec in sorted(shot['acteurs'].items(), key=lambda kv: kv[1]['y']):
                if spec.get('entre') is not None and li < spec['entre']:
                    continue
                st = self.actor_state(shot, name, spec, t, line, lines[:li])
                ch = chars[(shot['id'], name)]
                dx, dy, squash, tilt, k = st['fx']
                img, anchor = ch.render(st['pose'], st['emo'], st['gaze'], st['blink'], st['mouth'], t, st['talk'], squash, tilt,
                                        phase=_h(name) % 7)
                sc = spec.get('echelle', 1.0) * ch.scale * k
                if sc <= .01:
                    continue
                if spec.get('miroir'):
                    img = img.transpose(Image.FLIP_LEFT_RIGHT); anchor = (img.width - anchor[0], anchor[1])
                img = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.LANCZOS)
                frame.alpha_composite(img, (int(spec['x'] + dx - anchor[0] * sc), int(spec['y'] + dy - anchor[1] * sc)))
            # caméra : léger travelling avant sur le plan
            z0, z1 = shot.get('zoom', (1.0, 1.04))
            z = z0 + (z1 - z0) * ease_in_out((t - shot['t0']) / max(.1, shot['t1'] - shot['t0']))
            if abs(z - 1) > 1e-3:
                cx, cy = shot.get('centre', (W / 2, H / 2))
                w, h = W / z, H / z
                x0, y0 = clamp(cx - w / 2, 0, W - w), clamp(cy - h / 2, 0, H - h)
                frame = frame.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.LANCZOS)
            # transition entre plans : le nouveau plan glisse depuis la droite
            if si > 0 and t - shot['t0'] < .3:
                q = ease_out((t - shot['t0']) / .3)
                prev = decors[self.shots[si - 1]['id']].copy()
                prev.alpha_composite(frame.crop((0, 0, int(W * q) or 1, H)), (int(W * (1 - q)), 0))
                frame = prev
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
        i = min(len(words) - 1, int((t - line['t0']) / span * len(words)))
        g0 = (i // 3) * 3
        group = words[g0:g0 + 3]
        d = ImageDraw.Draw(frame)
        f = font('LuckiestGuy', 84)
        texts = [w.upper() for w in group]
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
        txt = self.niche.get('filigrane')
        if not txt:
            return
        spots = [(140, 260), (760, 300), (180, 1250), (800, 1180)]
        x, y = spots[int(t // 6) % len(spots)]
        layer = Image.new('RGBA', frame.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((x, y), txt, font=font('Fredoka', 34), fill=(255, 255, 255, 70), anchor='mm')
        frame.alpha_composite(layer)

    def _encode(self, tmp, out):
        video = tmp / 'v.mp4'
        sounds = []
        for i, l in enumerate(self.lines):
            for name in l.get('sfx', []) or []:
                sounds.append((name, l['t0']))
            for e in (l.get('effets') or {}).values():
                if e in DEFAULT_SFX and not l.get('sfx'):
                    sounds.append((DEFAULT_SFX[e], l['t0'] + l.get('effet_delai', 0)))
            if l.get('carte') and not l.get('sfx'):
                sounds.append(('pop', l['t0']))
        for s in self.shots[1:]:
            sounds.append(('whoosh', s['t0']))
        inputs, parts = [], []
        for i, (name, at) in enumerate(sounds):
            inputs += ['-i', str(SFX / f'{name}.mp3')]
            ms = int(at * 1000)
            parts.append(f'[{i + 1}:a]adelay={ms}|{ms},volume=.5[s{i}]')
        if sounds:
            mix = ''.join(f'[s{i}]' for i in range(len(sounds)))
            fc = f'{";".join(parts)};{mix}amix=inputs={len(sounds)}:normalize=0,apad,atrim=0:{self.duration},loudnorm=I=-16:TP=-1.5[a]'
            cmd = ['ffmpeg', '-v', 'error', '-y', '-i', str(video), *inputs, '-filter_complex', fc, '-map', '0:v', '-map', '[a]']
        else:
            cmd = ['ffmpeg', '-v', 'error', '-y', '-i', str(video), '-f', 'lavfi', '-i', f'anullsrc=r=48000:cl=stereo', '-t', str(self.duration),
                   '-map', '0:v', '-map', '1:a']
        subprocess.run(cmd + ['-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(out)], check=True)


def _bottom_shade():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(1400, H):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(140 * min(1, (y - 1400) / 260))))
    return im
