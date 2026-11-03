"""Petits outils de dessin partagés : courbes d'animation, polices, images, couleurs."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageFont

from .config import FONTS, W, H

INK = (24, 19, 19, 255)          # trait : l'encre de la palette (#181313)
WHITE = (255, 255, 255, 255)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x); return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def back_out(x, s=1.70158):
    x = clamp(x); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def elastic_out(x):
    x = clamp(x)
    if x in (0, 1):
        return x
    return 2 ** (-10 * x) * math.sin((x * 10 - .75) * (2 * math.pi) / 3) + 1


@lru_cache(maxsize=64)
def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / f'{name}.ttf'), size)


def rgb(c):
    """'#RRGGBB' ou (r, g, b) -> (r, g, b, 255)."""
    if isinstance(c, str):
        c = c.lstrip('#'); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    return tuple(c[:3]) + ((c[3],) if len(c) > 3 else (255,))


def shade(c, k):
    c = rgb(c); return tuple(int(clamp(v * k, 0, 255)) for v in c[:3]) + (c[3],)


def cover(img: Image.Image, w=W, h=H) -> Image.Image:
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def remove_flat_background(img: Image.Image, tol=18) -> Image.Image:
    """Rend transparent le fond uni (pris dans les coins) relié aux bords : pour les images générées sur fond blanc."""
    from scipy import ndimage
    a = np.array(img.convert('RGBA')).astype(int)
    corners = np.array([a[0, 0, :3], a[0, -1, :3], a[-1, 0, :3], a[-1, -1, :3]])
    ref = np.median(corners, axis=0)
    close = (np.abs(a[:, :, :3] - ref).max(axis=2) < tol)
    lab, _ = ndimage.label(close)
    border = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1])
    bg = np.isin(lab, [l for l in border if l])
    # bord adouci : 1 px de fondu pour éviter le liseré
    soft = ndimage.binary_dilation(bg, iterations=1) & ~bg
    a[bg, 3] = 0
    a[soft, 3] = (a[soft, 3] * .5).astype(int)
    out = Image.fromarray(a.astype(np.uint8))
    return out.crop(out.getbbox())


def affine_paste(canvas: Image.Image, img: Image.Image, pivot, to, angle=0.0, sx=1.0, sy=1.0):
    """Colle img sur canvas : le point pivot (pixels de img) arrive en `to`, après rotation (degrés) et échelle autour du pivot."""
    bounds = img.getbbox()
    if bounds is None:
        return
    left, top, right, bottom = bounds
    corners = [transform_point((x, y), pivot, to, angle, sx, sy)
               for x in (left - 2, right + 2) for y in (top - 2, bottom + 2)]
    xs, ys = zip(*corners)
    x0, y0 = max(0, math.floor(min(xs))), max(0, math.floor(min(ys)))
    x1, y1 = min(canvas.width, math.ceil(max(xs))), min(canvas.height, math.ceil(max(ys)))
    if x0 >= x1 or y0 >= y1:
        return
    a = math.radians(angle)
    ca, sa = math.cos(a), math.sin(a)
    # matrice directe : p' = to + R*S*(p - pivot) ; PIL attend l'inverse
    m00, m01, m10, m11 = ca * sx, -sa * sy, sa * sx, ca * sy
    det = m00 * m11 - m01 * m10
    i00, i01, i10, i11 = m11 / det, -m01 / det, -m10 / det, m00 / det
    tx, ty = to
    c = i00 * (x0 - tx) + i01 * (y0 - ty) + pivot[0]
    f = i10 * (x0 - tx) + i11 * (y0 - ty) + pivot[1]
    layer = img.transform((x1 - x0, y1 - y0), Image.AFFINE, (i00, i01, c, i10, i11, f), resample=Image.BICUBIC)
    canvas.alpha_composite(layer, (x0, y0))


def transform_point(p, pivot, to, angle=0.0, sx=1.0, sy=1.0):
    a = math.radians(angle)
    x, y = (p[0] - pivot[0]) * sx, (p[1] - pivot[1]) * sy
    return (to[0] + x * math.cos(a) - y * math.sin(a), to[1] + x * math.sin(a) + y * math.cos(a))
