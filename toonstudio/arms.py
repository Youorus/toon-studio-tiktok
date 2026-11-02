"""Bras dessinés par le moteur : épaule -> coude -> poignet, manche, main en plusieurs formes.

Pourquoi dessinés et pas générés : un bras généré change de style d'une image à l'autre et ne plie pas.
Ici le bras plie au coude, suit n'importe quel angle et garde exactement le même trait.

Angles en degrés : 0 = bras pendant le long du corps ; positif = le bras s'écarte vers l'extérieur et monte
(90 = horizontal vers l'extérieur, 180 = levé). Le coude ajoute son angle à celui de l'épaule.
"""
import math

from PIL import Image, ImageDraw

from .drawing import INK, rgb

SS = 2
HANDS = ('repos', 'ouvert', 'doigt', 'pouce', 'poing', 'salut')


def _dir(angle, side):
    a = math.radians(angle)
    return (math.sin(a) * side, math.cos(a))


def draw_arm(canvas: Image.Image, shoulder, side, spec: dict, shoulder_angle, elbow_angle, hand: str, scale=1.0, body_angle=0.0):
    """Dessine un bras sur canvas. shoulder : point d'attache (pixels du canvas) ; side : -1 bras à gauche de l'écran, +1 à droite."""
    L = spec['longueur'] * scale
    w = spec['epaisseur'] * scale
    lw = max(2.0, spec.get('trait', .09) * w)
    a1 = shoulder_angle + body_angle * side
    a2 = a1 + elbow_angle
    d1, d2 = _dir(a1, side), _dir(a2, side)
    S = shoulder
    E = (S[0] + d1[0] * L * .5, S[1] + d1[1] * L * .5)
    Wr = (E[0] + d2[0] * L * .5, E[1] + d2[1] * L * .5)
    hs = w * 1.05                                  # taille de la main
    pad = L + hs * 2
    ox, oy = S[0] - pad, S[1] - pad
    size = (int(pad * 2), int(pad * 2))
    im = Image.new('RGBA', (size[0] * SS, size[1] * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    P = lambda p: ((p[0] - ox) * SS, (p[1] - oy) * SS)
    sleeve, skin = rgb(spec.get('manche', '#F4F6FA')), rgb(spec.get('peau', '#C98B5E'))
    cuff = (E[0] + d2[0] * L * .5 * .82, E[1] + d2[1] * L * .5 * .82)
    # main (sous la manche)
    _hand(d, P(Wr), d2, side, hs * SS, hand, skin, lw * SS)
    # avant-bras nu entre le poignet de la manche et la main
    d.line([P(cuff), P(Wr)], fill=INK, width=int((w * .55 + lw * 2) * SS))
    d.line([P(cuff), P(Wr)], fill=skin, width=int(w * .55 * SS))
    # manche : trait de contour puis remplissage, articulations arrondies
    pts = [P(S), P(E), P(cuff)]
    for width, col in ((w + lw * 2, INK), (w, sleeve)):
        d.line(pts, fill=col, width=int(width * SS), joint='curve')
        for p in pts:
            r = width * SS / 2
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=col)
    # ombre douce sous le coude et bord de manche
    r = w * SS / 2
    nx, ny = -d2[1], d2[0]
    c = P(cuff)
    d.line([(c[0] + nx * r, c[1] + ny * r), (c[0] - nx * r, c[1] - ny * r)], fill=INK, width=int(lw * SS))
    small = im.resize(size, Image.LANCZOS)
    canvas.alpha_composite(small, (int(ox), int(oy)))
    return Wr


def _hand(d, c, direction, side, s, kind, skin, lw):
    """Main posée au poignet c, orientée selon direction (vecteur unitaire de l'avant-bras)."""
    ux, uy = direction                       # axe du bras
    vx, vy = -uy * side, ux * side           # axe du pouce (vers l'avant du personnage)

    def at(a, b):                            # a le long du bras, b vers le pouce
        return (c[0] + ux * a + vx * b, c[1] + uy * a + vy * b)

    def blob(a, b, r):
        x, y = at(a, b); d.ellipse((x - r, y - r, x + r, y + r), fill=skin, outline=INK, width=int(lw))

    def finger(a0, b0, a1, b1, r):
        p0, p1 = at(a0, b0), at(a1, b1)
        d.line([p0, p1], fill=INK, width=int(r * 2 + lw * 2))
        for p in (p0, p1):
            d.ellipse((p[0] - r - lw, p[1] - r - lw, p[0] + r + lw, p[1] + r + lw), fill=INK)
        d.line([p0, p1], fill=skin, width=int(r * 2))
        for p in (p0, p1):
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=skin)

    r = s * .2
    if kind in ('ouvert', 'salut'):
        blob(s * .45, 0, s * .48)
        for k in (-1.5, -.5, .5, 1.5):
            finger(s * .7, k * s * .2, s * 1.35, k * s * .34, r * .85)
        finger(s * .35, s * .42, s * .75, s * .85, r * .85)
        blob(s * .45, 0, s * .4)
    elif kind == 'doigt':
        blob(s * .42, 0, s * .45)
        finger(s * .55, s * .2, s * 1.25, s * .2, r * .85)
        finger(s * .25, s * .4, s * .5, s * .5, r * .8)
    elif kind == 'pouce':
        blob(s * .42, 0, s * .45)
        finger(s * .3, s * .38, s * .1, s * .95, r * .9)
    elif kind == 'poing':
        blob(s * .4, 0, s * .45)
        finger(s * .3, s * .38, s * .55, s * .42, r * .8)
    else:                                    # repos : main en moufle, pouce le long
        blob(s * .5, 0, s * .42)
        finger(s * .25, s * .35, s * .65, s * .42, r * .8)
