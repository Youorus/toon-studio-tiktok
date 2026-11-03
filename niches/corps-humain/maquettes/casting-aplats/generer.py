"""Deux modèles de personnage à comparer au casting de l’épisode 004."""
from pathlib import Path
import sys

from toonstudio import recraft

OUT=Path(__file__).parent
STYLE=(
    "Very simple 2D cartoon animation model, full figure and white seamless background. Copy only the reference's drawing treatment: "
    "thin even clean dark outlines, flat untextured opaque color areas, slightly oversized round white eyes and small black pupils, "
    "one nose curve, tiny mouth, simple chunky hands, simplified anatomy with readable posture. "
    "Few internal lines. Clean contour and completely flat colors. No gradients, rendering, glossy lighting, hatching, grain, shadows on the ground, "
    "extra figures, margins clipped, typography, watermark or play icon. Original character specific to the description."
)
ART={
    'docteure': ("A woman doctor of about 48, warm medium brown skin, dark auburn curly hair in a low bun, strong recognizable "
                 "silhouette, cream-white long coat over a single solid deep petrol teal top, dark charcoal trousers and ochre flat shoes. "
                 "Standing facing to screen right in three quarter view, holding a simple small teal clipboard in both hands at waist height, "
                 "friendly attentive open eyes, bare face, neither eyeglasses nor mask. Entire body and both feet visible with margin.",
                 [(33,28,32),(172,108,77),(97,54,44),(251,244,220),(36,97,105),(53,58,61),(168,118,63),(255,255,255)]),
    'lea': ("An adult French woman patient called Léa, warm olive skin, a short dark charcoal curly bob, "
            "a plain solid terracotta long-sleeved boat-neck sweater, dark plum trousers, cream sneakers. Seated upright on a simple "
            "dark chair facing screen left in a three quarter view. Both hands gently together over her knees, face with an attentive "
            "slightly worried expression. Entire body, hands, chair, and both feet visible with margin.",
            [(33,28,32),(190,150,106),(52,46,43),(184,110,87),(103,66,91),(253,244,217),(255,255,255)]),
}
if __name__=='__main__':
    ref=Path(sys.argv[1])
    for name,(description,palette) in ART.items():
        try:
            paths=recraft.generate(description+' '+STYLE,OUT/name,model='recraftv4_styles_vector',
                                   size='3:4',style_refs=[ref],colors=palette)
        except RuntimeError as e:
            print(f'{name}: {e}',flush=True)
            paths=recraft.generate(description+' '+STYLE,OUT/name,model='recraftv4_1_vector',
                                   size='3:4',colors=palette)
        print(paths,flush=True)
