"""Membres « tuyau » à l'ancienne (rubber hose) pour les organes et objets : bras noirs souples à gants blancs,
jambes à chaussures, cycle de marche. Dessinés par le moteur, donc gratuits et identiques d'un épisode à l'autre.

Angles en degrés. Bras : 0 = pend le long du corps, positif = s'écarte et monte (90 horizontal, 170 levé).
Jambe : 0 = verticale, positif = vers l'avant (sens de la marche).
"""
import math

from PIL import Image, ImageDraw

from .drawing import INK, rgb

SS = 2
GESTES = {
    # geste -> (épaule gauche, coude gauche, main gauche, épaule droite, coude droite, main droite)   (gauche = côté -1)
    'repos':    (10, 8, 'repos', 10, 8, 'repos'),
    'stop':     (12, 5, 'repos', 95, 70, 'ouvert'),          # main droite levée paume en avant
    'salut':    (12, 5, 'repos', 150, 30, 'ouvert'),
    'doigt':    (12, 5, 'repos', 100, 10, 'doigt'),          # pointe devant lui
    'hausse':   (60, 100, 'ouvert', 60, 100, 'ouvert'),     # haussement d'épaules, paumes en l'air
    'hanches':  (45, -95, 'poing', 45, -95, 'poing'),
    'bras_croises': (70, -120, 'poing', 70, -120, 'poing'),
    'joie':     (160, 15, 'ouvert', 160, 15, 'ouvert'),
    'tete':     (20, 150, 'poing', 20, 150, 'poing'),        # mains sur la tête
    'chut':     (12, 5, 'repos', 110, 120, 'doigt'),         # doigt devant la bouche
    'siffle':   (12, 5, 'repos', 115, 125, 'poing'),         # main à la bouche
    'pointe_bas': (12, 5, 'repos', 40, 10, 'doigt'),
}


def _dir(angle, side):
    a = math.radians(angle)
    return (math.sin(a) * side, math.cos(a))


def _P(ox, oy):
    return lambda p: ((p[0] - ox) * SS, (p[1] - oy) * SS)


def _glove(d, c, direction, side, s, kind, lw, glove=(255, 249, 237, 255)):
    """Gant blanc à 4 doigts, dans l'axe de l'avant-bras (direction unitaire)."""
    ux, uy = direction
    vx, vy = -uy * side, ux * side            # axe du pouce (vers l'avant du personnage)
    at = lambda a, b: (c[0] + ux * a + vx * b, c[1] + uy * a + vy * b)

    def capsule(p0, p1, r, fill):
        d.line([p0, p1], fill=INK, width=int(r * 2 + lw * 2))
        for p in (p0, p1):
            d.ellipse((p[0] - r - lw, p[1] - r - lw, p[0] + r + lw, p[1] + r + lw), fill=INK)
        d.line([p0, p1], fill=fill, width=int(r * 2))
        for p in (p0, p1):
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=fill)

    # poignet (manchette) + paume
    capsule(at(-s * .1, 0), at(s * .25, 0), s * .36, glove)
    palm = at(s * .55, 0)
    d.ellipse((palm[0] - s * .5 - lw, palm[1] - s * .5 - lw, palm[0] + s * .5 + lw, palm[1] + s * .5 + lw), fill=INK)
    d.ellipse((palm[0] - s * .5, palm[1] - s * .5, palm[0] + s * .5, palm[1] + s * .5), fill=glove)
    r = s * .19
    if kind == 'ouvert':
        for k in (-1.5, -.5, .5, 1.5):
            capsule(at(s * .75, k * s * .22), at(s * 1.35, k * s * .36), r, glove)
        capsule(at(s * .4, s * .45), at(s * .7, s * .9), r, glove)
    elif kind == 'doigt':
        capsule(at(s * .8, s * .1), at(s * 1.45, s * .1), r, glove)
        capsule(at(s * .4, s * .45), at(s * .62, s * .8), r * .9, glove)
        for k in (-.35, -.05):
            capsule(at(s * .75, k * s), at(s * .95, k * s - s * .05), r * .9, glove)
    elif kind == 'poing':
        for k in (-.35, -.05, .25):
            capsule(at(s * .75, k * s), at(s * .98, k * s), r * .9, glove)
        capsule(at(s * .4, s * .45), at(s * .75, s * .5), r * .9, glove)
    else:                                       # repos : moufle, pouce le long
        capsule(at(s * .75, -s * .1), at(s * 1.1, -s * .05), r * 1.1, glove)
        capsule(at(s * .4, s * .4), at(s * .7, s * .55), r * .85, glove)
    d.ellipse((palm[0] - s * .5, palm[1] - s * .5, palm[0] + s * .5, palm[1] + s * .5), fill=glove)   # la paume par-dessus les bases des doigts


def draw_noodle_arm(canvas, shoulder, side, spec, a_shoulder, a_elbow, hand, scale=1.0, body_angle=0.0, swing=0.0):
    """Bras tuyau : épaule -> coude -> poignet, courbe souple ; gant au bout."""
    L = spec.get('longueur', 120) * scale
    w = spec.get('epaisseur', 16) * scale
    lw = max(1.5, w * .22)
    col = rgb(spec.get('couleur', '#181313'))
    glove = rgb(spec.get('gant', '#FFF9ED'))
    a1 = a_shoulder + body_angle * side + swing
    a2 = a1 + a_elbow
    d1, d2 = _dir(a1, side), _dir(a2, side)
    S = shoulder
    E = (S[0] + d1[0] * L * .5, S[1] + d1[1] * L * .5)
    Wr = (E[0] + d2[0] * L * .5, E[1] + d2[1] * L * .5)
    hs = w * 1.6
    pad = L + hs * 3
    ox, oy = S[0] - pad, S[1] - pad
    size = (int(pad * 2), int(pad * 2))
    im = Image.new('RGBA', (size[0] * SS, size[1] * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    P = _P(ox, oy)
    # courbe souple : point de contrôle légèrement écarté du coude (bras « noodle »)
    mid = (E[0] + (d2[0] - d1[0]) * L * .08, E[1] + (d2[1] - d1[1]) * L * .08)
    pts = [P(S), P(mid), P(Wr)]
    for width, c in ((w + lw * 2, INK), (w, col)):
        d.line(pts, fill=c, width=int(width * SS), joint='curve')
        for p in pts:
            r = width * SS / 2
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=c)
    _glove(d, P(Wr), d2, side, hs * SS, hand, lw * SS, glove)
    canvas.alpha_composite(im.resize(size, Image.LANCZOS), (int(ox), int(oy)))


def draw_leg(canvas, hip, side, spec, a_hip, a_knee, scale=1.0, lift=0.0):
    """Jambe tuyau + chaussure. side = +1 jambe « avant » (vers la droite de l'écran), le pied pointe vers +x."""
    L = spec.get('longueur', 110) * scale
    w = spec.get('epaisseur', 18) * scale
    lw = max(1.5, w * .2)
    col = rgb(spec.get('couleur', '#181313'))
    shoe = rgb(spec.get('chaussure', '#181313'))
    a1 = math.radians(a_hip)
    H = hip
    K = (H[0] + math.sin(a1) * L * .5, H[1] + math.cos(a1) * L * .5)
    a2 = a1 + math.radians(a_knee)
    F = (K[0] + math.sin(a2) * L * .5, K[1] + math.cos(a2) * L * .5 - lift)
    pad = L + w * 4
    ox, oy = H[0] - pad, H[1] - pad
    size = (int(pad * 2), int(pad * 2))
    im = Image.new('RGBA', (size[0] * SS, size[1] * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    P = _P(ox, oy)
    pts = [P(H), P(K), P(F)]
    for width, c in ((w + lw * 2, INK), (w, col)):
        d.line(pts, fill=c, width=int(width * SS), joint='curve')
        for p in pts:
            r = width * SS / 2
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=c)
    # chaussure : ovale allongé vers l'avant, bout arrondi
    sx, sy = P(F)
    sl, sh = w * 2.6 * SS, w * 1.25 * SS
    fwd = spec.get('sens', 1)
    box = (sx - sl * (.35 if fwd > 0 else .65), sy - sh * .55, sx + sl * (.65 if fwd > 0 else .35), sy + sh * .45)
    d.ellipse((box[0] - lw * SS, box[1] - lw * SS, box[2] + lw * SS, box[3] + lw * SS), fill=INK)
    d.ellipse(box, fill=shoe)
    # reflet
    d.ellipse((box[0] + sl * .15, box[1] + sh * .15, box[0] + sl * .45, box[1] + sh * .4), fill=(255, 255, 255, 110))
    canvas.alpha_composite(im.resize(size, Image.LANCZOS), (int(ox), int(oy)))


def walk_cycle(t, speed=1.0):
    """Angles de marche à l'instant t : (hanche av, genou av, hanche ar, genou ar, rebond du corps, balancement des bras)."""
    w = 2 * math.pi * 2.2 * speed            # ~2,2 pas par seconde
    ph = t * w
    swing = 28 * math.sin(ph)
    bend_a = max(0, -40 * math.sin(ph - .9))  # le genou plie quand la jambe revient
    bend_b = max(0, -40 * math.sin(ph + math.pi - .9))
    bob = abs(math.sin(ph)) * 6
    return swing, bend_a, -swing, bend_b, bob, 22 * math.sin(ph)
