"""Génère les trois illustrations de l'épisode, à partir de texte et de couleurs."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from toonstudio import recraft

ART = Path(__file__).resolve().parent / 'art'
STYLE = 'Original clean minimalist 2D cel cartoon, smooth thick dark burgundy outlines, confident vivid flat colors, short flat shadows, no texture, no gradients. '
PALETTE = [(231,82,97),(246,144,145),(182,95,99),(109,56,59),(255,249,237),(24,19,19)]

def create(spec):
    name, shape, seed, text = spec
    return recraft.generate(STYLE + text, ART / name, size=shape, seed=seed, colors=PALETTE)

if __name__ == '__main__':
    subjects = [
        ('uterus-interieur','9:16',2913,'Vertical portrait 9:16, educational comic simplified inside view of a pregnant uterus cross section. The uterus is an enormous empty soft sac lined with a few broad smooth curved layered tissue contours at the edges, a tapered bottom and a curved dome. Bright living coral red outer tissue #E75261, flat lighter coral central sac, burgundy depth at both sides. Large empty middle stage from x=20 to 83 percent y=26 to 75 percent for three characters to be layered later. No characters, no baby, no placenta, no faces, no furniture, no text, no realistic gore.'),
        ('placenta','1:1',783,'One friendly human placenta cartoon cutout for a health explainer, stylized as a thick rounded soft lumpy coral red disk with a handful of broad curved wine-red branching marks only near the edges. Center of the disk blank to add animated eyes. No cord, no eyes, no face, no writing, no limbs, isolated on pure white, generous margins. Distinct soft red organic silhouette, visible from the front.'),
        ('foetus','1:1',1740,'Single adorable stylized human fetus cartoon in a side three-quarter curled floating fetal pose facing left, huge round peach pink head, tiny curled arms and bent legs, clenched little fists, smooth doll-like educational medical art, non-graphic and completely featureless anatomy, large blank face to add expressions, no eyes no mouth no eyebrows, no umbilical cord, no words, on pure white background with generous margin. Avoid thin tiny details.'),
    ]
    with ThreadPoolExecutor(max_workers=3) as executor:
        for paths in executor.map(create,subjects):
            print(paths[0].name,flush=True)
