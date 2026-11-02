"""Visage procédural, dessiné par-dessus n'importe quelle couche (organe, objet ou tête vierge).

Grands yeux blancs, pupilles qui suivent le regard, paupières de la couleur de la peau qui donnent l'émotion,
sourcils fins, bouches pour la parole (visèmes) et pour les expressions. Tout est dessiné en 3x puis réduit,
pour un trait net quelle que soit la taille.
"""
import math
from dataclasses import dataclass, field
from functools import lru_cache

from PIL import Image, ImageChops, ImageDraw

from .drawing import INK, WHITE, rgb, shade

CREAM = (255, 249, 237, 255)     # blanc des yeux : crème de la palette (pas de blanc pur)

SS = 3

# Émotion -> paupière haute (0 ouverte, 1 fermée), inclinaison (+ = coin intérieur bas : colère), paupière basse,
# sourcils (hauteur, inclinaison : + = intérieur levé, inquiet), taille des pupilles, bouche au repos.
EMOTIONS = {
    'neutre':    dict(lid=.12, tilt=0, low=0, brow=(0, 0), pupil=1.0, mouth='repos'),
    'content':   dict(lid=.05, tilt=0, low=.28, brow=(.15, 0), pupil=1.0, mouth='sourire'),
    'rire':      dict(lid=1.0, tilt=0, low=0, brow=(.25, 0), pupil=1.0, mouth='rire', arc=True),
    'choque':    dict(lid=0, tilt=0, low=0, brow=(.45, .1), pupil=.6, mouth='O'),
    'triste':    dict(lid=.32, tilt=-.35, low=0, brow=(.1, .6), pupil=1.1, mouth='triste'),
    'inquiet':   dict(lid=.12, tilt=-.25, low=0, brow=(.2, .55), pupil=.85, mouth='gene'),
    'fache':     dict(lid=.38, tilt=.55, low=.1, brow=(-.15, -.7), pupil=.9, mouth='grimace'),
    'fatigue':   dict(lid=.58, tilt=0, low=.12, brow=(-.05, .1), pupil=1.0, mouth='ferme'),
    'gene':      dict(lid=.22, tilt=-.15, low=0, brow=(.1, .4), pupil=.9, mouth='gene', blush=True),
    'degoute':   dict(lid=.42, tilt=.2, low=.22, brow=(-.1, -.3), pupil=.9, mouth='beurk'),
    'douleur':   dict(lid=1.0, tilt=0, low=0, brow=(-.1, .5), pupil=1.0, mouth='cri', squeeze=True),
    'malicieux': dict(lid=.35, tilt=.15, low=.1, brow=(.1, -.2), pupil=1.0, mouth='coin'),
    'amoureux':  dict(lid=.05, tilt=0, low=.2, brow=(.2, .2), pupil=1.35, mouth='sourire', blush=True),
}
# Visèmes de parole (lettres -> forme de bouche)
VISEMES = ('A', 'E', 'O', 'M', 'F', 'repos')


@dataclass
class FaceSpec:
    """Placement du visage dans l'image de sa couche (pixels de l'image source)."""
    eyes: tuple                 # centre entre les deux yeux (x, y)
    eye_r: float                # rayon d'un œil
    gap: float = 1.9            # écart centre-à-centre des yeux, en rayons (2 = yeux qui se touchent)
    mouth: tuple = None         # centre de la bouche ; par défaut sous les yeux
    mouth_w: float = None       # largeur de la bouche ; par défaut 1.6 rayon
    skin: str = '#F2A7A0'       # couleur des paupières (celle de la surface du visage)
    line: float = .1            # épaisseur du trait, en rayon d'œil (encre du rendu cellulo)
    eye_shape: float = 1.12     # hauteur / largeur de l'œil (1 = rond)
    brows: bool = True
    lid_base: float = 0.0       # paupière toujours un peu tombante (regard « blasé » des organes) : 0 à .4
    pupil: float = 1.0          # taille des pupilles (petites = .7)
    glasses: str | None = None  # couleur de lunettes rondes dessinées autour des yeux (signe distinctif)
    lashes: bool = False        # cils
    extra: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.mouth is None:
            self.mouth = (self.eyes[0], self.eyes[1] + self.eye_r * 1.75)
        if self.mouth_w is None:
            self.mouth_w = self.eye_r * 1.6


def _eye(r, emo, gaze, blink, skin, lw, shape, side, lid_base=0.0, pupil=1.0, lashes=False):
    """Un œil sur sa propre petite toile (masquée par le contour de l'œil)."""
    e = dict(EMOTIONS[emo])
    if not e.get('squeeze') and not e.get('arc'):
        e['lid'] = min(.9, e['lid'] + lid_base * (1 - e['lid'])) if emo != 'choque' else e['lid']
    w, h = r * 2, r * 2 * shape
    pad = r * .9
    W_, H_ = int(w + pad * 2), int(h + pad * 2)
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    box = (pad, pad, pad + w, pad + h)
    cx, cy = pad + w / 2, pad + h / 2
    if e.get('squeeze'):                                  # yeux plissés ><
        k = 1 if side < 0 else -1
        d.line([(cx - r * .55 * k, cy - r * .45), (cx + r * .45 * k, cy), (cx - r * .55 * k, cy + r * .45)], fill=INK, width=int(lw * 1.4), joint='curve')
        return im
    if blink or e.get('arc'):                             # œil fermé : un arc
        up = e.get('arc')
        d.arc((cx - r * .8, cy - r * (.2 if up else .5), cx + r * .8, cy + r * (.8 if up else .5)), 200 if up else 20, 340 if up else 160, fill=INK, width=int(lw * 1.3))
        return im
    d.ellipse(box, fill=CREAM)
    # pupille + reflet
    pr = r * .34 * e['pupil'] * pupil
    px, py = cx + gaze[0] * (r - pr) * .62, cy + gaze[1] * (h / 2 - pr) * .55
    d.ellipse((px - pr, py - pr, px + pr, py + pr), fill=INK)
    hr = pr * .3
    d.ellipse((px - pr * .38 - hr, py - pr * .42 - hr, px - pr * .38 + hr, py - pr * .42 + hr), fill=WHITE)
    hr2 = pr * .14
    d.ellipse((px + pr * .3 - hr2, py + pr * .3 - hr2, px + pr * .3 + hr2, py + pr * .3 + hr2), fill=WHITE)
    # paupières (couleur peau) : haute inclinée selon l'émotion, basse pour le sourire des yeux
    lid = Image.new('RGBA', im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lid)
    sk = rgb(skin)
    if e['lid'] > 0:
        y = pad + h * e['lid']
        t = e['tilt'] * r * .9 * (1 if side < 0 else -1)
        poly = [(0, 0), (W_, 0), (W_, y - t), (0, y + t)]
        ld.polygon(poly, fill=sk)
        ld.line([(0, y + t), (W_, y - t)], fill=INK, width=int(lw))
    if e['low'] > 0:
        y = pad + h * (1 - e['low'])
        ld.ellipse((pad - r * .3, y - r * .1, pad + w + r * .3, y + r * 1.4), fill=sk)
        ld.arc((pad - r * .3, y - r * .1, pad + w + r * .3, y + r * 1.4), 200, 340, fill=INK, width=int(lw * .8))
    mask = Image.new('L', im.size, 0); ImageDraw.Draw(mask).ellipse(box, fill=255)
    lid.putalpha(ImageChops.multiply(lid.getchannel('A'), mask))
    im.alpha_composite(lid)
    d = ImageDraw.Draw(im)
    d.ellipse(box, outline=INK, width=int(lw))
    if lashes:
        k = -1 if side < 0 else 1
        for i, ang in enumerate((-150, -130, -110) if k < 0 else (-30, -50, -70)):
            a = math.radians(ang)
            x0, y0 = cx + r * math.cos(a), cy + h / 2 * math.sin(a)
            d.line([(x0, y0), (x0 + r * .35 * math.cos(a), y0 + r * .35 * math.sin(a))], fill=INK, width=int(lw * .9))
    return im


def _mouth(d, cx, cy, w, shape, lw, skin):
    dark, tongue, teeth = (92, 24, 40, 255), (236, 110, 128, 255), WHITE
    if shape in ('repos', 'M', 'ferme'):
        d.arc((cx - w * .3, cy - w * .2, cx + w * .3, cy + w * .12), 25, 155, fill=INK, width=int(lw))
    elif shape == 'sourire':
        d.arc((cx - w * .45, cy - w * .35, cx + w * .45, cy + w * .2), 20, 160, fill=INK, width=int(lw))
    elif shape == 'coin':
        d.arc((cx - w * .4, cy - w * .3, cx + w * .45, cy + w * .2), 10, 120, fill=INK, width=int(lw))
    elif shape == 'triste':
        d.arc((cx - w * .32, cy, cx + w * .32, cy + w * .38), 200, 340, fill=INK, width=int(lw))
    elif shape == 'gene':
        pts = [(cx - w * .32 + i * w * .64 / 8, cy + (w * .05 if i % 2 else -w * .05)) for i in range(9)]
        d.line(pts, fill=INK, width=int(lw), joint='curve')
    elif shape == 'grimace':
        d.rounded_rectangle((cx - w * .38, cy - w * .1, cx + w * .38, cy + w * .14), radius=w * .08, fill=teeth, outline=INK, width=int(lw))
        for i in range(1, 5):
            x = cx - w * .38 + i * w * .76 / 5
            d.line([(x, cy - w * .1), (x, cy + w * .14)], fill=INK, width=max(1, int(lw * .5)))
        d.line([(cx - w * .38, cy + w * .02), (cx + w * .38, cy + w * .02)], fill=INK, width=max(1, int(lw * .5)))
    elif shape == 'O':
        d.ellipse((cx - w * .17, cy - w * .14, cx + w * .17, cy + w * .26), fill=dark, outline=INK, width=int(lw))
        d.chord((cx - w * .1, cy + w * .08, cx + w * .1, cy + w * .24), 180, 360, fill=tongue)
    elif shape in ('A', 'rire', 'cri', 'E', 'beurk'):
        oh = {'A': .42, 'rire': .45, 'cri': .55, 'E': .24, 'beurk': .3}[shape]
        ww = {'A': .4, 'rire': .48, 'cri': .36, 'E': .44, 'beurk': .4}[shape]
        top = cy - w * .05                                         # ligne des lèvres du haut
        box = (cx - w * ww, top - w * oh, cx + w * ww, top + w * oh)
        d.chord(box, 0, 180, fill=dark)
        d.chord((cx - w * ww * .55, top + w * oh * .45, cx + w * ww * .55, top + w * oh * 1.25), 180, 360, fill=tongue)
        if shape != 'cri':
            d.rectangle((cx - w * ww * .72, top, cx + w * ww * .72, top + w * .09), fill=teeth)
        if shape == 'beurk':                                    # langue qui pend
            d.rounded_rectangle((cx - w * .12, top + w * .1, cx + w * .12, top + w * .55), radius=w * .1, fill=tongue, outline=INK, width=int(lw * .8))
        d.chord(box, 0, 180, outline=INK, width=int(lw))
        d.line([(box[0], top), (box[2], top)], fill=INK, width=int(lw))
    elif shape == 'F':
        d.chord((cx - w * .3, cy - w * .12, cx + w * .3, cy + w * .2), 0, 180, fill=dark, outline=INK, width=int(lw))
        d.rectangle((cx - w * .2, cy - w * .12, cx + w * .2, cy - w * .02), fill=teeth)


@lru_cache(maxsize=4096)
def face_overlay(spec_key, emo, gaze, blink, mouth, size):
    """Calque du visage (taille de l'image de la couche), mis en cache par état."""
    spec = _SPECS[spec_key]
    W_, H_ = size
    im = Image.new('RGBA', (W_ * SS, H_ * SS), (0, 0, 0, 0))
    r = spec.eye_r * SS
    lw = max(2, spec.line * spec.eye_r * SS)
    ex, ey = spec.eyes[0] * SS, spec.eyes[1] * SS
    e = EMOTIONS[emo]
    d = ImageDraw.Draw(im)
    if e.get('blush'):
        for s in (-1, 1):
            bx, by = ex + s * r * spec.gap * .85, ey + r * 1.1
            d.ellipse((bx - r * .55, by - r * .25, bx + r * .55, by + r * .25), fill=(255, 110, 130, 110))
    for s in (-1, 1):
        eye = _eye(r, emo, gaze, blink, spec.skin, lw, spec.eye_shape, s, spec.lid_base, spec.pupil, spec.lashes)
        x = ex + s * r * spec.gap / 2
        im.alpha_composite(eye, (int(x - eye.width / 2), int(ey - eye.height / 2)))
        if spec.glasses:
            gr = r * 1.18
            d.ellipse((x - gr, ey - gr * spec.eye_shape * .95, x + gr, ey + gr * spec.eye_shape * .95), outline=rgb(spec.glasses), width=int(lw * 1.6))
            if s == 1:
                d.line([(ex - r * spec.gap / 2 + gr, ey), (x - gr, ey)], fill=rgb(spec.glasses), width=int(lw * 1.6))
        if spec.brows:
            bh, bt = e['brow']
            by = ey - r * spec.eye_shape - r * (.32 + bh * .4)
            inner = s * -1                     # côté intérieur
            x0, x1 = x - r * .7, x + r * .7
            y_in, y_out = by - bt * r * .25, by + bt * r * .25
            pts = [(x0, y_in if inner < 0 else y_out), (x1, y_out if inner < 0 else y_in)]
            d.line(pts, fill=INK, width=int(lw * 1.25))
    shape = mouth or e['mouth']
    mx, my = spec.mouth[0] * SS, spec.mouth[1] * SS
    _mouth(d, mx, my, spec.mouth_w * SS, shape, lw * 1.1, spec.skin)
    return im.resize((W_, H_), Image.LANCZOS)


_SPECS: dict = {}


def register(name: str, spec: FaceSpec):
    _SPECS[name] = spec
    return name


def visemes_for(text: str, t0: float, t1: float):
    """Suite (temps, visème) répartie sur la durée de la réplique, sans voix : une forme par lettre parlée."""
    table = [('aàâ', 'A'), ('eéèêëiîïy', 'E'), ('oôuùûœ', 'O'), ('mbp', 'M'), ('fv', 'F')]
    letters = [c for c in text.lower() if c.isalpha()]
    if not letters:
        return []
    step = (t1 - t0) / len(letters)
    out, last = [], None
    for i, c in enumerate(letters):
        v = next((v for chars, v in table if c in chars), 'E' if i % 3 else 'repos')
        if v != last:
            out.append((t0 + i * step, v)); last = v
    return out
