"""Mix musical de la reprise avec des creux sur les contacts et la parole."""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'out'
BASE=OUT/'La-bacterie-qui-na-pas-bouge-Reprise.mp4'
FINAL=OUT/'La-bacterie-qui-na-pas-bouge-Le-Corps-Parle-Reprise.mp4'
STEM=OUT/'musique-de-fond.wav'
sys.path.insert(0,str(ROOT.parent/'006-antibioresistance-v2'))
from mixer_musique import compose, levels, mix_envelope, SR


def ff(*args):
    return subprocess.run(list(map(str,args)),capture_output=True,check=True)


def make_bed(montage, stem):
    music=compose(montage['duree'])
    wavfile.write(stem,SR,music)
    loudness,_=levels(stem)
    music*=10**((-26.0-loudness)/20)
    subtitles=json.loads((OUT/'sous-titres.json').read_text())
    # Le mix reprend la musique du compte et respire brièvement à chaque impact.
    montage['moments']['ouverture']=montage['moments']['estomac']
    music=mix_envelope(music,subtitles,montage)
    time=np.arange(len(music))/SR
    for scene,key in (('intrusion','coup'),('intrusion','chute'),('duel','duel'),('resistance','parade')):
        moment=montage['moments'][scene][key]
        gain=1-.50*np.maximum(0,1-np.abs(time-moment)/.29)
        music*=gain[:,None]
    wavfile.write(stem,SR,music.astype('float32'))


def main():
    p=ArgumentParser()
    p.add_argument('--source',type=Path,default=BASE)
    p.add_argument('--sortie',type=Path,default=FINAL)
    args=p.parse_args()
    montage=json.loads((OUT/'montage.json').read_text())
    stem=STEM if args.sortie==FINAL else args.sortie.with_suffix('.wav')
    make_bed(montage,stem)
    voice_lufs,_=levels(args.source)
    gain=max(-1.0,min(1.4,-14.2-voice_lufs))
    graph=(f'[0:a]aresample=48000,pan=stereo|c0=0.707*c0|c1=0.707*c0,volume={gain:.2f}dB[voix];'
           '[voix][1:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.84:level=false:latency=true[a]')
    ff('ffmpeg','-nostdin','-v','error','-y','-i',args.source,'-i',stem,'-filter_complex',graph,
       '-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-ar',48000,
       '-movflags','+faststart',args.sortie)
    lufs,peak=levels(args.sortie)
    print(f'{args.sortie.name} · {lufs:.1f} LUFS · {peak:.1f} dBTP')
    assert -16 < lufs < -12 and peak < -1
    if args.sortie==FINAL:
        out={'mix_lufs':lufs,'mix_crete_dbtp':peak,'fond_lufs':levels(STEM)[0],
             'sha256':sha256(FINAL.read_bytes()).hexdigest(),'composition_originale':True}
        (OUT/'controle-mix.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    main()
