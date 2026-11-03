"""Calques animables, décor de microscope et bruitages fabriqués à partir des éléments de l’épisode."""
import math
from pathlib import Path
import wave

import numpy as np
from PIL import Image, ImageDraw
import yaml

from toonstudio.drawing import cover, font, remove_flat_background

ROOT = Path(__file__).parent
ART = ROOT / 'art'
W, H = 1080, 1920


def load(name):
    return Image.open(ART / f'{name}.png').convert('RGBA')


def install(name, image, cfg):
    folder = ROOT / 'personnages' / name
    folder.mkdir(exist_ok=True, parents=True)
    image.save(folder / 'corps.png')
    (folder / 'personnage.yaml').write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))


def root_layer(pivot):
    return [{'id': 'corps', 'images': {'defaut': 'corps.png'}, 'pivot': pivot}]


def prepare_human(name, source, eyes, mouth, neck, eye_r, skin, glasses=None):
    raw = load(source)
    img = remove_flat_background(raw, tol=26)
    # Les repères sont en proportions du PNG Recraft complet. Reprendre son cadre de détourage.
    corners = raw.getpixel((0, 0))[:3]
    a = np.array(raw)[:, :, :3].astype(int)
    from scipy.ndimage import label
    delta = np.abs(a - np.array(corners)).max(axis=2)
    lab, _ = label(delta < 26)
    ids = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])
    bg = np.isin(lab, ids[ids != 0])
    ys, xs = np.where(~bg)
    x0, y0 = int(xs.min()), int(ys.min())
    scale = 910 / img.height
    img = img.resize((round(img.width * scale), 910), Image.Resampling.LANCZOS)
    def xy(point):
        return [round((point[0] * raw.width - x0) * scale), round((point[1] * raw.height - y0) * scale)]
    eyes, mouth, neck = xy(eyes), xy(mouth), xy(neck)
    r = round(eye_r * raw.width * scale)
    face = {'couche': 'tete', 'yeux': eyes, 'rayon_oeil': r, 'ecart': 2.27,
            'bouche': mouth, 'largeur_bouche': r * 2, 'peau': skin, 'forme_oeil': 1.12,
            'pupille': 0.71, 'paupiere': 0.10, 'trait': 0.09}
    if glasses:
        face['lunettes'] = glasses
    install(name, img, {
        'nom': name, 'type': 'humain',
        'couches': root_layer([img.width // 2, img.height - 1]),
        'decoupe_tete': {'y': neck[1], 'cou': neck}, 'visage': face,
        'mouvement': {'souplesse': 0.18, 'respiration': 0.005},
    })


def prepare_cell(name, colored):
    raw = load('cellule')
    crop = (438, 132, 575, 424)
    cell = raw.crop(crop)
    pixels = np.array(cell)
    from scipy.ndimage import label
    white = np.min(pixels[:, :, :3], axis=2) >= 242
    lab, _ = label(white)
    ids = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])
    pixels[np.isin(lab, ids[ids > 0]), 3] = 0
    if colored:
        mask = ((pixels[:,:,1].astype(int) - pixels[:,:,0] > 5)
                & (pixels[:,:,2].astype(int) - pixels[:,:,0] > 8)
                & (pixels[:,:,3] > 0))
        pixels[mask, :3] = (133, 170, 238)
    cell = Image.fromarray(pixels)
    # Le corps et le cou viennent du modèle Recraft. L'animation remplace la queue figée.
    width = 151 if colored else 156
    height = 246 if colored else 268
    cell = cell.resize((width, height), Image.Resampling.LANCZOS)
    angle = -58 if colored else -73
    result = cell.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    def transform(fx, fy):
        a = math.radians(-angle)
        x, y = width * (fx - 0.5), height * (fy - 0.5)
        return [round(result.width / 2 + x * math.cos(a) - y * math.sin(a)),
                round(result.height / 2 + x * math.sin(a) + y * math.cos(a))]
    join = transform(0.49, 0.93)
    pivot = transform(0.47, 0.36)
    eyes = [pivot[0] + 15, pivot[1] - 10]
    mouth = [pivot[0] + 21, pivot[1] + 23]
    install(name, result, {
        'nom': name, 'type': 'organe', 'couches': root_layer(pivot),
        'visage': {'couche': 'corps', 'yeux': eyes, 'rayon_oeil': 18, 'ecart': 2.04,
                   'bouche': mouth, 'largeur_bouche': 37, 'peau': '#F8EDDA',
                   'forme_oeil': 1.16, 'pupille': 0.69, 'trait': 0.095, 'paupiere': 0.08},
        'flagelle': {'attache': join, 'longueur': 235 if colored else 228, 'amplitude': 43 if colored else 47,
                    'angle': 152 if colored else 164, 'frequence': 2.1 if colored else 3.3,
                    'couleur': '#85AAEE' if colored else '#89D3D0', 'epaisseur': 17},
        'mouvement': {'souplesse': 0.24, 'respiration': 0.004},
    })


def prepare_map():
    m = cover(load('coupe-uterus'))
    # Remonter le schéma pour réserver une bande aux légendes.
    bg = Image.new('RGBA', (W, H), m.getpixel((2, 200)))
    bg.alpha_composite(m, (0, -174))
    bg.save(ROOT / 'decors/uterus.png')
    ovule = remove_flat_background(load('ovocyte'), tol=21)
    ovule.thumbnail((245, 245), Image.Resampling.LANCZOS)
    install('ovocyte', ovule, {
        'nom': 'Ovocyte', 'type': 'organe',
        'couches': root_layer([ovule.width // 2, ovule.height // 2]),
        'mouvement': {'souplesse': 0, 'respiration': 0},
    })


def prepare_microscope():
    img = Image.new('RGB', (W, H), '#143F49')
    d = ImageDraw.Draw(img)
    d.ellipse((68, 240, 1012, 1190), fill='#D3EAE4', outline='#719D9E', width=13)
    d.ellipse((91, 263, 989, 1167), outline='#AAD0C9', width=4)
    for y in (630, 900):
        d.line((222, y + 98, 857, y + 98), fill='#86AEAA', width=3)
        for x in range(222, 858, 80):
            d.line((x, y + 90, x, y + 106), fill='#86AEAA', width=3)
    d.rounded_rectangle((238, 333, 842, 416), radius=30, fill='#164B55')
    d.text((540, 375), 'SOUS LE MICROSCOPE', fill='#FFF9ED', font=font('Fredoka', 45), anchor='mm')
    img.save(ROOT / 'decors/microscope.png')


def sounds():
    path = ROOT / 'sons'
    path.mkdir(exist_ok=True)
    sr = 48000
    for name, duration, f0, f1, amp in (
        ('bulle', .21, 285, 485, .24),
        ('glisse', .38, 235, 525, .14),
        ('loupe', .24, 440, 705, .17),
    ):
        t = np.arange(round(sr * duration)) / sr
        phase = 2 * np.pi * (f0 * t + (f1 - f0) * t*t / (2 * duration))
        env = np.minimum(1, t * 52) * (1 - t / duration)**3
        sig = amp * env * (np.sin(phase) + 0.16 * np.sin(2.03 * phase))
        with wave.open(str(path / f'{name}.wav'), 'wb') as out:
            out.setparams((1, 2, sr, 0, 'NONE', 'not compressed'))
            out.writeframes((sig * 32767).astype('<i2').tobytes())


def main():
    prepare_cell('nino', False)
    prepare_cell('malo', True)
    prepare_map()
    prepare_microscope()
    cover(load('trompe-macro')).save(ROOT / 'decors/trompe.png')
    cabinet = cover(load('cabinet-vide-2'))
    shadow = Image.new('RGBA', cabinet.size)
    d = ImageDraw.Draw(shadow)
    for x in (328, 713):
        d.ellipse((x - 100, 1630, x + 106, 1662), fill=(33, 41, 43, 52))
    cabinet.alpha_composite(shadow)
    cabinet.save(ROOT / 'decors/cabinet.png')
    prepare_human('soignante', 'soignante', (0.533, 0.191), (0.538, 0.221), (0.51, 0.260), 0.027, '#B78266')
    prepare_human('lea', 'patiente-episode', (0.520, 0.105), (0.528, 0.141), (0.470, 0.195), 0.032, '#C19C7D')
    sounds()


if __name__ == '__main__':
    main()
