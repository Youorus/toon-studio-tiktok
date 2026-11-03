"""Visuels Recraft propres au décor du côlon et au Caca."""
from pathlib import Path
from toonstudio import recraft

ROOT = Path(__file__).parent
ART = ROOT / 'art'
STYLE = (
    "Original simple 2D cartoon design, crisp smooth dark outlines of consistent thin weight, flat bold "
    "colors, one clean cel shadow, no hatching, no grain, no gradients, no 3D rendering. "
    "Strong readable silhouette at phone size. No typography or watermark."
)
SCENES = {
    'colon': ('9:16', [(109,56,59),(182,95,99),(199,119,121),(143,71,75),(247,160,143),(24,19,19)],
        "Vertical stage inside a cartoon human colon in shallow cross-section. Wide open central passage, "
        "a warm coral tissue floor in the lower half, a few large rounded muscle folds visible around the outer edges. "
        "Left wall at eye level a large smooth salmon colored curved tissue section, ample blank surface for a face added later. "
        "Background strong matte red-pink, dark burgundy recesses, simple organic contour rhythm. "
        "The center and right stay open and empty for characters and props to be added later. "
        "Only soft anatomical tissue. No door, no furniture, no people, no eyeballs, no lettering."),
    'caca': ('1:1', [(76,38,40),(113,57,46),(165,87,56),(214,130,82),(255,249,237)],
        "A single original cartoon poop BODY, rounded squat asymmetrical organic lump like a short bent cylinder with two "
        "soft irregular lobes and a flattened bottom. Side facing slightly right, three quarter view, "
        "chestnut terracotta brown with a single darker flat shadow and modest soft folds. "
        "Looks like a malleable organic mass rather than a spiral emoji. No eyes, no mouth, no face, "
        "no arms, no feet, no accessories. Plain solid white background, generous margins."),
}
def main():
    for name,(ratio,palette,prompt) in SCENES.items():
        try:
            print(recraft.generate(prompt+' '+STYLE, ART/name, size=ratio, colors=palette), flush=True)
        except RuntimeError as exc:
            print(name, exc, flush=True)
    organic = (
        'Original hand-inked 2D cartoon model sheet, one isolated dark brown organic cylindrical lump standing upright, '
        'shape resembles a short, gently bent oval sausage with a flat bottom and three soft irregular lateral bulges. '
        'A blunt round top, broad bottom, a slightly S-shaped silhouette, no taper at the top, no peak, no swirl, no stacked coils. '
        'Simple chestnut brown solid color, one dark burgundy shadow on the left, small flat caramel patch. '
        'Smooth dark outline, very readable strong shape, matte cel animation, no grain, no gradients. '
        'No face, no limbs, no accessories, no drop shadow. Centered on plain pure white, clear margins.'
    )
    print(recraft.generate(organic, ART/'caca-b', size='1:1',
                           colors=[(69,35,35),(107,57,43),(151,83,53),(197,119,72),(255,255,255)]))

if __name__ == '__main__':
    main()
