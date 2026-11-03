"""Prépare les calques animables du casting validé, avec les visages dessinés d’origine."""
from pathlib import Path

from PIL import Image
import yaml

ROOT = Path(__file__).parent
PERSONNAGES = ROOT.parents[1] / 'personnages'
CAST = {
    'docteure': (910, [[128,90,166,128],[185,90,217,125]], [154,167,198,190], [177,177], 38),
    'lea': (741, [[94,79,120,104],[136,79,164,107]], [115,139,143,153], [129,146], 29),
}

for nom, (height, eyes, mouth_box, mouth_center, mouth_width) in CAST.items():
    with Image.open(ROOT / f'{nom}.png') as source:
        image = source.convert('RGBA')
    image = image.resize((round(image.width * height / image.height), height), Image.Resampling.LANCZOS)
    folder = PERSONNAGES / f'{nom}-aplats'
    folder.mkdir(parents=True, exist_ok=True)
    image.save(folder / 'corps.png')
    config = {
        'nom': nom.capitalize(), 'type': 'humain',
        'couches': [{'id':'corps','images':{'defaut':'corps.png'},'pivot':[image.width//2,height-1]}],
        'visage': {'mode':'dessine','couche':'corps','yeux':eyes,'yeux_precis':True,
                   'bouche':{'zone':mouth_box,'centre':mouth_center,'largeur':mouth_width}},
        'mouvement': {'souplesse':0.08,'respiration':0.003},
    }
    (folder / 'personnage.yaml').write_text(yaml.safe_dump(config,allow_unicode=True,sort_keys=False))
