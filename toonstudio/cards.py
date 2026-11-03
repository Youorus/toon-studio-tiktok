"""Cartes de motion design : elles apparaissent au-dessus de la scène pour appuyer une idée.

Chaque type est une fonction draw(args, p, duree, palette) -> image RGBA de CW x CH, où p est le temps (s)
depuis l'apparition. L'entrée (rebond) est gérée par la scène ; ici on anime le contenu.
Types : choc, chiffre, liste, alerte, image, bouton, vote. Ajouter un type = ajouter une fonction à TYPES.
"""
import math

from PIL import Image, ImageDraw, ImageFilter

from .drawing import INK, WHITE, back_out, ease_out, font, rgb, shade

CW, CH, SS = 960, 640, 2
GREEN, RED, ORANGE = (52, 168, 96, 255), (230, 64, 70, 255), (242, 140, 40, 255)


def _canvas():
    im = Image.new('RGBA', (CW * SS, CH * SS), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im), CW * SS / 2, CH * SS / 2


def _panel(im, w, h, fill=WHITE, radius=46):
    x0, y0 = (CW * SS - w * SS) / 2, (CH * SS - h * SS) / 2
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 16 * SS, x0 + w * SS, y0 + h * SS + 16 * SS), radius=radius * SS, fill=(0, 0, 0, 80))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12 * SS)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y0, x0 + w * SS, y0 + h * SS), radius=radius * SS, fill=rgb(fill), outline=INK, width=6 * SS)
    return d


def _t(d, xy, s, f, fill, stroke=0, anchor='mm'):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=INK)


def _fit(d, text, name, size, maxw):
    while size > 20 and d.textlength(text, font=font(name, size)) > maxw:
        size -= 4
    return font(name, size)


def _icon(d, kind, cx, cy, s, p=1.0):
    col = {'ok': GREEN, 'non': RED, 'attention': ORANGE}.get(kind, GREEN)
    d.ellipse((cx - s, cy - s, cx + s, cy + s), fill=col)
    lw = int(s * .22)
    if kind == 'ok':
        a, b, c = (cx - s * .45, cy), (cx - s * .1, cy + s * .38), (cx + s * .5, cy - s * .35)
        q = min(1, p * 2); d.line([a, (a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q)], fill=WHITE, width=lw)
        if p > .5:
            q = (p - .5) * 2; d.line([b, (b[0] + (c[0] - b[0]) * q, b[1] + (c[1] - b[1]) * q)], fill=WHITE, width=lw)
    elif kind == 'non':
        for u, v in (((-.4, -.4), (.4, .4)), ((-.4, .4), (.4, -.4))):
            d.line([(cx + u[0] * s, cy + u[1] * s), (cx + v[0] * s, cy + v[1] * s)], fill=WHITE, width=lw)
    else:
        _t(d, (cx, cy + s * .05), '!', font('LuckiestGuy', int(s * 1.4)), WHITE)


def choc(a, p, dur, pal):
    """Onomatopée ou mot choc dans une étoile de BD (« HIC ! », « BEURK »)."""
    im, d, cx, cy = _canvas()
    n, R, r = 14, 300 * SS, 215 * SS
    spin = math.radians(6 * math.sin(p * 9))
    pts = [(cx + (R if i % 2 == 0 else r) * math.cos(i * math.pi / n + spin), cy + (R if i % 2 == 0 else r) * .72 * math.sin(i * math.pi / n + spin)) for i in range(2 * n)]
    d.polygon(pts, fill=rgb(a.get('fond', pal['accent'])))
    d.line(pts + [pts[0]], fill=INK, width=7 * SS, joint='curve')
    f = _fit(d, a['texte'], 'LuckiestGuy', 150 * SS, 440 * SS)
    _t(d, (cx, cy), a['texte'], f, WHITE, 6 * SS)
    return im


def chiffre(a, p, dur, pal):
    """Grand nombre (qui compte s'il est numérique) + légende."""
    im, d, cx, cy = _canvas()
    d = _panel(im, 760, 380)
    val = a['valeur']
    if isinstance(val, (int, float)):
        v = val * ease_out(p / .9)
        txt = (f'{v:,.0f}' if val >= 100 else f'{v:.0f}').replace(',', ' ') + a.get('unite', '')
    else:
        txt = str(val)
    _t(d, (cx, cy - 40 * SS), txt, _fit(d, txt, 'LuckiestGuy', 170 * SS, 680 * SS), rgb(a.get('couleur', pal['accent'])), 4 * SS)
    _t(d, (cx, cy + 115 * SS), a.get('legende', ''), _fit(d, a.get('legende', ''), 'Fredoka', 48 * SS, 680 * SS), INK)
    return im


def liste(a, p, dur, pal):
    """Lignes qui arrivent une à une : [texte, icône ok|non|attention]."""
    im, d, cx, cy = _canvas()
    rows = a['lignes']
    h = 110 + 120 * len(rows) + (70 if a.get('titre') else 0)
    d = _panel(im, 860, h)
    y0 = cy - (h * SS) / 2 + (95 if a.get('titre') else 40) * SS + 60 * SS
    if a.get('titre'):
        _t(d, (cx, cy - (h * SS) / 2 + 60 * SS), a['titre'], font('LuckiestGuy', 56 * SS), INK)
    for i, row in enumerate(rows):
        text, icon = (row, 'ok') if isinstance(row, str) else row
        q = ease_out((p - .15 - i * .35) / .3)
        if q <= 0:
            continue
        y = y0 + i * 120 * SS
        off = (1 - q) * 200 * SS
        _icon(d, icon, cx - 350 * SS + off, y, 40 * SS, q)
        d.text((cx - 285 * SS + off, y), text, font=_fit(d, text, 'Fredoka', 50 * SS, 640 * SS), fill=INK, anchor='lm')
    return im


def alerte(a, p, dur, pal):
    """Encadré d'avertissement (« Consulte si… »)."""
    im, d, cx, cy = _canvas()
    d = _panel(im, 820, 330, fill=(255, 244, 214))
    pulse = 1 + .08 * max(0, math.sin(p * 6))
    _icon(d, 'attention', cx - 300 * SS, cy, 62 * SS * pulse)
    lines = a['texte'].split('\n')
    for i, line in enumerate(lines):
        d.text((cx - 210 * SS, cy + (i - (len(lines) - 1) / 2) * 70 * SS), line, font=_fit(d, line, 'Fredoka', 54 * SS, 560 * SS), fill=INK, anchor='lm')
    return im


def image(a, p, dur, pal):
    """Image (schéma, objet) dans un cadre, avec légende."""
    from .config import ROOT
    im, d, cx, cy = _canvas()
    d = _panel(im, 700, 560)
    pic = Image.open(ROOT / a['fichier']).convert('RGBA')
    pic.thumbnail((600 * SS, 400 * SS), Image.LANCZOS)
    im.alpha_composite(pic, (int(cx - pic.width / 2), int(cy - 40 * SS - pic.height / 2)))
    d = ImageDraw.Draw(im)
    _t(d, (cx, cy + 225 * SS), a.get('legende', ''), _fit(d, a.get('legende', ''), 'Fredoka', 46 * SS, 620 * SS), INK)
    return im


def bouton(a, p, dur, pal):
    """Bouton d'appel à l'action qui pulse (« Envoie à un pote »)."""
    im, d, cx, cy = _canvas()
    k = 1 + .05 * math.sin(p * 2 * math.pi * 1.5)
    w, h = a.get('largeur', 800) * SS * k, 170 * SS * k
    col = rgb(a.get('couleur', pal['accent']))
    d.rounded_rectangle((cx - w / 2, cy - h / 2 + 14 * SS, cx + w / 2, cy + h / 2 + 14 * SS), radius=int(h / 2), fill=shade(col, .6))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=int(h / 2), fill=col, outline=INK, width=6 * SS)
    _t(d, (cx, cy), a['texte'], _fit(d, a['texte'], 'LuckiestGuy', 64 * SS, w - 120 * SS), WHITE, 3 * SS)
    return im


def vote(a, p, dur, pal):
    """Deux boutons pour faire commenter (« Déjà vécu ? OUI / NON »)."""
    im, d, cx, cy = _canvas()
    _t(d, (cx, cy - 190 * SS), a.get('question', 'Ton avis ?'), font('LuckiestGuy', 80 * SS), WHITE, 6 * SS)
    for i, (lab, col) in enumerate(((a.get('oui', 'OUI'), GREEN), (a.get('non', 'NON'), RED))):
        q = back_out((p - i * .25) / .35)
        if q <= 0:
            continue
        bx = cx + (-220 if i == 0 else 220) * SS
        w, h = 390 * SS * q, 180 * SS * q
        d.rounded_rectangle((bx - w / 2, cy - h / 2 + 14 * SS, bx + w / 2, cy + h / 2 + 14 * SS), radius=int(40 * SS * q), fill=shade(col, .6))
        d.rounded_rectangle((bx - w / 2, cy - h / 2, bx + w / 2, cy + h / 2), radius=int(40 * SS * q), fill=col, outline=INK, width=6 * SS)
        if q > .5:
            _t(d, (bx, cy), lab, _fit(d, lab, 'LuckiestGuy', int(64 * SS * q), w - 40 * SS), WHITE, 2 * SS)
    return im


TYPES = {'choc': choc, 'chiffre': chiffre, 'liste': liste, 'alerte': alerte, 'image': image, 'bouton': bouton, 'vote': vote}


def draw(card: dict, p: float, dur: float, palette: dict) -> Image.Image:
    im = TYPES[card['type']](card, p, dur, palette)
    return im.resize((CW, CH), Image.LANCZOS)


def organ_badge(organ: str) -> Image.Image:
    """Cartouche de lieu anatomique pour les plans à l’intérieur du corps."""
    label = organ.upper()
    f = font('LuckiestGuy', 38 * SS)
    w, h = math.ceil(f.getlength(label) / SS) + 96, 74
    im = Image.new('RGBA', (w * SS, h * SS))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((2, 2, w * SS - 3, h * SS - 4), radius=29 * SS,
                        fill='#6D383B', outline='#FFF9ED', width=3 * SS)
    d.ellipse((12 * SS, 12 * SS, 60 * SS, 60 * SS), fill='#F3C5C5')
    if organ.casefold() == 'estomac':
        points = [(34,20),(33,29),(37,32),(42,28),(48,30),(51,35),(50,42),
                  (45,48),(40,50),(32,48),(28,49),(26,54),(22,53),(23,47),
                  (26,43),(35,42),(38,37),(34,37),(29,33),(29,25),(30,19)]
        d.polygon([(x * SS, y * SS) for x, y in points], fill='#B65F63', outline='#6D383B', width=2 * SS)
    elif organ.casefold() == 'peau':
        for y, color in ((24, '#B65F63'), (34, '#8F474B'), (44, '#B65F63')):
            d.line([(x * SS, (y + dy) * SS) for x, dy in ((21, 2), (29, 0), (39, 2), (51, 0))],
                   fill=color, width=4 * SS, joint='curve')
    else:
        d.ellipse((24 * SS, 24 * SS, 48 * SS, 48 * SS), outline='#8F474B', width=3 * SS)
        d.ellipse((32 * SS, 32 * SS, 40 * SS, 40 * SS), fill='#8F474B')
    _t(d, (73 * SS, 38 * SS), label, f, '#FFF9ED', anchor='lm')
    return im.resize((w, h), Image.Resampling.LANCZOS)


def actor_badge(text: str, color: str, dot: str) -> Image.Image:
    """Mini-badge d’identification, avec un point coloré en plus du nom."""
    rows = text.upper().splitlines()
    f = font('Fredoka', 41 * SS)
    f.set_variation_by_name('SemiBold')
    w = math.ceil(max(f.getlength(row) for row in rows) / SS) + 64
    h = 64 + 43 * (len(rows) - 1)
    im = Image.new('RGBA', (w * SS, h * SS))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((2, 2, w * SS - 3, h * SS - 3), radius=24 * SS,
                        fill=color, outline='#FFF9ED', width=3 * SS)
    middle = h * SS / 2
    d.ellipse((14 * SS, middle - 10 * SS, 34 * SS, middle + 10 * SS), fill=dot)
    for i, row in enumerate(rows):
        d.text((45 * SS, middle + (i - (len(rows) - 1) / 2) * 43 * SS),
               row, font=f, fill='#FFF9ED', anchor='lm')
    return im.resize((w, h), Image.Resampling.LANCZOS)
