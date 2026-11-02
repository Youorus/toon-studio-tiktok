"""Personnage en couches (« rig ») décrit par un fichier personnage.yaml.

Un personnage = des couches PNG transparentes (corps, tête, bras, accessoires…), chacune avec :
  - un pivot (le point de l'image autour duquel elle tourne) ;
  - un parent et un point d'attache sur ce parent (l'épaule pour un bras, le cou pour la tête) ;
  - une ou plusieurs variantes d'image (bras « repos », « levé », « pointe »…).
Une pose choisit pour chaque couche une variante et un angle. Un visage procédural (yeux, sourcils, bouche)
est dessiné sur la couche indiquée. Les organes sont des personnages à une seule couche.

Voir docs/PERSONNAGES.md pour le format complet.
"""
import math
from pathlib import Path

import numpy as np
import yaml
from PIL import Image

from .arms import draw_arm
from .drawing import affine_paste, transform_point
from .face import FaceSpec, face_overlay, register


class Character:
    def __init__(self, folder: Path):
        self.folder = Path(folder)
        cfg = yaml.safe_load((self.folder / 'personnage.yaml').read_text())
        self.cfg = cfg
        self.name = cfg.get('nom', self.folder.name)
        self.kind = cfg.get('type', 'organe')
        self.scale = cfg.get('echelle', 1.0)
        self.layers = []
        for L in cfg['couches']:
            imgs = L['images'] if isinstance(L['images'], dict) else {'defaut': L['images']}
            self.layers.append(dict(
                id=L['id'], parent=L.get('parent'), attach=tuple(L.get('attache', (0, 0))), pivot=tuple(L['pivot']),
                images={k: Image.open(self.folder / v).convert('RGBA') for k, v in imgs.items()},
                z=L.get('z', 0)))
        cut = cfg.get('decoupe_tete')
        if cut:                                  # une seule image -> corps + tête qui peut pencher
            root = self.layers[0]
            full = root['images']['defaut']
            a = np.array(full)
            body, head = a.copy(), a.copy()
            body[:cut['y'] - 6, :, 3] = 0
            head[cut['y']:, :, 3] = 0
            root['images']['defaut'] = Image.fromarray(body)
            self.layers.append(dict(id='tete', parent=root['id'], attach=tuple(cut['cou']), pivot=tuple(cut['cou']),
                                    images={'defaut': Image.fromarray(head)}, z=root['z'] + 1))
        self.by_id = {L['id']: L for L in self.layers}
        self.arms = cfg.get('bras', []) or []
        f = cfg.get('visage')
        self.face_layer = f['couche'] if f else None
        self.face_key = register(str(self.folder), FaceSpec(
            eyes=tuple(f['yeux']), eye_r=f['rayon_oeil'], gap=f.get('ecart', 1.9),
            mouth=tuple(f['bouche']) if f.get('bouche') else None, mouth_w=f.get('largeur_bouche'),
            skin=f.get('peau', '#F2A7A0'), line=f.get('trait', .07), eye_shape=f.get('forme_oeil', 1.12),
            brows=f.get('sourcils', True), lid_base=f.get('paupiere', 0.0), pupil=f.get('pupille', 1.0),
            glasses=f.get('lunettes'), lashes=f.get('cils', False))) if f else None
        self.poses = cfg.get('poses', {}) or {}
        self.poses.setdefault('defaut', {})
        m = cfg.get('mouvement', {}) or {}
        self.softness = m.get('souplesse', 1.0 if self.kind == 'organe' else .3)
        self.breath = m.get('respiration', .012)

    # --------------------------------------------------------------------------------------------------
    def layer_image(self, L, variant, emo, gaze, blink, mouth):
        img = L['images'].get(variant) or L['images'].get('defaut') or next(iter(L['images'].values()))
        if L['id'] != self.face_layer:
            return img
        return _with_face(id(img), img, self.face_key, emo, gaze, blink, mouth)

    def render(self, pose='defaut', emo='neutre', gaze=(0, 0), blink=False, mouth=None, t=0.0, talk=0.0,
               squash=0.0, tilt=0.0, phase=0.0):
        """Image du personnage et position de son point d'ancrage (bas-centre) dans cette image.

        talk : 0..1, intensité de la parole (rebond) ; squash : écrasement ponctuel (-1..1) ; tilt : penché (degrés).
        """
        P = self.poses.get(pose, {})
        root = self.layers[0]
        w0, h0 = root['images']['defaut' if 'defaut' in root['images'] else next(iter(root['images']))].size
        pad = int(max(w0, h0) * .9)
        canvas = Image.new('RGBA', (w0 + 2 * pad, h0 + 2 * pad), (0, 0, 0, 0))
        anchor = (pad + root['pivot'][0], pad + root['pivot'][1])
        # mouvement vivant : respiration, rebond de parole, écrasement (squash & stretch) des organes
        wob = math.sin(t * 2 * math.pi * .9 + phase)
        s = self.softness
        sy = 1 + self.breath * math.sin(t * 2 * math.pi / 3.2 + phase) + s * (.035 * talk * abs(math.sin(t * 11)) + .18 * squash)
        sx = 1 + s * (-.02 * talk * abs(math.sin(t * 11)) - .12 * squash)
        root_angle = tilt + s * 2.0 * wob + P.get(root['id'], {}).get('angle', 0)
        placed = {}
        order = sorted(self.layers, key=lambda L: L['z'])
        # placer d'abord la racine puis les enfants (les parents avant leurs enfants)
        todo = [root] + [L for L in self.layers if L is not root]
        for L in todo:
            spec = P.get(L['id'], {})
            variant = spec.get('image', 'defaut')
            if L is root:
                placed[L['id']] = dict(to=anchor, angle=root_angle, sx=sx, sy=sy, variant=variant)
            else:
                par = placed[L['parent']]
                pl = self.by_id[L['parent']]
                to = transform_point(L['attach'], pl['pivot'], par['to'], par['angle'], par['sx'], par['sy'])
                own = spec.get('angle', 0)
                if L['id'] == self.face_layer or L['id'].startswith('tete'):
                    own += 2.5 * math.sin(t * 1.3 + phase) + 3 * talk * math.sin(t * 7)
                elif L['id'].startswith('bras'):
                    own += 1.5 * math.sin(t * 1.7 + phase + len(L['id']))
                placed[L['id']] = dict(to=to, angle=par['angle'] + own, sx=1, sy=1, variant=variant)
        root_p = placed[root['id']]

        def arms(front):
            for arm in self.arms:
                if bool(arm.get('devant', True)) != front:
                    continue
                spec = {**{'epaule': 8, 'coude': 4, 'main': 'repos'}, **P.get(arm['id'], {})}
                sh = transform_point(arm['epaule'], root['pivot'], root_p['to'], root_p['angle'], root_p['sx'], root_p['sy'])
                swing = 2.0 * math.sin(t * 1.6 + phase + arm['cote']) + talk * 6 * math.sin(t * 5 + arm['cote'])
                draw_arm(canvas, sh, arm['cote'], arm, spec['epaule'] + swing, spec['coude'] + talk * 5 * math.sin(t * 6),
                         spec['main'], 1.0, root_p['angle'])

        arms(False)
        for L in order:
            p = placed[L['id']]
            img = self.layer_image(L, p['variant'], emo, gaze, blink, mouth)
            affine_paste(canvas, img, L['pivot'], p['to'], p['angle'], p['sx'], p['sy'])
        arms(True)
        bb = canvas.getbbox() or (0, 0, 1, 1)
        return canvas.crop(bb), (anchor[0] - bb[0], anchor[1] - bb[1])


_FACE_CACHE: dict = {}


def _with_face(img_id, img, face_key, emo, gaze, blink, mouth):
    k = (img_id, face_key, emo, gaze, blink, mouth)
    if k not in _FACE_CACHE:
        if len(_FACE_CACHE) > 3000:
            _FACE_CACHE.clear()
        out = img.copy()
        out.alpha_composite(face_overlay(face_key, emo, gaze, blink, mouth, img.size))
        _FACE_CACHE[k] = out
    return _FACE_CACHE[k]


_CHARS: dict = {}


def load(folder: Path) -> Character:
    folder = Path(folder)
    if folder not in _CHARS:
        _CHARS[folder] = Character(folder)
    return _CHARS[folder]


def auto_setup_organ(png: Path, name: str, skin: str | None = None) -> dict:
    """Configuration de départ pour un organe ou un objet d'une seule image : pivot en bas au centre ; le visage se place
    dans la partie la plus épaisse de la forme (point le plus éloigné des bords), à une taille proportionnée."""
    from scipy import ndimage
    img = Image.open(png).convert('RGBA')
    a = np.array(img)
    w, h = img.size
    mask = a[:, :, 3] > 200
    dt = ndimage.distance_transform_edt(mask)
    dt[int(h * .8):, :] *= .6                      # préférer le haut de la forme
    cy, cx = np.unravel_index(np.argmax(dt), dt.shape)
    R = float(dt[cy, cx])
    r = max(14, min(R * .42, min(w, h) * .13))
    if skin is None:
        y0, y1, x0, x1 = max(0, int(cy - R * .5)), int(cy + R * .5), max(0, int(cx - R * .5)), int(cx + R * .5)
        region = a[y0:y1, x0:x1][mask[y0:y1, x0:x1]][:, :3]
        skin = '#%02X%02X%02X' % tuple(int(v) for v in np.median(region, axis=0)) if len(region) else '#F2A7A0'
    return {
        'nom': name, 'type': 'organe', 'echelle': 1.0,
        'couches': [{'id': 'corps', 'images': {'defaut': png.name}, 'pivot': [w // 2, h]}],
        'visage': {'couche': 'corps', 'yeux': [int(cx), int(cy - r * .35)], 'rayon_oeil': round(r), 'ecart': 1.95,
                   'bouche': [int(cx), int(cy + r * 1.35)], 'largeur_bouche': round(r * 1.5), 'peau': skin,
                   'paupiere': .2, 'pupille': .8, 'forme_oeil': 1.2},
        'mouvement': {'souplesse': 1.0},
        'poses': {'defaut': {}},
    }


def auto_setup_human(png: Path, name: str) -> dict:
    """Personnage humain d'une seule image (bras dessinés, visage vierge) : repère le visage (tache de peau du haut),
    coupe la tête au cou pour qu'elle penche, place yeux et bouche. Seul le visage est animé."""
    from scipy import ndimage
    img = Image.open(png).convert('RGBA')
    a = np.array(img).astype(int)
    h, w = a.shape[:2]
    top = a[:int(h * .3)]
    ys, xs = np.nonzero(top[:, :, 3] > 200)
    hx = int(np.median(xs))
    # couleur de peau : la plus fréquente parmi les tons chair du haut du personnage
    px = top[top[:, :, 3] > 200][:, :3]
    chair = px[(px[:, 0] > px[:, 2] + 25) & (px[:, 0] > 150) & (px.max(axis=1) - px.min(axis=1) > 25)]
    col = np.median(chair, axis=0) if len(chair) else px.mean(axis=0)
    skin = (np.abs(a[:, :, :3] - col).max(axis=2) < 30) & (a[:, :, 3] > 200)
    skin[int(h * .3):] = False
    lab, n = ndimage.label(skin)
    i = int(np.argmax(ndimage.sum(skin, lab, range(1, n + 1)))) + 1
    fy, fx = np.nonzero(lab == i)
    x0, x1, y0, y1 = fx.min(), fx.max(), fy.min(), fy.max()
    fw, fh = x1 - x0, y1 - y0
    cx = int((x0 + x1) / 2)
    r = round(fw * .13)
    return {
        'nom': name, 'type': 'humain', 'echelle': 1.0,
        'couches': [{'id': 'corps', 'images': {'defaut': png.name}, 'pivot': [w // 2, h]}],
        'decoupe_tete': {'y': int(y1 + 4), 'cou': [cx, int(y1 + 2)]},
        'visage': {'couche': 'tete', 'yeux': [cx, int(y0 + fh * .48)], 'rayon_oeil': r, 'ecart': 2.25,
                   'bouche': [cx, int(y0 + fh * .78)], 'largeur_bouche': round(fw * .26),
                   'peau': '#%02X%02X%02X' % tuple(int(v) for v in col), 'forme_oeil': 1.15, 'pupille': .85},
        'mouvement': {'souplesse': .15, 'respiration': .008},
        'poses': {'defaut': {}},
    }
