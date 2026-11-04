"""Catalogue daté, sauvegarde et préparation image par image des inspirations."""
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from uuid import NAMESPACE_URL, uuid5

from PIL import Image, ImageDraw

from .config import ROOT
from .postly import CONFIG, send
from .production import digest

NICHE=ROOT/'niches/corps-humain'
DOWNLOADS=NICHE/'downloads'
BASE=NICHE/'references'
CATALOG=BASE/'catalogue.json'
VIDEO_SUFFIXES={'.mp4','.mov','.mkv','.webm'}


def write_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


def probe(path):
    output=subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)],stderr=subprocess.PIPE)
    data=json.loads(output);v=next(s for s in data['streams'] if s['codec_type']=='video')
    n,d=(v.get('avg_frame_rate') or '0/1').split('/')
    return {'duration_seconds':float(data['format'].get('duration',0)),
            'width':int(v['width']),'height':int(v['height']),
            'frame_rate':float(n)/max(float(d),1),'frame_count':int(v['nb_frames']) if str(v.get('nb_frames','')).isdigit() else None,
            'has_audio':any(s['codec_type']=='audio' for s in data['streams']),'readable':True}


def indexer():
    BASE.mkdir(parents=True,exist_ok=True)
    old=json.loads(CATALOG.read_text()) if CATALOG.exists() else {'references':[]}
    previous={x['id']:x for x in old['references']}
    paths=sorted(p for p in DOWNLOADS.rglob('*') if p.is_file() and p.suffix.lower() in VIDEO_SUFFIXES)
    def inspect(path):
        rel=path.relative_to(DOWNLOADS).as_posix();folder=path.relative_to(DOWNLOADS).parts[0]
        date.fromisoformat(folder)
        sha=digest(path);rid='r-'+hashlib.sha256((rel+'\0'+sha).encode()).hexdigest()[:24]
        thumb=BASE/'out/miniatures'/f'{rid}.jpg';thumb.parent.mkdir(parents=True,exist_ok=True)
        cached=previous.get(rid)
        meta={k:cached[k] for k in ('duration_seconds','width','height','frame_rate','frame_count','has_audio','readable') if k in cached} if cached else {}
        if not meta:
            try:meta=probe(path)
            except (subprocess.CalledProcessError,StopIteration,KeyError,ValueError):
                meta={'duration_seconds':0,'width':0,'height':0,'frame_rate':0,'frame_count':None,'has_audio':False,'readable':False}
        if meta['readable'] and not thumb.exists():
            subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(min(1,meta['duration_seconds']/4)),
                '-i',str(path),'-frames:v','1','-vf','scale=216:-2','-q:v','3',str(thumb)],check=True,capture_output=True)
        match=re.search(r'(?<!\d)(\d{15,22})(?!\d)',path.stem)
        return {'id':rid,'folder':folder,'filename':path.name,'relative_path':rel,
            'title':path.stem.split('_',2)[-1],'source_video_id':match.group(1) if match else None,
            'sha256':sha,'size_bytes':path.stat().st_size,'local_present':True,**meta,
            'thumbnail_sha256':digest(thumb) if thumb.exists() else None,
            'thumbnail_size_bytes':thumb.stat().st_size if thumb.exists() else 0}
    with ThreadPoolExecutor(max_workers=6) as executor:
        found=list(executor.map(inspect,paths))
    current={r['id']:r for r in found}
    for rid,entry in previous.items():
        if rid not in current:current[rid]={**entry,'local_present':False}
    result={'schema':'le-corps-parle-references-v1','source_root':'niches/corps-humain/downloads',
        'updated_at':datetime.now(timezone.utc).isoformat(),
        'references':sorted(current.values(),key=lambda r:(r['folder'],r['filename']))}
    write_json(CATALOG,result)
    print(f"{len(found)} vidéos locales · {len(result['references'])} références conservées dans le catalogue.",flush=True)
    return result


def catalogue():
    return json.loads(CATALOG.read_text()) if CATALOG.exists() else indexer()


def resolve(folder,video=None):
    date.fromisoformat(folder)
    candidates=[r for r in catalogue()['references'] if r['folder']==folder]
    if video:
        candidates=[r for r in candidates if video==r['id'] or video==r.get('source_video_id') or video.casefold() in r['filename'].casefold()]
    if len(candidates)!=1:
        raise ValueError(f"{len(candidates)} vidéos correspondent. Préciser --video avec l'identifiant : "+
            json.dumps([{'id':r['id'],'video_id':r.get('source_video_id'),'titre':r['title']} for r in candidates],ensure_ascii=False))
    return candidates[0]


def restore(ref):
    config=json.loads(CONFIG.read_text());account=str(uuid5(NAMESPACE_URL,'https://www.tiktok.com/@'+config['account']['handle'].lstrip('@')))
    target=(DOWNLOADS/ref['relative_path']).resolve()
    if not target.is_relative_to(DOWNLOADS.resolve()):raise ValueError('Chemin de référence invalide')
    if target.exists():
        if digest(target)!=ref['sha256']:raise ValueError('Fichier local différent ; ne pas le remplacer silencieusement')
        return target
    target.parent.mkdir(parents=True,exist_ok=True);temporary=target.with_suffix(target.suffix+'.part')
    command=f"docker exec {config['container']} python -m scripts.import_studio_references --account {account} --export {ref['id']}"
    with temporary.open('wb') as output:
        result=subprocess.run(['ssh','-i',str(Path(config['ssh_key']).expanduser()),'-o','BatchMode=yes',config['ssh_host'],command],stdout=output,stderr=subprocess.PIPE)
    if result.returncode or digest(temporary)!=ref['sha256']:
        temporary.unlink(missing_ok=True);raise RuntimeError('Restauration non vérifiée ; original local préservé')
    temporary.replace(target);print('Référence restaurée et SHA-256 vérifié : '+str(target),flush=True)
    return target


def preparer(ref,overview_only=False):
    source=DOWNLOADS/ref['relative_path']
    if not source.is_file():raise FileNotFoundError('Référence absente localement : lancer restaurer '+ref['folder']+' --video '+ref['id'])
    if digest(source)!=ref['sha256']:raise ValueError('La vidéo a changé : réindexer avant analyse')
    out=BASE/'analyses'/ref['id'];out.mkdir(parents=True,exist_ok=True)
    metadata=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames',
        '-show_entries','frame=best_effort_timestamp_time,pkt_duration_time,key_frame,pict_type','-of','json',str(source)],stderr=subprocess.PIPE)
    frames=[{'index':i+1,'fichier':f'images/{i+1:06d}.jpg',**entry} for i,entry in enumerate(json.loads(metadata)['frames'])]
    write_json(out/'images-et-temps.json',frames)
    streams=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(source)],stderr=subprocess.PIPE))
    write_json(out/'caracteristiques-source.json',streams)
    if not overview_only:
        images=out/'images';images.mkdir(exist_ok=True)
        if len(list(images.glob('*.jpg')))!=len(frames):
            subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',str(source),'-map','0:v:0',
                '-fps_mode','passthrough','-q:v','3',str(images/'%06d.jpg')],check=True)
    if ref['has_audio'] and not (out/'audio-reference.wav').exists():
        subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(source),'-vn','-ac','2','-ar','48000','-c:a','pcm_s16le',str(out/'audio-reference.wav')],check=True)
    overviews=out/'apercus';overviews.mkdir(exist_ok=True)
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',str(source),'-vf','fps=1,scale=216:-2','-q:v','3',str(overviews/'%04d.jpg')],check=True)
    shots=sorted(overviews.glob('*.jpg'))
    for start in range(0,len(shots),20):
        board=Image.new('RGB',(1080,1680),'#EEEAE4');draw=ImageDraw.Draw(board)
        for j,path in enumerate(shots[start:start+20]):
            im=Image.open(path).convert('RGB');im.thumbnail((216,380));x=j%5*216;y=j//5*420
            board.paste(im,(x+(216-im.width)//2,y));draw.text((x+8,y+387),f'{start+j} s',fill='#181313')
        board.save(out/f'planche-{start//20+1:03d}.jpg',quality=92)
    write_json(out/'reference.json',{**ref,'source':str(source.relative_to(ROOT)),
        'images_extraites':0 if overview_only else len(frames),'analyse_semantique':'À réaliser par l’agent ; extraction technique uniquement.'})
    analysis=out/'analyse.md'
    if not analysis.exists():analysis.write_text(f'''# Analyse de référence — {ref['folder']}\n\nRéférence `{ref['id']}` · SHA-256 `{ref['sha256']}`.\n\nLes planches à une image par seconde servent au repérage. Pour la lecture image par image, utiliser `images/` et les horodatages de `images-et-temps.json`. Écouter `audio-reference.wav` pour les voix, la musique et les contacts. L’extraction seule n’est pas une analyse.\n\n| Début–fin | Images examinées | Plan, action, anticipation, contact, réaction | Dialogue et intonation | Bruitage et musique | Équivalent Le Corps Parle.fr |\n|---|---|---|---|---|---|\n\nDocumenter les passages effectivement examinés, le découpage complet, les répliques, la chute, les faits médicaux à vérifier et les actifs existants à réutiliser. Conserver cette référence dans la provenance du futur épisode.\n''')
    print(f'{len(frames)} images source · dossier de travail : {out}',flush=True)
    return out


def sauvegarder():
    data=indexer();config=json.loads(CONFIG.read_text());account=config['account']
    account={**account,'id':str(uuid5(NAMESPACE_URL,'https://www.tiktok.com/@'+account['handle'].lstrip('@')))}
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out=BASE/'out'/stamp;out.mkdir(parents=True,exist_ok=False)
    bundle={'schema':'postly-reference-library-v1','account':account,'references':[],'auxiliary':[]};mapping={}
    def record(path,arc):
        mapping[arc]=path
        return {'path':arc,'filename':path.name,'sha256':digest(path),'size_bytes':path.stat().st_size}
    for r in data['references']:
        if not r['local_present']:continue
        v=record(DOWNLOADS/r['relative_path'],f"files/{r['id']}/original{Path(r['filename']).suffix.lower()}")
        thumb=BASE/'out/miniatures'/f"{r['id']}.jpg"
        t=record(thumb,f"files/{r['id']}/preview.jpg") if thumb.exists() else None
        bundle['references'].append({**r,'video':v,'thumbnail':t})
    archive=DOWNLOADS/'archive.txt'
    if archive.exists():bundle['auxiliary'].append(record(archive,'files/archive.txt'))
    manifest=out/'manifest.json';write_json(manifest,bundle)
    print(f"Sauvegarde : {len(bundle['references'])} vidéos · {sum(p.stat().st_size for p in mapping.values())/1024**2:.1f} Mio",flush=True)
    receipt=send(config,manifest,mapping,remote_module='scripts.import_studio_references',episode_receipts=False)
    write_json(BASE/'recu-sauvegarde.json',receipt)


def main():
    parser=ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    sub.add_parser('indexer');sub.add_parser('sauvegarder')
    for name in ('preparer','restaurer'):
        p=sub.add_parser(name);p.add_argument('date');p.add_argument('--video')
        if name=='preparer':p.add_argument('--apercus-seulement',action='store_true')
    args=parser.parse_args()
    if args.action=='indexer':indexer()
    elif args.action=='sauvegarder':sauvegarder()
    else:
        ref=resolve(args.date,args.video)
        if args.action=='restaurer':restore(ref)
        else:preparer(ref,args.apercus_seulement)


if __name__=='__main__':main()
