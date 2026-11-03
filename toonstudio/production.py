"""Vérifie la charte de série et archive les sources d'un épisode livré."""
from argparse import ArgumentParser
from hashlib import file_digest
import json
from pathlib import Path
from shutil import copy2, copytree, ignore_patterns
import subprocess
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZIP_DEFLATED, ZipFile

import yaml

from . import voice
from .config import ROOT
from .episode import Episode

PROFILE='profil-verrou.json'
IGNORE=ignore_patterns('out','__pycache__','.DS_Store','*.pyc','apercu.jpg','recu-livraison.json')
SOURCES=('requirements.txt','toonstudio','shared')


def digest(path):
    with path.open('rb') as stream:
        return file_digest(stream,'sha256').hexdigest()


def write_json(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n')


def freeze(niche,create=False):
    base=ROOT/'niches'/niche
    config=yaml.safe_load((base/'niche.yaml').read_text())['direction_artistique']
    lock=base/PROFILE
    if create:
        ref=base/config['episode_reference']
        paths=[base/'niche.yaml',base/'kit.yaml',base/config['cabinet'],
               ROOT/'docs'/'DIRECTION-ARTISTIQUE.md',base/'decors'/'estomac-corail.png',
               base/'decors'/'peau-corail.png',ref/'produire.py',ref/'preparer.py']
        for cast in config['casting'].values():
            rig=base/'personnages'/cast['rig']
            paths.extend(rig.glob('*.png'))
            paths.append(rig/'personnage.yaml')
        paths.extend(p for p in (ref/'personnages'/'policier-comique').iterdir() if p.is_file())
        paths.extend((ROOT/'shared'/'fonts').glob('*.ttf'))
        paths.extend(ROOT/'toonstudio'/f'{module}.py' for module in
                     ('episode','sous_titres','rig','face','cards','drawing','musique_cartoon'))
        if lock.exists() and json.loads(lock.read_text())['version']==config['version']:
            raise ValueError('Une révision de la charte exige un nouvel identifiant de version.')
        files={p.relative_to(ROOT).as_posix():digest(p) for p in sorted(paths)}
        write_json(lock,{'version':config['version'],'files':files})
    locked=json.loads(lock.read_text())
    differences=[path for path,h in locked['files'].items() if not (ROOT/path).is_file() or digest(ROOT/path)!=h]
    if differences or locked['version']!=config['version']:
        raise ValueError('Dérive du profil '+locked['version']+' : '+', '.join(differences))
    return locked


def copy_project_path(path,root):
    target=root/path.relative_to(ROOT)
    target.parent.mkdir(parents=True,exist_ok=True)
    if path.is_dir():
        copytree(path,target,ignore=IGNORE,dirs_exist_ok=True)
    else:
        copy2(path,target)


def take_sources(folder,target):
    target.mkdir()
    takes={}
    tts=voice.tts

    def capture(archetype,text,stability=None,seed=7):
        key=voice.take_key(archetype,text,stability,seed)
        result=tts(archetype,text,stability,seed)
        audio=f'{key}.mp3'
        align=f'{key}.json'
        if key not in takes:
            copy2(result['audio'],target/audio)
            write_json(target/align,result['alignment'])
            takes[key]={'audio':audio,'alignement':align,'profil':archetype,'texte_dirige':text}
        return result

    with patch.object(voice,'tts',capture), patch.object(voice.requests,'post',
            side_effect=RuntimeError('La prise doit être déjà enregistrée pour être archivée.')):
        episode=Episode(folder)
    write_json(target/'index.json',takes)
    return len(episode.lines),len(takes)


def mux_audio(source,target):
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(source),'-vn','-map','0:a:0',
                    '-c','copy',str(target)],check=True)


def archive(folder,master,dry,dependencies):
    folder=folder.resolve()
    niche_dir=folder.parents[1]
    if folder.parent.name!='episodes' or niche_dir.parent!=ROOT/'niches':
        raise ValueError('Épisode attendu dans niches/<niche>/episodes/.')
    if not (folder/'provenance.md').is_file():
        raise ValueError('Renseigner provenance.md avant l’archivage.')
    profile=freeze(niche_dir.name)
    destination=ROOT/'archives-production'/niche_dir.name
    destination.mkdir(parents=True,exist_ok=True)
    out=destination/f'{folder.name}-{digest(master)[:12]}.zip'
    with TemporaryDirectory(dir=destination) as tmp:
        root=Path(tmp)/'projet'
        root.mkdir()
        for path in (*[ROOT/item for item in SOURCES],folder,niche_dir/'niche.yaml',niche_dir/'kit.yaml',
                     niche_dir/PROFILE,niche_dir/'personnages',niche_dir/'decors',ROOT/'docs'/'DIRECTION-ARTISTIQUE.md'):
            copy_project_path(path,root)
        for item in dependencies:
            dep=niche_dir/'episodes'/item
            if dep.parent!=niche_dir/'episodes' or not dep.is_dir():
                raise ValueError(f'Dépendance d’épisode inconnue : {item}')
            copy_project_path(dep,root)
        for path in profile['files']:
            if not (root/path).exists():
                copy_project_path(ROOT/path,root)
        for shot in (folder/'out').glob('*.jpg'):
            if shot.name in {'controle.jpg','controle-policier.jpg','planche-travail.jpg','controle-livraison.jpg'}:
                copy_project_path(shot,root)
        for name in ('sous-titres.srt','sous-titres.json','montage.json','controle.txt','controle-musique.json',
                     'controle-policier.json','controle-livraison.json','petites-combines.wav'):
            path=folder/'out'/name
            if path.is_file():
                copy_project_path(path,root)
        lines,takes=take_sources(folder,root/'prises')
        deliver=root/'livraison'
        deliver.mkdir()
        copy2(master,deliver/master.name)
        mux_audio(master,deliver/'mix-final.m4a')
        mux_audio(dry,deliver/'voix-et-bruitages.m4a')
        (root/'LIRE-MOI.md').write_text(
            '# Sources de production\n\n'
            f'Voir les instructions dans `{folder.relative_to(ROOT)}/README.md`. '
            'Depuis ce dossier, installer les dépendances de requirements.txt, puis définir '
            '`TOON_PRISES_INDEX="$PWD/prises/index.json"` avant de rendre. '
            'Les fichiers audio et les alignements d’origine sont inclus. '
            'La reproduction de l’image et le remix sont possibles sans compte externe.\n')
        manifest={'episode':folder.name,'profil':profile['version'],'repliques':lines,'prises_uniques':takes,
                  'master':master.name,'sha256_master':digest(master),
                  'fichiers':{p.relative_to(root).as_posix():digest(p) for p in sorted(root.rglob('*')) if p.is_file()}}
        write_json(root/'MANIFESTE.json',manifest)
        temporary=Path(tmp)/out.name
        with ZipFile(temporary,'w',ZIP_DEFLATED,compresslevel=4) as zipped:
            for file in sorted(root.rglob('*')):
                if file.is_file():
                    zipped.write(file,file.relative_to(root))
        verify(temporary)
        temporary.replace(out)
    write_receipt(folder,out,manifest)
    return out


def write_receipt(folder,path,manifest):
    receipt={key:manifest[key] for key in ('episode','profil','master','sha256_master','prises_uniques')}
    receipt.update(archive=path.name,sha256_archive=digest(path),fichiers_verifies=len(manifest['fichiers']))
    write_json(folder/'recu-livraison.json',receipt)


def verify(path):
    with ZipFile(path) as zipped:
        manifest=json.loads(zipped.read('MANIFESTE.json'))
        expected=manifest['fichiers']
        if sorted(zipped.namelist())!=sorted(['MANIFESTE.json',*expected]):
            raise ValueError('Inventaire ZIP différent du manifeste.')
        for name,checksum in expected.items():
            with zipped.open(name) as source:
                if file_digest(source,'sha256').hexdigest()!=checksum:
                    raise ValueError(f'Empreinte incorrecte : {name}')
    return manifest


def main():
    parser=ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    style=sub.add_parser('style')
    style.add_argument('niche')
    style.add_argument('--figer',action='store_true')
    pack=sub.add_parser('archiver')
    pack.add_argument('episode',type=Path)
    pack.add_argument('--master',type=Path,required=True)
    pack.add_argument('--sec',type=Path,required=True)
    pack.add_argument('--dependance',action='append',default=[])
    check=sub.add_parser('verifier')
    check.add_argument('zip',type=Path)
    args=parser.parse_args()
    if args.command=='style':
        result=freeze(args.niche,args.figer)
        print(f"{result['version']} · {len(result['files'])} fichiers contrôlés.")
    elif args.command=='archiver':
        print(archive(args.episode,args.master,args.sec,args.dependance))
    else:
        result=verify(args.zip)
        print(f"{result['episode']} · {len(result['fichiers'])} empreintes · {result['prises_uniques']} prises.")


if __name__=='__main__':
    main()
