"""Montage court à partir de l'épisode 006 et de ses prises françaises validées."""
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image
from scipy.ndimage import binary_propagation

from preparer_art import art
from toonstudio.config import FPS, H, SFX, W
from toonstudio.drawing import cover
from toonstudio.sous_titres import srt_time

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'out'
ORIGINAL = OUT / 'La-bacterie-qui-na-pas-bouge.mp4'
FINAL = OUT / 'La-bacterie-qui-na-pas-bouge-TikTok.mp4'
sys.path.insert(0, str(ROOT.parents[1] / 'identite'))
from preparer_elements import Preview


@dataclass(frozen=True)
class Cut:
    shot: str
    start: float
    stop: float
    tempo: float = 1
    zoom: float = 1

    @property
    def frames(self):
        return round((self.stop - self.start) / self.tempo * FPS)

    @property
    def duration(self):
        return self.frames / FPS

    @property
    def rate(self):
        return (self.stop - self.start) / self.duration


CUTS = (
    Cut('la-vieille-boite', 0, 7.24, 1.11),
    Cut('la-vieille-boite', 10.37, 18.54, 1.09, 1.075),
    Cut('la-breche', 20.30, 33.76, 1.13),
    Cut('cette-fois', 40.41, 46.68, 1.05, 1.055),
    Cut('celles-qui-restent', 46.83, 61.03, 1.12),
    Cut('au-cabinet', 67.06, 80.19, 1.05),
    Cut('au-cabinet', 88.96, 91.00, 1, 1.05),
    Cut('au-cabinet', 94.50, 99.70, 1.07),
)
TOTAL = sum(cut.frames for cut in CUTS) / FPS


def apply_coral_background(image, source, regions):
    original = np.asarray(cover(source))[:, :, :3].astype(np.int16)
    result = np.array(image)
    for rows, source_color, current_color in regions:
        zone = original[rows]
        distance = np.abs(zone - source_color).max(axis=2)
        candidates = distance <= 24
        edges = np.zeros(candidates.shape, dtype=bool)
        edges[:, [0, -1]] = True
        edges[[0, -1], :] = True
        selected = binary_propagation(edges & candidates, mask=candidates)
        weight = (selected * np.clip((24 - distance) / 17, 0, 1))[..., None]
        delta = np.array([231, 82, 97]) - current_color
        result[rows, :, :3] = np.rint(result[rows, :, :3] + weight * delta).clip(0, 255).astype(np.uint8)
    return Image.fromarray(result)


def short_preview():
    preview = Preview()
    for name, source, regions in (
        ('estomac', 'estomac', [(slice(None), (251, 220, 176), (232, 170, 186))]),
        ('plaie', 'plaie-b', [(slice(0, 438), (251, 227, 200), (244, 203, 199)),
                              (slice(1100, None), (250, 172, 131), (230, 164, 164))]),
    ):
        rel = f'decors/{name}.png'
        preview.backgrounds[rel] = apply_coral_background(preview.backgrounds[rel], art(source), regions)
    return preview


def edit_decisions(preview):
    cursor = 0
    timing, subtitles = [], []
    for cut in CUTS:
        start = cursor / FPS
        timing.append(dict(plan=cut.shot, source_debut=cut.start, source_fin=cut.stop, image_debut=cursor,
                           images=cut.frames, facteur_lecture=cut.rate, zoom=cut.zoom))
        for cue in preview.episode.cues:
            if cue['debut'] >= cut.stop or cue['fin'] <= cut.start:
                continue
            if cue['debut'] < cut.start - .035 or cue['fin'] > cut.stop + .035:
                raise ValueError(f'Coupure au milieu du sous-titre {cue["texte"]}')
            subtitles.append({**cue,
                              'debut': round(start + (max(cue['debut'], cut.start) - cut.start) / cut.rate, 3),
                              'fin': round(start + (min(cue['fin'], cut.stop) - cut.start) / cut.rate, 3)})
        cursor += cut.frames
    assert all(cue['debut'] < cue['fin'] for cue in subtitles)
    assert all(a['fin'] <= b['debut'] for a, b in zip(subtitles, subtitles[1:]))
    return timing, subtitles


def render_pictures(preview, target):
    command = ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
               '-s', f'{W}x{H}', '-r', str(FPS), '-i', 'pipe:0',
               '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
               '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
               '-c:v', 'libx264', '-crf', '16', str(target)]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
        for cut in CUTS:
            print(f'{cut.shot} · {cut.duration:.2f} s', flush=True)
            shot = preview.shots[cut.shot]
            for frame_number in range(cut.frames):
                source_time = min(cut.start + frame_number / FPS * cut.rate, shot['t1'] - 1e-5)
                picture = preview.frame(cut.shot, source_time, cut.zoom, captions=True)
                encoder.stdin.write(picture.convert('RGB').tobytes())
        encoder.stdin.close()
        if encoder.wait():
            raise RuntimeError('Échec de l’encodage vidéo')


def mux_audio(pictures, target):
    filters = []
    for i, cut in enumerate(CUTS):
        d = cut.duration
        filters.append(f'[1:a]atrim=start={cut.start}:end={cut.stop},asetpts=PTS-STARTPTS,'
                       f'aresample=48000,aformat=channel_layouts=stereo,atempo={cut.rate:.8f},'
                       f'apad,atrim=0:{d:.8f},afade=d=0.012,afade=t=out:st={d - .027:.8f}:d=0.027[c{i}]')
    filters.append(''.join(f'[c{i}]' for i in range(len(CUTS))) + f'concat=n={len(CUTS)}:v=0:a=1[dialogue]')
    # Un petit impact marque la coupe sur le genou, avant la première syllabe.
    scratch_ms = round(sum(cut.duration for cut in CUTS[:2]) * 1000)
    filters.extend([
        f'[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:0.16,'
        f'afade=t=out:st=0.07:d=0.09,volume=0.16,adelay={scratch_ms}:all=1[impact]',
        '[dialogue][impact]amix=inputs=2:duration=first:normalize=0,'
        'alimiter=limit=0.84:level=false:latency=true[mix]',
    ])
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', str(pictures), '-i', str(ORIGINAL),
                    '-i', str(SFX / 'pop.mp3'), '-filter_complex', ';'.join(filters),
                    '-map', '0:v', '-map', '[mix]', '-c:v', 'copy', '-c:a', 'aac', '-ar', '48000', '-b:a', '192k',
                    '-movflags', '+faststart', str(target)], check=True)


def main():
    assert 61 <= TOTAL <= 65, TOTAL
    preview = short_preview()
    timing, subtitles = edit_decisions(preview)
    with TemporaryDirectory() as directory:
        pictures = Path(directory) / 'images.mp4'
        render_pictures(preview, pictures)
        mux_audio(pictures, FINAL)
    srt = '\n\n'.join(f"{i}\n{srt_time(cue['debut'])} --> {srt_time(cue['fin'])}\n{cue['texte']}"
                      for i, cue in enumerate(subtitles, 1))
    FINAL.with_suffix('.srt').write_text(srt + '\n', encoding='utf-8')
    FINAL.with_suffix('.json').write_text(json.dumps(
        {'images_par_seconde': FPS, 'duree_s': TOTAL, 'source': ORIGINAL.name, 'coupes': timing,
         'sous_titres': subtitles}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{TOTAL:.2f} s · {len(subtitles)} sous-titres · {FINAL.name}', flush=True)


if __name__ == '__main__':
    main()
