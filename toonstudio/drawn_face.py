"""Animation d'un visage DÉJÀ DESSINÉ par Recraft (yeux, nez, bouche dans le style de l'image).

Contrairement à face.py (visage ajouté sur une tête vierge), on garde le dessin d'origine et on anime seulement :
  - le regard : le blanc de l'œil est repeint, la pupille redessinée un peu décalée ;
  - les paupières : couleur de la peau + trait d'encre, selon l'émotion (mêmes réglages que face.EMOTIONS) ;
  - le clignement ;
  - la bouche (si le personnage n'a pas de masque) : l'ancienne est effacée et remplacée par une forme de parole.

Repères dans personnage.yaml (pixels de l'image) :
  visage: {mode: dessine, couche: tete, yeux: [[x0, y0, x1, y1], …], bouche: {zone: [x0, y0, x1, y1], centre: [x, y], largeur: 30}}
"""
import numpy as np
from PIL import Image, ImageChops, ImageDraw
from scipy import ndimage

from .drawing import INK
from .face import EMOTIONS, _mouth

SS = 3


class DrawnFace:
    def __init__(self, img: Image.Image, cfg: dict):
        a = np.array(img.convert('RGBA')).astype(int)
        self.eyes = []
        for x0, y0, x1, y1 in cfg['yeux']:
            x0, y0, x1, y1 = x0 - 7, y0 - 7, x1 + 8, y1 + 8
            sub = a[y0:y1, x0:x1]
            white = (sub[:, :, :3].min(axis=2) > 205) & (sub[:, :, 3] > 200)
            lab, n = ndimage.label(white)
            big = lab == (int(np.argmax(ndimage.sum(white, lab, range(1, n + 1)))) + 1)
            inner = ndimage.binary_fill_holes(big)
            dark = inner & (sub[:, :, :3].max(axis=2) < 110)
            ys, xs = np.nonzero(inner)
            if dark.any():
                py, px = np.nonzero(dark)
                pc = (x0 + px.mean(), y0 + py.mean())
                pr = max(1.5, np.sqrt(dark.sum() / np.pi))
            else:
                pc, pr = (x0 + xs.mean(), y0 + ys.mean()), (xs.max() - xs.min()) * .2
            ring = ndimage.binary_dilation(inner, iterations=7) & ~ndimage.binary_dilation(inner, iterations=3)
            rp = sub[ring & (sub[:, :, 3] > 200)][:, :3]
            rp = rp[(rp.max(axis=1) > 120) & (rp.min(axis=1) < 235)]
            skin = tuple(int(v) for v in np.median(rp, axis=0)) + (255,) if len(rp) else (240, 200, 170, 255)
            white_col = tuple(int(v) for v in np.median(sub[big][:, :3], axis=0)) + (255,)
            self.eyes.append(dict(box=(x0, y0), inner=inner, outline=ndimage.binary_dilation(inner, iterations=2), cover=ndimage.binary_dilation(inner, iterations=4),
                                  bbox=(x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1),
                                  pc=pc, pr=pr, skin=skin, white=white_col))
        self.mouth = cfg.get('bouche')
        if self.mouth:
            x0, y0, x1, y1 = self.mouth['zone']
            sub = a[y0:y1, x0:x1]
            darkm = (sub[:, :, :3].max(axis=2) < 120) & (sub[:, :, 3] > 200)
            self.mouth_mask = (x0, y0, ndimage.binary_dilation(darkm, iterations=2))
            lighter = sub[~darkm & (sub[:, :, 3] > 200)][:, :3]
            self.mouth_skin = tuple(int(v) for v in np.median(lighter, axis=0)) + (255,) if len(lighter) else self.eyes[0]['skin']
        self.cache = {}

    def apply(self, img: Image.Image, emo: str, gaze, blink: bool, mouth: str | None) -> Image.Image:
        key = (emo, gaze, blink, mouth)
        if key in self.cache:
            return self.cache[key]
        e = EMOTIONS.get(emo, EMOTIONS['neutre'])
        arr = np.array(img).copy()
        for i, eye in enumerate(self.eyes):
            x0, y0 = eye['box']
            h, w = eye['inner'].shape
            region = arr[y0:y0 + h, x0:x0 + w]
            if blink or e.get('arc') or e.get('squeeze'):
                cov = eye['cover'][:region.shape[0], :region.shape[1]]
                region[cov] = eye['skin']
            else:
                region[eye['inner']] = eye['white']
        out = Image.fromarray(arr)
        for i, eye in enumerate(self.eyes):
            out = self._eye(out, eye, e, gaze, blink, side=-1 if i == 0 else 1)
        if self.mouth and mouth and mouth not in ('repos', 'M', 'ferme'):
            arr = np.array(out)
            x0, y0, m = self.mouth_mask
            arr[y0:y0 + m.shape[0], x0:x0 + m.shape[1]][m] = self.mouth_skin
            out = Image.fromarray(arr)
            big = Image.new('RGBA', (out.width * SS, out.height * SS), (0, 0, 0, 0))
            cx, cy = self.mouth['centre']
            _mouth(ImageDraw.Draw(big), cx * SS, cy * SS, self.mouth['largeur'] * SS, mouth, 2.2 * SS, None)
            out.alpha_composite(big.resize(out.size, Image.LANCZOS))
        if len(self.cache) > 600:
            self.cache.clear()
        self.cache[key] = out
        return out

    def _eye(self, out, eye, e, gaze, blink, side):
        bx0, by0, bx1, by1 = eye['bbox']
        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
        rw, rh = (bx1 - bx0) / 2, (by1 - by0) / 2
        pad = 6
        W_, H_ = int((bx1 - bx0 + 2 * pad) * SS), int((by1 - by0 + 2 * pad) * SS)
        ox, oy = bx0 - pad, by0 - pad
        P = lambda x, y: ((x - ox) * SS, (y - oy) * SS)
        lay = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        lw = max(2, int(1.6 * SS))
        if blink or e.get('arc'):
            up = e.get('arc')
            x_a, y_a = P(cx - rw * 1.05, cy + (rh * .2 if up else 0))
            x_b, y_b = P(cx + rw * 1.05, cy + (rh * .2 if up else 0))
            bb = (x_a, y_a - rh * SS * (.7 if up else .35), x_b, y_b + rh * SS * (.7 if up else .35))
            d.arc(bb, 200 if up else 20, 340 if up else 160, fill=INK, width=lw)
            out.alpha_composite(lay.resize((W_ // SS, H_ // SS), Image.LANCZOS), (ox, oy))
            return out
        if e.get('squeeze'):
            k = side
            pts = [P(cx - rw * .7 * k, cy - rh * .5), P(cx + rw * .6 * k, cy), P(cx - rw * .7 * k, cy + rh * .5)]
            d.line(pts, fill=INK, width=lw, joint='curve')
            out.alpha_composite(lay.resize((W_ // SS, H_ // SS), Image.LANCZOS), (ox, oy))
            return out
        # pupille : position dessinée d'origine + petit décalage du regard
        px, py = eye['pc']
        px += gaze[0] * rw * .35
        py += gaze[1] * rh * .25
        pr = eye['pr'] * e['pupil']
        d.ellipse((*P(px - pr, py - pr), *P(px + pr, py + pr)), fill=INK)
        hr = max(.6, pr * .3)
        d.ellipse((*P(px - pr * .35 - hr, py - pr * .4 - hr), *P(px - pr * .35 + hr, py - pr * .4 + hr)), fill=(255, 255, 255, 255))
        # paupières selon l'émotion
        lid = Image.new('RGBA', lay.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lid)
        if e['lid'] > .05:
            y = by0 + (by1 - by0) * e['lid']
            t = e['tilt'] * rh * .8 * (1 if side < 0 else -1)
            ld.polygon([P(ox, oy), P(ox + W_ / SS, oy), P(ox + W_ / SS, y - t), P(ox, y + t)], fill=eye['skin'])
            ld.line([P(bx0 - 1, y + t * (1 if True else 0)), P(bx1 + 1, y - t)], fill=INK, width=lw)
        if e['low'] > 0:
            y = by1 - (by1 - by0) * e['low']
            ld.ellipse((*P(bx0 - rw * .3, y), *P(bx1 + rw * .3, y + rh * 2)), fill=eye['skin'])
            ld.arc((*P(bx0 - rw * .3, y), *P(bx1 + rw * .3, y + rh * 2)), 200, 340, fill=INK, width=max(1, lw - 1))
        mask = Image.new('L', lay.size, 0)
        m = Image.fromarray((eye['outline'] * 255).astype(np.uint8)).resize(
            (eye['outline'].shape[1] * SS, eye['outline'].shape[0] * SS), Image.NEAREST)
        mask.paste(m, (int((eye['box'][0] - ox) * SS), int((eye['box'][1] - oy) * SS)))
        lid.putalpha(ImageChops.multiply(lid.getchannel('A'), mask))
        lay.alpha_composite(lid)
        out.alpha_composite(lay.resize((W_ // SS, H_ // SS), Image.LANCZOS), (ox, oy))
        return out
