"""Quatre illustrations manquantes, ciblées sur les défauts de la V1 rejetée."""
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from toonstudio import recraft

ROOT=Path(__file__).resolve().parent
NICHE=ROOT.parents[1]
ART=ROOT/'art/v2'
STYLE=(
    'Original French health cartoon, same clean hand-inked retro 2D cel animation finish throughout: '
    'confident thin near-black warm burgundy ink contours, smooth vivid separated flat colors, '
    'one short flat colored shadow per surface, sparse small soft-edged cel highlights, '
    'simple expressive shapes readable on a phone, professional traditionally drawn animation background. '
    'No pencil hatching, no sketch lines, no 3D, no generic vector infographic, no gradients, '
    'no typography, no watermark, no face, no eyes, no character, no limbs. '
)
PALETTE=[(231,82,97),(246,132,139),(238,101,118),(199,119,121),(109,56,59),(255,249,237),(24,19,19)]
SPECS={
    'caca':('1:1',
        'ONE single plain cartoon brown stool body asset isolated on pure white, generous blank margins. '
        'A broad rounded irregular chunky oval, one continuous fat pear-like organic mass, slightly asymmetric sloping rounded top, '
        'short wide nearly flat base. Body height about 1.25 times its width. '
        'Warm medium chestnut brown, one muted reddish dark brown shadow on left edge and tiny caramel cel highlight. '
        'A few shallow subtle creases near the sides only, broad blank central surface for a face to be animated later. '
        'Readable brown organic lump. No spiral, no stacked balls, no cone, no tapered peak, no sausage, no stick, '
        'no emoji, no eyes, no mouth, no hands, no legs, no scenery. ',
        [(141,82,55),(165,99,65),(110,61,48),(196,128,82),(109,56,59),(255,255,255)],73410),
    'rectum':('9:16',
        'Vertical theatrical stage INSIDE the lower human large intestine. The central passage is broad and empty, '
        'warm vivid coral red #E75261 floor fills the bottom half, a few low flat wavy tissue lines provide ground contact. '
        'Above and on both sides, THREE broad curved concentric salmon-pink muscular folds form a shallow rounded tunnel arch. '
        'The curves follow each other smoothly toward a wide empty center; flattened soft anatomical folds, no giant bulbous lumps. '
        'Pink rim highlights and short burgundy cel shadows convey the thickness of each tissue fold. '
        'Bright coral fills every corner; keep the center from x=25% to 88%, y=35% to 75% clear for two animated characters and a door added later. '
        'Full frame warm anatomical stage, no black cave, no door, no rectangular panels, no furniture. ',
        PALETTE,73411),
    'coupe':('9:16',
        'Non-graphic educational ANATOMICAL CUTAWAY of the lower large intestine and rectum, one large clearly curved vertical '
        'S-shaped peach inner passage down the middle, bounded by smooth layered coral pink muscle walls with narrow burgundy outlines. '
        'The passage bends right near the top, left at midheight, gently right near the lower half, narrowing smoothly to a small outlet near bottom center. '
        'The lumen is wide and visible, an uncluttered peach #F0A080 surface. Rounded nested contours model the thickness of the walls. '
        'Large close-up, fills 75 percent of the frame width and all height, anatomical asymmetry and soft curves, no ruler-straight tube, '
        'no diagram labels, no other organs, no exterior genital anatomy. Background entirely vivid coral #E75261 including all four corners. '
        'No beige or black exterior background. No contents: completely empty lumen, no stool yet. ',
        PALETTE+[(240,160,128)],73412),
    'toilettes':('9:16',
        'Hand-drawn cartoon domestic bathroom background, medium view from standing eye height, gentle three-quarter perspective. '
        'A clean cream ceramic toilet with raised lid on the LEFT in the lower half, its broad oval bowl and pale blue water '
        'seen from above. Bowl center at x=30%, y=72%, raised cistern behind at y=57%. '
        'Right half empty for one STANDING character to be added, no chair, no stool seat, no person. '
        'Pale grey-green ceramic tiled wall with simple dark grout lines, blue-grey floor, a few tasteful muted teal wall details. '
        'Readable toilet, curved porcelain rim, oval water, simple credible perspective and short cel shadows. '
        'Smooth ink outlines, flat cel colors and no geometric vector icon look. Not a yellow room. Empty bowl, no waste. ',
        [(229,230,224),(179,194,204),(175,189,186),(255,249,237),(145,211,223),(109,56,59),(36,102,109)],73413),
}
SPECS['coupe-propre']=('9:16',
    'Match precisely the thin clean ink outlines, flat vivid coral cel colors and restrained painted shadows of the attached APPROVED anatomy background. '
    'Original educational cartoon CUTAWAY of the RECTUM, only the last lower part of a large intestine, not a whole colon. '
    'A broad peach inner cavity starts beyond the TOP EDGE of the frame, gently bends from the right toward the left at midheight, '
    'then follows a broad S curve back toward the center and a narrowing relaxed outlet at the bottom. '
    'The top is cropped OPEN, no closed hook, no question mark silhouette. Pink muscular walls have two thin nested contours '
    'and one dark pink cel shadow. Lumen stays wide enough for a large stool to slide through. '
    'Outside entirely vivid coral #E75261. Simple recognizable organic cross-section, attractive clean 2D animation, '
    'minimal fine anatomical contour details, no geometric ruler-straight tubing, no sketch, no hatching, no white shine stripes, '
    'no text, no face, no stool, no contents, no characters, no genitals, non-graphic.',
    PALETTE+[(240,160,128)],73416)
SPECS['rectum-propre']=('9:16',
    'Original 2D animated health comedy background, MATCH THE FINISH OF THE ATTACHED APPROVED ANATOMY BACKGROUND: crisp clean thin ink lines, '
    'saturated coral and salmon color fields, one small cel shadow, sparse restrained small highlights. Not hand sketched and not painterly. '
    'A front view inside a human rectum, a broad shallow rounded coral chamber. Very subtle large wavy horizontal tissue ridges curve round '
    'the ceiling and side walls, EMPTY center and floor, simple smooth rounded wall folds. Wide floor in vivid coral #E75261 from half-height '
    'to bottom. Same coral in the corners. The frame must leave central 70 percent open for characters and a door added later, no door yet, '
    'no object, no face, no eyes, no character, no text. More like a clean cartoon anatomical corridor than a cave. NO white streaks, no cream '
    'bands, no glossy wrinkles, no black background, no giant rounded sausages. Smooth solid painted cel areas, very few confident dark contours.',
    [(231,82,97),(246,132,139),(238,101,118),(199,119,121),(109,56,59),(24,19,19)],73415)

def generate(name):
    if (ART/(name+'.png')).exists():
        print(name,'réemploi du fichier présent',flush=True);return
    ratio,prompt,palette,seed=SPECS[name]
    # Référence de finition : actif de notre propre casting, jamais une image du tiers.
    refs=([NICHE/'decors/estomac-corail.png'] if name.endswith('propre') else
          [NICHE/'personnages/docteure-aplats/corps.png'] if name=='toilettes' else None)
    paths=recraft.generate(prompt if name.endswith('propre') else prompt+STYLE,ART/name,model='recraftv4_1',size=ratio,
                           colors=palette,seed=seed,style_refs=refs)
    print(name,paths[0].name,flush=True)

if __name__=='__main__':
    parser=ArgumentParser();parser.add_argument('elements',nargs='*');args=parser.parse_args()
    ART.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(generate,args.elements or SPECS))
