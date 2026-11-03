"""Illustrations propres à l’épisode. Le cabinet et son casting viennent de l’épisode 004."""
from pathlib import Path
from toonstudio import recraft

ART = Path(__file__).parent / 'art'
STYLE = ("French educational 2D cartoon, smooth thin dark ink contours, vivid clean flat cel colors, "
         "a few selective matte shadows, original forms, clear anatomy, no noise, hatching, grain, typography, watermark, or 3D gloss.")
BODY = [(73,42,56),(134,54,73),(188,77,102),(232,125,135),(247,174,161),(255,227,199)]
ITEMS = {
 'estomac': ('9:16', BODY,
    "Portrait textbook-like cartoon frontal cutaway of the inside of a human stomach. Clear tube enters from the top and widens into a large asymmetrical J-shaped chamber, "
    "the lower curve narrows to a short outlet on the lower right. Large interior pale coral, shallow peach gastric liquid at the bottom edge. "
    "Burgundy tissue around the cavity, a few wide visible clean folds. Most of the central space empty. No characters, no eyes, no objects, no labels. Whole stomach from entry to exit recognizable."),
 'plaie': ('9:16', BODY,
    "Portrait 2D educational skin diagram, close-up side cross-section with one small scraped skin breach in the upper center. "
    "Single horizontal skin surface at around upper third, a shallow notch with an interrupted surface, smooth salmon tissue beneath. "
    "Below the skin, broad open pink space for animated cells, lightly colored, a few sparse deeper curved lines at the bottom. "
    "Pale dusty cream upper third. Skin anatomy simplified and non-graphic, no blood pools, no faces, no cells or objects, no text."),
 'gelule': ('1:1', [(42,60,82),(44,123,149),(138,205,210),(255,249,237)],
    "One isolated generic medicine capsule, upright, two rounded ends, upper half calm dark teal and bottom half ivory, thin dark outline, clean matte cel shadow. "
    "Entire simple shape visible on pure white. Face-free, no limbs, no letters, no markings."),
 'bacterie': ('1:1', [(38,80,65),(64,149,100),(113,217,130),(219,252,185),(255,255,255)],
    "One isolated anthropomorphizable rod-shaped bacterium body, asymmetrical soft rounded bean silhouette, bright yellow green with a soft dark green cel shadow, "
    "three small flexible bristles at the edges, no face, no limbs, no eyes. Flat pure white background."),
 'resistante': ('1:1', [(52,41,82),(107,74,156),(175,135,207),(214,187,238),(255,255,255)],
    "One isolated purple rod-shaped bacterium body, firm short asymmetrical bean, small short bristles and a single darker purple flat shadow. "
    "Readable silhouette, empty blank surface for face placement, no eyes, no hands, no feet. Solid pure white background."),
 'globule': ('1:1', [(35,89,110),(114,191,202),(199,236,229),(255,244,212),(255,255,255)],
    "One isolated simplified white blood cell body, irregular rounded amoeboid silhouette with broad shallow organic lobes. "
    "Ivory fill and a light turquoise rim, dark outline, flat stylized pastel colors, blank center for face later, no face, no limbs. Centered on plain white background."),
}

def main():
    for name,(ratio,colors,prompt) in ITEMS.items():
        try:
            print(recraft.generate(prompt+' '+STYLE, ART/name, size=ratio, colors=colors), flush=True)
        except RuntimeError as error:
            print(name, error, flush=True)

if __name__ == '__main__':
    main()
