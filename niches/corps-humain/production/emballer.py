"""Prépare les décors corail et assemble le kit à partir des actifs validés."""
from pathlib import Path
from shutil import copy2, copytree, ignore_patterns, make_archive
import sys
from tempfile import TemporaryDirectory

from toonstudio import cards

HERE = Path(__file__).resolve().parent
NICHE = HERE.parent
STUDIO = NICHE.parents[1]
EPISODE = NICHE / 'episodes' / '006-antibioresistance'
sys.path.insert(0, str(EPISODE))
from produire_tiktok import short_preview

IGNORE = ignore_patterns('__pycache__', '.DS_Store', 'out', 'apercu.jpg', 'emballer.py')
ANATOMY = ('estomac', 'peau')


def main():
    preview = short_preview()
    for organ in ANATOMY:
        preview.backgrounds['decors/' + ('plaie' if organ == 'peau' else organ) + '.png'].save(
            NICHE / 'decors' / f'{organ}-corail.png')
    with TemporaryDirectory() as folder:
        root = Path(folder) / 'le-corps-parle-fr'
        packaged = root / 'niches' / 'corps-humain'
        packaged.mkdir(parents=True)
        copytree(STUDIO / 'toonstudio', root / 'toonstudio', ignore=IGNORE)
        copytree(STUDIO / 'shared', root / 'shared', ignore=IGNORE)
        copy2(STUDIO / 'requirements.txt', root)
        copy2(HERE / 'LISEZ-MOI.md', root)
        (root / 'docs').mkdir()
        copy2(STUDIO / 'docs' / 'DIRECTION-ARTISTIQUE.md', root / 'docs')
        for name in ('kit.yaml', 'niche.yaml'):
            copy2(NICHE / name, packaged)
        copytree(HERE, packaged / 'production', ignore=IGNORE)
        copytree(NICHE / 'personnages', packaged / 'personnages',
                 ignore=ignore_patterns('__pycache__', '.DS_Store', 'apercu.jpg',
                                        'docteure', 'docteur', 'patient', 'patiente'))
        reference = packaged / 'episodes' / EPISODE.name
        reference.mkdir(parents=True)
        for name in ('personnages', 'sons'):
            copytree(EPISODE / name, reference / name, ignore=IGNORE)
        copytree(EPISODE / 'relecture', reference / 'relecture', ignore=IGNORE)
        (packaged / 'decors').mkdir()
        for name in ('estomac-corail.png', 'peau-corail.png', 'cabinet-abonne-toi.png'):
            copy2(NICHE / 'decors' / name, packaged / 'decors')
        identity = packaged / 'identite'
        identity.mkdir()
        copy2(NICHE / 'identite' / 'photo-profil-ton-corps-explique.png', identity / 'photo-profil-le-corps-parle-fr.png')
        copy2(NICHE / 'identite' / 'comparatif-fond-corail.jpg', identity)
        casting = packaged / 'maquettes' / 'casting-aplats'
        casting.mkdir(parents=True)
        for name in ('casting.jpg', 'docteure.png', 'lea.png'):
            copy2(NICHE / 'maquettes' / 'casting-aplats' / name, casting)
        cards.actor_badge('Le Corps Parle.fr', '#6D383B', '#E75261').save(identity / 'badge-le-corps-parle-fr.png')
        for organ in ANATOMY:
            cards.organ_badge(organ).save(identity / f'badge-{organ}.png')
        cta = cards.draw(preview.episode.niche['direction_artistique']['abonnement_final'], 0, 1, preview.episode.palette)
        cta.crop(cta.getbbox()).save(identity / 'abonne-toi.png')
        for text, color, dot, name in (
            ('Antibiotique', '#1E4352', '#91D3DF', 'antibiotique'),
            ('Bactérie', '#503467', '#D4A5ED', 'bacterie'),
            ('Bactéries', '#2C4E37', '#8FF194', 'bacteries'),
            ('Bactérie\nrésistante', '#503467', '#D4A5ED', 'bacterie-resistante'),
            ('Globule blanc', '#285259', '#E9F9EB', 'globule-blanc'),
        ):
            cards.actor_badge(text, color, dot).save(identity / f'mini-badge-{name}.png')
        print(make_archive(str(NICHE / 'identite' / 'kit-production-le-corps-parle-fr'), 'zip', root.parent, root.name))


if __name__ == '__main__':
    main()
