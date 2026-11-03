"""Composition originale « Petites combines », instrumentale synthétisée pour Toon Studio."""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

RATE=48000
BPM=146
BEAT=60/BPM
SWING=.59
CHORDS=[(45,57,60,64),(38,53,57,60),(43,55,59,62),(36,55,59,64),
        (41,53,57,60),(42,54,57,60),(47,57,59,62),(40,56,62,65)]
THEME=[
    [(0,72),(.5,76),(1.5,74),(2.5,69),(3.5,72)],
    [(.5,77),(1,76),(1.5,72),(3,69)],
    [(0,71),(.5,74),(1.5,79),(2.5,76),(3.5,74)],
    [(.5,71),(1.5,67),(2,69),(3.5,74)],
    [(0,72),(.5,76),(1.5,77),(2.5,81),(3.5,77)],
    [(0,75),(1,72),(2,66),(3.5,69)],
    [(.5,71),(1,74),(1.5,77),(3,74)],
    [(0,68),(1,71),(1.5,74),(2.5,77),(3.5,68)],
]


def compose(duration):
    track=np.zeros((round(duration*RATE),2))
    rng=np.random.default_rng(722)

    def event(beat,length,level,pan,note=None,kind='mallet'):
        start=round((beat+(SWING-.5 if beat%1==.5 else 0))*BEAT*RATE)
        count=min(len(track)-start,round(length*BEAT*RATE))
        if count<=0:
            return
        t=np.arange(count)/RATE
        n=rng.standard_normal(count) if note is None else None
        if kind=='kick':
            signal=np.sin(2*np.pi*(52*t+2.1*(1-np.exp(-32*t))))*np.exp(-23*t)
        elif kind=='brush':
            band=sosfilt(butter(2,[920,7400],fs=RATE,btype='bandpass',output='sos'),n)
            signal=band*np.exp(-21*t)
        elif kind=='hat':
            band=sosfilt(butter(2,5100,fs=RATE,btype='highpass',output='sos'),n)
            signal=band*np.exp(-52*t)
        else:
            phase=2*np.pi*440*2**((note-69)/12)*t
            if kind=='bass':
                signal=(np.sin(phase)+.38*np.sin(2*phase)+.15*np.sin(3*phase))*np.exp(-5.6*t)
            elif kind=='pizz':
                signal=(np.sin(phase)+.53*np.sin(2*phase)+.21*np.sin(3*phase))*np.exp(-15*t)
            else:
                signal=(np.sin(phase)+.34*np.sin(3.98*phase)+.16*np.sin(8.14*phase))*np.exp(-8.8*t)
        envelope=np.minimum(1,t*320)*np.minimum(1,(count/RATE-t)*100)
        track[start:start+count]+=level*(signal*envelope)[:,None]*[np.sqrt(.5-pan/2),np.sqrt(.5+pan/2)]

    for index in range(int(duration/(BEAT*4))+1):
        base=index*4
        root,*voicing=CHORDS[index%len(CHORDS)]
        next_root=CHORDS[(index+1)%len(CHORDS)][0]
        for beat,note in enumerate((root,root+7,root+12,next_root-2 if next_root>root else next_root+2)):
            event(base+beat,.96,.30,0,note,'bass')
            if beat in (0,2):
                event(base+beat,.62,.125,.05,kind='kick')
            else:
                event(base+beat,.52,.13,-.12,kind='brush')
            event(base+beat+.5,.26,.10,.24,kind='hat')
        for beat in (.5,1.5,3):
            for note in voicing:
                event(base+beat,.47,.079,-.44,note,'pizz')
        melody=THEME[index%len(THEME)]
        if index%8 in (2,5,7):
            melody=melody[:-1]
        for beat,note in melody:
            event(base+beat,.73,.135,.36,note)
        if index%8==7:
            for beat,note in ((2.75,64),(3.25,67),(3.5,68)):
                event(base+beat,.42,.087,.15,note,'pizz')
    peak=np.sqrt(np.mean(track**2))
    track*=.069/max(peak,.0001)
    size=len(track)
    fade_in=min(size,round(.18*RATE))
    fade_out=min(size,round(.55*RATE))
    track[:fade_in]*=np.linspace(0,1,fade_in)[:,None]
    track[-fade_out:]*=np.linspace(1,0,fade_out)[:,None]
    return track


def ff(*args):
    return subprocess.run(list(map(str,args)),capture_output=True,text=True,check=True)


def levels(path):
    result=ff('ffmpeg','-nostdin','-hide_banner','-i',path,'-vn','-af','ebur128=peak=true','-f','null','-')
    summary=result.stderr.rsplit('Summary:',1)[-1]
    return [float(re.search(pattern,summary)[1]) for pattern in (r'I:\s+(-?[\d.]+) LUFS',r'Peak:\s+(-?[\d.]+) dBFS')]


def mix(image,sound,subtitles,markers,out):
    duration=float(ff('ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',image).stdout.strip())
    stem=out.parent/'petites-combines.wav'
    track=compose(duration)
    env=np.ones(len(track))
    for cue in json.loads(subtitles.read_text()):
        a=max(0,round((cue['debut']-.075)*RATE))
        b=min(len(track),round((cue['fin']+.10)*RATE))
        t=np.arange(max(0,b-a))/RATE
        env[a:b]=np.minimum(env[a:b],1-.43*np.minimum(np.minimum(1,t/.08),(len(t)/RATE-t)/.10))
    for group in json.loads(markers.read_text())['moments'].values():
        for name,time in group.items():
            if name not in {'coup','chute','duel','parade','impact','réaction','refus'}:
                continue
            a=max(0,round((time-.12)*RATE))
            b=min(len(track),round((time+.34)*RATE))
            env[a:b]*=1-.47*np.maximum(0,1-abs(np.arange(a,b)/RATE-time)/.29)
    wavfile.write(stem,RATE,(track*env[:,None]).astype('float32'))
    source_lufs,_=levels(sound)
    gain=np.clip(-14.5-source_lufs,-4,7)
    graph=(f'[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain:.2f}dB[dialogue];'
           '[dialogue][2:a]amix=inputs=2:duration=first:normalize=0,'
           'alimiter=limit=0.80:level=false:latency=true[final]')
    ff('ffmpeg','-nostdin','-v','error','-y','-i',image,'-i',sound,'-i',stem,'-filter_complex',graph,
       '-map','0:v:0','-map','[final]','-c:v','copy','-c:a','aac','-b:a','192k','-ar',RATE,
       '-t',duration,'-movflags','+faststart',out)
    loudness,peak=levels(out)
    print(f'{out.name} · {duration:.2f} s · {loudness:.1f} LUFS · {peak:.1f} dBTP',flush=True)
    assert -17 < loudness < -12 and peak < -.8
    (out.parent/'controle-musique.json').write_text(json.dumps({
        'titre':'Petites combines','tempo_bpm':BPM,'source':'composition et synthèse Toon Studio',
        'mix_lufs':loudness,'mix_crete_dbtp':peak,'master_sha256':sha256(out.read_bytes()).hexdigest(),
    },ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    parser=ArgumentParser(description=__doc__)
    for flag in ('image','son','sous-titres','montage','sortie'):
        parser.add_argument('--'+flag,type=Path,required=True)
    args=parser.parse_args()
    mix(args.image,args.son,args.sous_titres,args.montage,args.sortie)
