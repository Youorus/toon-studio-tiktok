"""Illustrations nouvelles de l'épisode 008, créées à partir de texte et de couleurs."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from toonstudio import recraft

ART=Path(__file__).resolve().parent/'art'
SPECS=[
    ('cerveau-source',3833,'A single front-facing human brain character base, anatomical left and right hemispheres with only a few readable folds mostly on the edges, wide chunky puffy organic silhouette, lower cerebellum hint. Original minimalist 2D cel cartoon, thick smooth dark burgundy contour, flat warm light pink and coral pink with one simple shadow, completely uninterrupted smooth central face zone to animate later. No eyes, no eyebrows, no mouth, no limbs, no props, no words, centered on pure solid white with broad margins.',[(246,155,155),(199,119,121),(109,56,59),(255,249,237),(24,19,19)]),
    ('plateau-source',4492,'A simple 2 by 2 SPRITE SHEET with FOUR completely separated small cartoon food icons, equally spaced, generous white space, absolutely nothing crossing quadrants. Top left a single stacked cheeseburger with toasted bun, lettuce, cheese and patty. Top right a small loose pile of golden French fries clearly separate from other objects. Bottom left one cooked chicken drumstick viewed diagonally with tiny cream bone. Bottom right one plain closed kraft paper takeaway bag with a folded top and no logo. Original minimalist 2D cartoon cel paint, smooth deep dark outlines, cheerful solid natural colors, very few details, no highlights outside the silhouettes, pure white background, no text, no labels, no shadows on background.',[(255,249,237),(238,180,79),(181,127,97),(91,221,121),(109,56,59),(24,19,19)]),
]
def render(spec):
    name,seed,prompt,colors=spec
    recraft.generate(prompt,ART/name,model='recraftv4_1',size='1:1',colors=colors,seed=seed)
    print(name,flush=True)
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(render,SPECS))
