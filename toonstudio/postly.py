"""Sauvegarder les épisodes dans CAlabs Studio, sans programmer de publication."""
from __future__ import annotations

from argparse import ArgumentParser
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import tarfile
from uuid import NAMESPACE_URL, uuid5
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import yaml

from .config import ROOT
from .production import check_publication, digest, verify

CONFIG=ROOT/'integrations'/'postly'/'config.json'


def item(path, ident, label, kind, episode):
    return {'id':ident,'label':label,'kind':kind,'filename':path.name,
            'path':f'episodes/{episode}/{ident}/{path.name}',
            'size_bytes':path.stat().st_size,'sha256':digest(path)}


def pilot_archive(out):
    """Fichiers existants des épisodes pilotes ; ces essais ne sont pas des fiches prêtes à poster."""
    archive=out/'archives-pilotes-001-005.zip'
    files=[f for p in (ROOT/'niches/corps-humain/episodes').iterdir()
           if p.name[:3] in {'001','002','003','004','005'}
           for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.name!='.DS_Store']
    with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=2) as z:
        manifest={}
        for f in sorted(files):
            rel=f.relative_to(ROOT).as_posix();z.write(f,rel);manifest[rel]=digest(f)
        info=ZipInfo('INVENTAIRE.json',(1980,1,1,0,0,0));info.compress_type=ZIP_DEFLATED
        z.writestr(info,json.dumps({'contenu':'Fichiers locaux des épisodes pilotes, avec essais et animatique. Consulter les épisodes 006 à 009 pour le style de série actuel.','fichiers':manifest},ensure_ascii=False,indent=2))
    return archive


def prepare(folders=None):
    config=json.loads(CONFIG.read_text())
    account=config['account'];account_id=uuid5(NAMESPACE_URL,'https://www.tiktok.com/@'+account['handle'].lstrip('@'))
    account={**account,'id':str(account_id)}
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out=ROOT/'integrations/postly/out'/stamp;out.mkdir(parents=True,exist_ok=False)
    folders=folders or sorted(p.parent for p in (ROOT/'niches/corps-humain/episodes').glob('*/recu-livraison.json'))
    bundle={'schema':'postly-local-studio-v1','account':account,'source_repository':config['source_repository'],'episodes':[]}
    mapping={}
    for folder in folders:
        folder=folder.resolve();check_publication(folder)
        receipt=json.loads((folder/'recu-livraison.json').read_text())
        master=folder/'out'/receipt['master'];archive=ROOT/'archives-production/corps-humain'/receipt['archive']
        if digest(master)!=receipt['sha256_master'] or digest(archive)!=receipt['sha256_archive']:
            raise ValueError('Master ou ZIP différent du reçu : '+folder.name)
        manifest=verify(archive)
        if manifest['sha256_master']!=receipt['sha256_master']:
            raise ValueError('Archive ne correspondant pas au master')
        proof=archive.with_name(archive.stem+'-contestation')
        publication=(folder/'publication-tiktok.txt').read_text().strip()
        tags=re.findall(r'(?<!\S)#[\w]+',publication)
        description=re.sub(r'(?<!\S)#[\w]+','',publication).strip()
        if '#Santé' not in tags or len(tags)>5:
            raise ValueError('Inclure #Santé et au plus cinq hashtags : '+folder.name)
        cfg=yaml.safe_load((folder/'episode.yaml').read_text())
        script='\n'.join(line['dit'] for shot in cfg['plans'] for line in shot['repliques'])
        episode={'episode':folder.name,'id':str(uuid5(account_id,folder.name+'@'+receipt['sha256_master'])),
                 'title':cfg['titre'],'profile':receipt['profil'],'description':description,
                 'hashtags':tags,'script':script,'files':[]}
        sources=[(master,'master','Vidéo finale','master'),(folder/'out/sous-titres.srt','subtitles','Sous-titres','subtitles'),
                 (archive,'sources','Sources complètes de cette version','sources'),
                 (folder/'publication-tiktok.txt','publication','Description et hashtags','publication'),
                 (proof/'01-calques-et-rendu.jpg','proof-calques','Calques et rendu','proof'),
                 (proof/'02-reperes-de-montage.jpg','proof-montage','Repères de montage','proof'),
                 (proof/'texte-contestation.txt','appeal','Texte de contestation à compléter','appeal'),
                 (folder/'provenance.md','provenance','Provenance et choix de fabrication','project')]
        sources.extend((ROOT/'docs'/name,ident,label,'project') for name,ident,label in (
            ('SCENARIOS-RETENTION.md','editorial-guide','Scénarios et objectif 10 000 abonnés'),
            ('MASTER-PROMPT-TIKTOK.md','editorial-master','Master prompt éditorial de Marc')))
        # Garder aussi toutes les archives des révisions déjà livrées.
        for prior in sorted(archive.parent.glob(folder.name+'-*.zip')):
            if prior!=archive:
                verify(prior)
                key='revision-'+prior.stem.rsplit('-',1)[-1]
                sources.append((prior,key,'Sources — révision '+key[9:],'sources'))
        if folder.name.startswith('006-'):
            sources.append((pilot_archive(out),'pilotes','Archives des épisodes pilotes 001–005','sources'))
        for path,ident,label,kind in sources:
            record=item(path,ident,label,kind,folder.name);episode['files'].append(record);mapping[record['path']]=path
        delivery=out/(folder.name+'-livraison.json')
        delivery.write_text(json.dumps({**episode,'source_repository':bundle['source_repository']},ensure_ascii=False,indent=2)+'\n')
        record=item(delivery,'manifest','Inventaire et empreintes de livraison','manifest',folder.name);episode['files'].append(record);mapping[record['path']]=delivery
        bundle['episodes'].append(episode)
    manifest_path=out/'manifest.json';manifest_path.write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
    return config,manifest_path,mapping


def send(config, manifest, mapping):
    ssh=['ssh','-i',str(Path(config['ssh_key']).expanduser()),'-o','BatchMode=yes','-o','ConnectTimeout=20',config['ssh_host']]
    stage=config['staging_root']+'/'+manifest.parent.name
    # Les paramètres de destination sont des constantes contrôlées, jamais du texte utilisateur.
    for val in (config['container'],stage):
        if not re.fullmatch(r'[A-Za-z0-9_./-]+',val) or '..' in val.split('/'):
            raise ValueError('Destination SSH invalide')
    remote=f"docker exec -i {config['container']} sh -c 'mkdir -p {stage} && tar -xf - -C {stage}'"
    process=subprocess.Popen(ssh+[remote],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        with tarfile.open(fileobj=process.stdin,mode='w|') as tar:
            tar.add(manifest,arcname='manifest.json',recursive=False)
            for rel,path in mapping.items():tar.add(path,arcname=rel,recursive=False)
        process.stdin.close();process.stdin=None
        _,errors=process.communicate()
        if process.returncode:raise RuntimeError('Le transfert SSH a échoué ; le lot local est conservé.')
    except Exception:
        process.kill();process.wait();raise
    command=f"docker exec {config['container']} python -m scripts.import_local_studio {stage}/manifest.json --apply"
    result=subprocess.run(ssh+[command],capture_output=True,text=True)
    if result.returncode:
        (manifest.parent/'import-error.log').write_text(result.stderr)
        raise RuntimeError('Import interrompu ; voir import-error.log. Le lot et ses sources sont conservés.')
    receipt=json.loads(result.stdout.strip().splitlines()[-1])
    receipt['studio_url']=config['studio_url']
    (manifest.parent/'recu-postly.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    for episode in receipt['episodes']:
        folder=ROOT/'niches/corps-humain/episodes'/episode['episode']
        (folder/'recu-postly.json').write_text(json.dumps({**episode,'account_id':receipt['account_id'],
            'url':config['studio_url']+episode['path'],'buffer_sent':False},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(receipt,ensure_ascii=False,indent=2),flush=True)
    # Seulement le lot de transit créé par cet envoi ; le stockage objet a été relu avant le reçu.
    cleanup=f"docker exec {config['container']} rm -rf {stage}"
    done=subprocess.run(ssh+[cleanup],capture_output=True,text=True)
    if done.returncode:print('Import vérifié ; le dossier de transit reste à nettoyer sur le serveur.')


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('episode',nargs='*',type=Path)
    parser.add_argument('--envoyer',action='store_true')
    args=parser.parse_args()
    config,manifest,mapping=prepare(args.episode or None)
    print(str(manifest),flush=True)
    print(f'{len(mapping)} fichiers · {sum(p.stat().st_size for p in mapping.values())/1024**2:.1f} Mio',flush=True)
    if args.envoyer:send(config,manifest,mapping)


if __name__=='__main__':main()
