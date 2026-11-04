"""Actifs originaux propres au 009, à partir de texte et de couleurs."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from toonstudio import recraft

ART=Path(__file__).resolve().parent/'art'
SPECS=[
    ('microbe-rouge',4191,'One single original tiny funny cartoon oral bacterium mascot, a compact uneven soft rounded berry-red blob with about 9 smooth lobes, one thin curved flexible tail on right, 2 little tufts. Large uninterrupted flat empty center for animated facial features. NO eyes, no mouth, no eyebrows, no limbs. Smooth thick dark burgundy outlines, very simple clean 2D cel cartoon, flat muted vivid red #D45C58 with a short darker red shadow. Very readable minimal shapes, no texture, no hatching, pure solid white background, full shape visible with broad margins.',[(212,92,88),(154,61,76),(255,249,237),(24,19,19),(255,255,255)]),
    ('ami-source',3397,'Original minimalist 2D flat cel animation character, FULL BODY adult male friend sitting on a simple dark petrol blue chair, facing THREE QUARTER RIGHT, head turned slightly toward right, short simple curly copper brown hair, warm tan skin, long oval large uninterrupted blank face with NO eyes NO eyebrows NO mouth, one simple visible rounded ear, short dark teal t-shirt with no collar, muted slate trousers, brown simple shoes, short relaxed forearms down and hands on thighs, knees bent and legs clear, about 4.0 heads tall. Smooth dark confident outlines, solid colors, only one simple flat shadow, no texture no hatch marks no writing, entire figure visible on pure white, ample margins.',[(38,102,109),(181,127,97),(121,74,53),(83,92,111),(255,249,237),(24,19,19),(255,255,255)]),
]
def render(spec):
    name,seed,prompt,colors=spec
    recraft.generate(prompt,ART/name,model='recraftv4_1',size='1:1',colors=colors,seed=seed)
    print(name,flush=True)
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(render,SPECS))
