"""Candidats visuels de l’épisode. Exécuter avec python depuis la racine de Toon Studio."""
from pathlib import Path

from toonstudio import recraft

OUT = Path(__file__).parent / 'art'
STYLE = (
    "Clean hand-inked 2D cel animation for a French educational cartoon, clear smooth contours, "
    "confident flat colors, carefully drawn anatomy, two shadow tones maximum, restrained pin highlights. "
    "Stylized but credible proportions. No grain, no hatch, no sketch, no gradients, no 3D gloss, "
    "no labels, no text, no logos, no watermark. Distinct original character design."
)
COLORS = {
    'anatomie': [(73, 42, 56), (134, 54, 73), (188, 77, 102), (232, 125, 135), (247, 174, 161), (255, 227, 199)],
    'cellule': [(24, 19, 19), (255, 249, 237), (137, 211, 208), (49, 133, 143), (253, 199, 124)],
}
ASSETS = {
    'coupe-uterus': ('9:16', 'anatomie',
        "Portrait. Simplified medically legible frontal section of a human uterus in the upper-middle of the frame. "
        "Continuous inverted pear shape with a clearly open pale salmon central cavity. At the top, two connected narrow "
        "fallopian tubes curve symmetrically out and toward two separate small almond-shaped ovaries with clear negative space. "
        "The lower part narrows continuously into a short cervix. Smooth selective dark red tissue rims, "
        "solid deep aubergine surrounding field. Show the whole diagram including both ovaries, approximately "
        "75% canvas width, top gap 14%, bottom gap 30%. Smooth internal region for moving an overlay, no characters, no eyes."),
    'trompe-macro': ('9:16', 'anatomie',
        "Portrait frame for a scene taking place in the lumen of a fallopian tube. Close-up longitudinal anatomical section with "
        "an open simple pale salmon channel crossing the image diagonally from bottom left to upper right, broad and uninterrupted. "
        "Curved rose red soft tissue walls are only in the top-left and lower-right corners with sparse gentle folds, "
        "ample calm open lumen in the central 75% of the image for an animated sperm cell. Cool dark wine-red outer edges. "
        "Flat graphic planes with a few subtle sweeping contours that direct attention rightward. No objects and no figures."),
    'cellule': ('1:1', 'cellule',
        "An isolated single anatomically recognizable human sperm cell icon with a flattened compact tapered oval head, "
        "a short narrow neck and one long thin wavy flagellum. Head in a soft cream with a small pale teal shaded segment "
        "at the top, dark clean outline. Vertical orientation with the head at the TOP, tail below. "
        "Head shape has a clean smooth outer contour. Face-free, no eyes or mouth, no limbs. "
        "Single asset centered with margins, flat solid pure white background."),
    'ovocyte': ('1:1', 'anatomie',
        "An isolated unfertilized human egg cell in the style of a bright educational 2D cartoon medical diagram. "
        "One circular cell with a simple pale apricot membrane ring and warm golden coral interior, distinct dark contour "
        "and two restrained small translucent granule shapes inside. Round continuous outline. "
        "Face-free, no eyes or mouth. Centered on pure solid white with generous margin."),
    'soignante': ('9:16', None,
        "Full body stylized French female doctor age 48, facing front but subtly turned toward screen right, planted stance, "
        "dark auburn curly hair in a low rounded bun, long cream medical coat open over a deep petrol teal blouse, "
        "slate trousers and ochre shoes. Petite, sturdy adult build, warm medium brown skin, one hand relaxed at side and the "
        "other at waist with a small closed muted teal notebook. Clean blank facial area for later eye and mouth animation, "
        "no face, no eyes, no eyebrows, no mouth, small understated nose optional. White background, whole character within margins."),
    'patiente-episode': ('9:16', None,
        "Full body original French woman patient age 31, subtly turned toward screen left, short dark curly bob, "
        "warm olive complexion, terracotta pullover with a wide boat neckline, high-waisted muted plum trousers, ivory sneakers, "
        "one hand on the other forearm in a natural slightly worried pose, adult proportions, plain warm white background. "
        "Blank face, no eyes, no eyebrows, no mouth. The whole body visible with margins."),
}

CABINET = (
    "Empty INTERIOR BACKGROUND PLATE, flat 2D cel animation. The image contains only architecture and furniture. "
    "Portrait front-on wide view. A pale sage wall occupies the center, a tall window with cream blind cropped to the extreme left, "
    "a low credenza with two closed drawers on the extreme right, three small wall art frames, warm gray matte floor visible in lower third. "
    "Center fully empty. Empty room. Subtle dusty sage, muted teal trim, matte ochre trim. Clean dark contours, smooth solid flat fills, "
    "two simple shadow tones. Architectural illustration without people, figures, faces, silhouettes, creatures, typography, or grain."
)


def main():
    for name, (ratio, palette, prompt) in ASSETS.items():
        print(recraft.generate(prompt + " " + STYLE, OUT / name, size=ratio, colors=COLORS.get(palette)), flush=True)
    print(recraft.generate(CABINET, OUT / 'cabinet-vide', size='9:16', n=2,
                           colors=[(43, 75, 80), (128, 158, 151), (207, 222, 210), (235, 220, 189), (165, 147, 128)]))


if __name__ == '__main__':
    main()
