"""Deux illustrations de correction. Chaque source existante est reprise depuis le disque."""
from argparse import ArgumentParser
from pathlib import Path
from toonstudio import recraft

ART=Path(__file__).resolve().parent/'art'
SPECS={
    'bouche':('bouche-reprise-source','9:16',91673,
        'Original clean smooth retro 2D cel animation anatomical interior of a human open mouth, front-on close view, vertical 9:16. Strong clear anatomical shapes with rounded contours and moderately detailed folds, vivid coral red #E75261 cheek tissue filling ALL four corners, upper arch of clearly rounded cream-white teeth emerging from curved fleshy red gums at upper 18 to 31 percent, visible individual tooth curvature with one short cel shadow, side cheek folds, a broad beautiful reddish pink tongue taking up the lower 45 percent with central longitudinal groove, natural curved tip and 3 gentle papillae hints, tongue forms an empty stage at x=25 to 80 percent y=58 to 74 percent for characters to be added later, no eyes no faces no microbes no characters no writing. Mouth cavity and throat use colored burgundy reds, no black-filled area, no black border. Smooth confident dark ink contour, vivid solid flat cel paints with single flat shadows and only a few smooth cream highlights on wet tissue. No hatching, no pencil, no speckled texture, no watercolor, no photorealism, no glossy 3D. Readable and appealing medical cartoon, not an abstract oval symbol.',
        [(231,82,97),(237,121,129),(182,95,99),(109,56,59),(199,119,121),(255,249,237),(24,19,19),(145,211,223)]),
    'assiette':('assiette-source','1:1',85327,
        'One single appealing cartoon breakfast plate cutout, a large oval ivory ceramic plate, close view from a slightly elevated three-quarter frontal perspective, clearly showing the food. Two thick golden toast slices with brown crusts, one fried egg with bright yellow round yolk and creamy white, 2 red tomato wedges and a few green leaves. Food all sits naturally INSIDE the plate, no objects outside plate, entire plate visible, broad margin, solid PURE WHITE background. Original minimalist smooth retro 2D cel animation, confident clean dark outlines of constant width, vivid flat colors, one short flat shadow per shape, small restrained highlights, no black gradients, no texture no hatching no writing no table no cutlery no hands no characters.',
        [(255,249,237),(238,180,79),(181,127,97),(91,221,121),(212,92,88),(24,19,19),(255,255,255)]),
}

if __name__=='__main__':
    parser=ArgumentParser()
    parser.add_argument('element',choices=SPECS)
    args=parser.parse_args()
    name,size,seed,prompt,colors=SPECS[args.element]
    out=ART/name
    if out.with_suffix('.png').is_file():
        print(out.with_suffix('.png'))
    else:
        recraft.generate(prompt,out,model='recraftv4_1',size=size,seed=seed,colors=colors)
