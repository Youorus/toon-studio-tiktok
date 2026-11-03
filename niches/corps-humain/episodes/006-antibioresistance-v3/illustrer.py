"""Nouveaux actifs de la séquence de la brèche dans la charte Le Corps Parle.fr."""
from pathlib import Path
from toonstudio import recraft

ROOT = Path(__file__).resolve().parent
NICHE = ROOT.parents[1]
ART = ROOT / 'art'
STYLE = (
    "Simple clean flat 2D cel cartoon, thick confident very dark outlines, warm solid flat paints with one "
    "simple shadow per surface, distinct shapes, minimal visual detail, original character design, no texture, no text. "
)

if __name__ == '__main__':
    recraft.generate(
        STYLE + "Full-body friendly cartoon skin security police officer, short round chunky silhouette, looking to the right in "
        "three quarter view, large flat uninterrupted medium brown face with NO eyes NO eyebrows NO mouth NO nose NO facial hair "
        "so the face can be animated later, dark petrol-blue rounded service cap with a single small gold shape, pale petrol-blue "
        "police shirt with dark lapels, dark trousers and big simple boots, both arms down by sides and hands visible, standing, "
        "one character on a pure solid white background, whole body with generous margin, no props.",
        ART/'policier', model='recraftv4_1', size='3:4',
        colors=[(24,19,19),(38,102,109),(117,171,187),(181,127,97),(238,180,79),(255,255,255)],seed=1741)
    print('Policier dessiné',flush=True)
    recraft.generate(
        STYLE + "Vertical 9:16 background, INSIDE a cutaway of human skin, cartoon anatomical stage for an action scene. "
        "Vivid uniform coral red #E75261 dominates, soft pink tissue folds, dark wine burgundy contour. "
        "Upper three quarters a smooth vertical wall of living skin tissue, a SINGLE clearly readable narrow jagged "
        "dark red vertical fissure at x=56 percent, starting halfway down the image and ending where wall meets floor at "
        "y=59 percent, like a breach through which a microbe can emerge. Clear horizontal flat coral tissue floor with "
        "gentle perspective occupying the lower 41 percent, empty playing space for three cartoon characters at x=24%, "
        "x=55%, x=77%. Calm upper third, simple shapes, separate foreground floor from the vertical tissue wall. "
        "No characters, no eyes, no words, no watermarks, no blood, no complicated texture, no tunnels.",
        ART/'breche', model='recraftv4_1', size='9:16',
        colors=[(231,82,97),(109,56,59),(199,119,121),(241,158,154),(246,138,139),(24,19,19)],seed=668)
    print('Décor de la brèche dessiné',flush=True)
