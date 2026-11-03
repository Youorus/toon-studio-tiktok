"""Rendu de l’épisode 004 avec la présentation de sous-titres de la série."""
from argparse import ArgumentParser
from pathlib import Path

from toonstudio.sous_titres import CaptionedEpisode

ROOT = Path(__file__).parent


def main():
    parser = ArgumentParser()
    parser.add_argument('--planche', action='store_true')
    args = parser.parse_args()
    episode = CaptionedEpisode(ROOT)
    out = ROOT / 'out'
    out.mkdir(exist_ok=True)
    episode.save_subtitles(out)
    print(f'{episode.duration:.2f} s · {len(episode.lines)} prises · {len(episode.cues)} sous-titres', flush=True)
    if args.planche:
        episode.preview(out, [0.6, 2.8, 7.1, 11.1, 15.2, 17.3, 19.8, 23.5, 30.6, 37.9, 49.7, 60.8])
    else:
        problems = episode.controle(out)
        if problems:
            raise SystemExit('\n'.join(problems))
        episode.render(out / 'Il-bouge-mais-il-navance-pas.mp4', preview_every=150)


if __name__ == '__main__':
    main()
