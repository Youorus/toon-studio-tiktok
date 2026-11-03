"""Génère les illustrations Recraft employées dans la reprise 007."""
from argparse import ArgumentParser
from pathlib import Path

from toonstudio import recraft

ART=Path(__file__).resolve().parent/'art'
PALETTE=[(231,82,97),(246,160,157),(255,213,193),(109,56,59),(255,249,237),(255,255,255)]
FOETUS=(
    'Single compact adorable cartoon fetus cutout for original 2D French anatomy animation, three-quarter side profile FACING LEFT. '
    'Smooth pale peach-pink and soft cream cel paint with one simple pink cel shadow, thick dark burgundy outlines. '
    'Visibly newborn proportions about 2.1 heads tall, medium gently oval head and clear small rounded nose on left outline, visible simple ear on the right, only tiny comma-shaped dark tuft at crown. '
    'No eyes, mouth or eyebrows because animated later. Small tucked chin, stubby bent arms and rounded knees tucked toward belly, very compact curl, small distinct feet with closed forms, tiny cream onesie with no patterns. '
    'Non-graphic. Whole body and adequate margins, isolated solid pure white background. No words, no ground shadow, no cord. '
    'Attractive minimal expressive classic 2D animation proportions, NOT a giant perfectly spherical head.'
)
PLACENTA=(
    'Original clean minimalist 2D cel cartoon, smooth thick dark burgundy outlines, confident vivid flat colors, short flat shadows, no texture, no gradients. '
    'One friendly human placenta cartoon cutout for a health explainer, stylized as a thick rounded soft lumpy coral red disk with a handful of broad curved wine-red branching marks only near the edges. '
    'Center of the disk blank to add animated eyes. No cord, no eyes, no face, no writing, no limbs, isolated on pure white, generous margins. Distinct soft red organic silhouette, visible from the front.'
)

if __name__=='__main__':
    parser=ArgumentParser()
    parser.add_argument('calque',choices=('foetus','placenta'))
    args=parser.parse_args()
    if args.calque=='foetus':
        spec=FOETUS,'foetus-reprise',2264,PALETTE
    else:
        spec=PLACENTA,'placenta',783,[(231,82,97),(246,144,145),(182,95,99),(109,56,59),(255,249,237),(24,19,19)]
    prompt,name,seed,palette=spec
    recraft.generate(prompt,ART/name,model='recraftv4_1',size='1:1',seed=seed,colors=palette)
