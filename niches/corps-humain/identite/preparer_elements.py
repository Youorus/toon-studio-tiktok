"""Export du kit de série à partir du casting et du rendu approuvés."""
from pathlib import Path
from shutil import copy2, copytree, make_archive
import subprocess
import sys
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image, ImageDraw

from toonstudio import cards, rig
from toonstudio.config import FPS, H, W
from toonstudio.drawing import font

IDENTITY = Path(__file__).resolve().parent
NICHE = IDENTITY.parent
EPISODE = NICHE / 'episodes' / '006-antibioresistance'
ORIGINAL = EPISODE / 'out' / 'La-bacterie-qui-na-pas-bouge.mp4'
sys.path.insert(0, str(EPISODE))
from produire import Antibiotiques

CORAL = np.array([231, 82, 97])
PINK, WINE, CREAM = '#E8AABA', '#6D383B', '#FFF9ED'
# Images source inclusives/exclusives. Garder les prises à leur vitesse d’origine.
EXCERPT = ((0, 66, 1), (167, 217, 1.13), (364, 553, 1.04))


def anatomy_grade(image, base, strength, face=None):
    """Renforce le premier plan rouge à la composition, en préservant les tons de fond."""
    pixels = np.asarray(image).copy()
    rgb = pixels[:, :, :3].astype(np.float32)
    difference = np.abs(rgb - base).max(axis=2)
    weight = np.clip((49 - difference) / 40, 0, 1)
    if face is not None:
        # Le raccord du visage animé doit garder la teinte de son calque de peau.
        x, y = face
        yy, xx = np.ogrid[:H, :W]
        distance = np.sqrt(((xx - x) / 155) ** 2 + ((yy - y) / 148) ** 2)
        weight *= np.clip((distance - 0.67) / 0.75, 0, 1)
    rgb += weight[..., None] * strength * (CORAL - base)
    pixels[:, :, :3] = rgb.round().clip(0, 255).astype(np.uint8)
    return Image.fromarray(pixels)


class Preview:
    def __init__(self):
        self.episode = Antibiotiques(EPISODE)
        ep = self.episode
        self.shots = {shot['id']: shot for shot in ep.shots}
        self.lines = {name: [line for line in ep.lines if line['shot'] == name] for name in self.shots}
        self.characters = {
            (shot['id'], name): rig.load(ep.path(actor['perso']))
            for shot in ep.shots for name, actor in shot['acteurs'].items()
        }
        ep._chars = {name: character for (_, name), character in self.characters.items()}
        self.cabinet = ep.cfg['plans'][-1]['decor']
        self.backgrounds = {
            path: Image.open(ep.path(path)).convert('RGBA')
            for path in ('decors/estomac.png', 'decors/plaie.png', self.cabinet)
        }
        self.backgrounds['decors/estomac.png'] = anatomy_grade(
            self.backgrounds['decors/estomac.png'], (250, 119, 125), .84, (821, 811))
        self.backgrounds['decors/plaie.png'] = anatomy_grade(
            self.backgrounds['decors/plaie.png'], (252, 111, 101), .70)

    def frame(self, shot_id, time, zoom=1, captions=False):
        ep = self.episode
        shot = self.shots[shot_id]
        lines = self.lines[shot_id]
        index = next(i for i, line in enumerate(lines) if line['t0'] <= time < line['t1'])
        line = lines[index]
        image = self.backgrounds[shot['decor']].copy()
        for actor in ep._place_actors(shot, lines, index, line, time, self.characters):
            image.alpha_composite(actor['img'], actor['pos'])
        if zoom > 1:
            w, h = W / zoom, H / zoom
            crop = ((W - w) / 2, (H - h) / 2 - 28, (W + w) / 2, (H + h) / 2 - 28)
            image = image.resize((W, H), Image.Resampling.LANCZOS, box=crop)
        if line.get('carte'):
            card = cards.draw(line['carte'], time - line['t0'], line['t1'] - line['t0'], ep.palette)
            image.alpha_composite(card, ((W - card.width) // 2, 430 - card.height // 2))
        if captions:
            ep._caption(image, line, time)
            ep._watermark(image, time)
        elif shot_id in ep.organ_badges:
            image.alpha_composite(ep.organ_badges[shot_id], ep.badge_xy)
        return image


def export_pack(preview, root):
    for name in ('decors', 'habillage', 'personnages'):
        (root / name).mkdir(parents=True, exist_ok=True)
    for path, image in preview.backgrounds.items():
        image.save(root / path)
    for name in ('docteure-aplats', 'lea-aplats', 'estomac', 'peau', 'gelule', 'bacterie', 'resistante', 'globule'):
        copytree(preview.episode.path(f'personnages/{name}'), root / 'personnages' / name)
    for actor, gaze in (('docteure', (.8, .5)), ('lea', (-.85, -.5))):
        pose, _ = preview.characters[('au-cabinet', actor)].render(gaze=gaze)
        pose.crop(pose.getbbox()).save(root / 'personnages' / f'{actor}-aplats' / 'pose-consultation.png')
    for organ in ('estomac', 'peau'):
        cards.organ_badge(organ).save(root / 'habillage' / f'badge-{organ}.png')
    style = preview.episode.niche['direction_artistique']
    button = cards.draw(style['abonnement_final'], 0, 1, preview.episode.palette)
    button.crop(button.getbbox()).save(root / 'habillage' / 'abonne-toi.png')
    copy2(IDENTITY / 'photo-profil-ton-corps-explique.png', root / 'habillage')
    copy2(NICHE / 'niche.yaml', root)
    copytree(EPISODE / 'sons', root / 'sons')
    (root / 'LISEZ-MOI.md').write_text(
        '# Ton corps, expliqué\n\n'
        'Éléments réutilisables dérivés du casting Recraft et de l’épisode 006 de Toon Studio.\n\n'
        '- Décors verticaux de 1080 × 1920. Les visages animés de l’estomac et de la peau '
        'sont des calques séparés. Placer leur ancre respectivement à (821, 811) et (226, 657).\n'
        '- Casting en PNG transparent et rigs Toon Studio. Les fichiers pose-consultation.png ont les regards '
        'du plan de cabinet. Le cadre « Abonne-toi » fait partie du cabinet.\n'
        '- Badges et bouton en PNG transparent. Coordonnées de référence et timbres dans niche.yaml.\n'
        '- Bruitages courts en WAV. Le kit contient les références de voix pour Toon Studio.\n',
        encoding='utf-8')
    make_archive(str(IDENTITY / 'elements-ton-corps-explique'), 'zip', root.parent, root.name)


def export_board(preview):
    sheet = Image.new('RGB', (1200, 944), '#211C20')
    d = ImageDraw.Draw(sheet)
    d.text((36, 29), 'Ton corps, expliqué', font=font('Fredoka', 47), fill=CREAM)
    d.text((39, 89), 'Éléments de la série   /   @toncorps.explique', font=font('Fredoka', 23), fill='#E8AABA')
    examples = (
        ('la-vieille-boite', 6.2, 'Estomac', 'Fond rosé et relief corail'),
        ('la-breche', 32.5, 'Peau', 'Coupe du genou et microbes'),
        ('au-cabinet', 97.4, 'Cabinet', 'Docteure, Léa et abonnement'),
    )
    for i, (shot, time, title, note) in enumerate(examples):
        x = 36 + i * 382
        frame = preview.frame(shot, time).convert('RGB').resize((360, 640), Image.Resampling.LANCZOS)
        sheet.paste(frame, (x, 135))
        d.text((x, 788), title, font=font('Fredoka', 32), fill=CREAM)
        d.text((x, 832), note, font=font('Fredoka', 21), fill='#E8AABA')
    for i, (color, name) in enumerate(((PINK, 'Rose organique'), ('#E75261', 'Corail vif'), (WINE, 'Bordeaux'))):
        x = 37 + i * 232
        d.rounded_rectangle((x, 885, x + 32, 917), radius=7, fill=color)
        d.text((x + 42, 886), name, font=font('Fredoka', 20), fill=CREAM)
    sheet.save(IDENTITY / 'planche-elements-ton-corps-explique.jpg', quality=94, subsampling=0)


def export_excerpt(preview, temp):
    video = temp / 'images.mp4'
    command = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
               '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264',
               '-crf', '17', '-pix_fmt', 'yuv420p', str(video)]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
        for start, end, zoom in EXCERPT:
            for number in range(start, end):
                frame = preview.frame('la-vieille-boite', number / FPS, zoom, captions=True)
                encoder.stdin.write(frame.convert('RGB').tobytes())
        encoder.stdin.close()
        if encoder.wait():
            raise RuntimeError('Encodage des images interrompu.')
    filters = []
    for i, (start, end, _) in enumerate(EXCERPT):
        length = (end - start) / FPS
        filters.append(f'[1:a]atrim=start={start / FPS:.6f}:end={end / FPS:.6f},asetpts=PTS-STARTPTS,'
                       f'afade=d=0.016,afade=t=out:st={length - 0.022:.6f}:d=0.022[a{i}]')
    filters.append(''.join(f'[a{i}]' for i in range(len(EXCERPT))) + f'concat=n={len(EXCERPT)}:v=0:a=1[mix]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(video), '-i', str(ORIGINAL),
                    '-filter_complex', ';'.join(filters), '-map', '0:v', '-map', '[mix]',
                    '-c:v', 'copy', '-c:a', 'aac', '-ar', '48000', '-b:a', '192k',
                    '-movflags', '+faststart', str(IDENTITY / 'extrait-ton-corps-explique.mp4')], check=True)


if __name__ == '__main__':
    preview = Preview()
    with TemporaryDirectory() as folder:
        temp = Path(folder)
        export_pack(preview, temp / 'ton-corps-explique')
        export_board(preview)
        export_excerpt(preview, temp)
