"""Compose un morceau de fond continu et le mixe avec le master 006."""
import json
import math
from pathlib import Path
import re
import subprocess

import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'out'
MASTER = OUT / 'La-bacterie-qui-na-pas-bouge-Le-Corps-Parle.mp4'
FINAL = MASTER.with_name(MASTER.stem + '-Avec-Musique.mp4')
STEM = OUT / 'musique-de-fond.wav'
SR = 48000
BEAT = .5


def ff(*args):
    return subprocess.run(list(map(str, args)), capture_output=True, check=True)


def levels(file):
    report = ff('ffmpeg', '-nostdin', '-hide_banner', '-nostats', '-i', file, '-vn',
                '-af', 'ebur128=peak=true', '-f', 'null', '-').stderr.decode().rsplit('Summary:', 1)[-1]
    return (float(re.search(r'I:\s*([-\d.]+) LUFS', report)[1]),
            float(re.search(r'Peak:\s*([-\d.]+) dBFS', report)[1]))


def compose(duration):
    size = round(duration * SR)
    stereo = np.zeros((size, 2), dtype=np.float32)
    rng = np.random.default_rng(164)
    tau = 2 * np.pi

    def add(at, signal, amp, pan=0):
        i = round(at * SR)
        n = min(len(signal), size-i)
        if n <= 0:
            return
        angles = (pan + 1) * np.pi / 4
        stereo[i:i+n, 0] += amp * math.cos(angles) * signal[:n]
        stereo[i:i+n, 1] += amp * math.sin(angles) * signal[:n]

    def note(at, midi, duration, amp, pan, instrument):
        t = np.arange(round(SR * duration)) / SR
        hz = 440 * 2 ** ((midi-69)/12)
        phase = tau * hz * t
        fade = np.minimum(1, (duration-t)/.060)
        if instrument == 'keys':
            index = .73 * np.exp(-5.7*t)
            signal = (np.sin(phase + index*np.sin(2*phase)) + .11*np.sin(1.002*phase)) * np.exp(-3.8*t)
        elif instrument == 'mallet':
            signal = (np.sin(phase)*np.exp(-7.4*t) + .23*np.sin(4.02*phase)*np.exp(-24*t)
                      + .08*np.sin(9.06*phase)*np.exp(-46*t))
        else:
            signal = (.76*np.sin(phase) + .19*np.sin(2*phase) + .08*np.sin(3*phase))*np.exp(-3.2*t)
        add(at, signal * fade * np.minimum(1, t/.010), amp, pan)

    bands = {
        'brush': butter(2, [1350, 4350], 'bandpass', fs=SR, output='sos'),
        'hat': butter(2, [4200, 8800], 'bandpass', fs=SR, output='sos'),
    }

    def drum(at, kind, amp, pan=0):
        t = np.arange(round(SR * (.14 if kind == 'hat' else .24))) / SR
        if kind == 'kick':
            phase = tau * (54*t + 2.8*(1-np.exp(-26*t)))
            signal = np.sin(phase)*np.exp(-25*t)
        else:
            signal = sosfilt(bands[kind], rng.standard_normal(t.size))
            signal *= np.exp(-t*(57 if kind=='hat' else 36))
        add(at, signal * np.minimum(1, t/.005), amp, pan)

    # Une grille originale, des syncopes légères et un motif de quatre notes.
    progression = (
        (50,(60,64,65,69)), (43,(59,64,65,69)), (48,(59,62,64,67)), (45,(59,60,64,67)),
        (41,(57,60,64,67)), (47,(55,59,62,64)), (50,(60,64,65,69)), (45,(57,62,64,67)),
    )
    melody = {
        0: ((.72,69),(1.45,72),(2.35,74)),
        1: ((.28,71),(1.26,69)),
        3: ((.30,67),(1.05,69),(1.58,64)),
        4: ((.55,69),(1.26,72),(1.75,76)),
        5: ((.28,74),(1.32,71)),
        7: ((.52,64),(1.25,67),(1.75,69)),
    }
    for bar in range(math.ceil(duration/(4*BEAT))):
        at = bar * 4 * BEAT
        bass, chord = progression[bar % len(progression)]
        closing = duration-at <= 2.3
        for j, offset in enumerate((.03, .79, 1.37)):
            pitches = chord if j == 0 else chord[j-1:j+2]
            for i, pitch in enumerate(pitches):
                note(at+offset+.018*i, pitch, .72 if not closing else 1.15,
                     (.050 if j==0 else .037)*(1-.045*i), -.23+.16*i, 'keys')
            if closing:
                break
        for offset, pitch in ((.005, bass-12 if bass>=47 else bass), (.61, bass),
                              (1.02,bass-12 if bass>=47 else bass), (1.61,bass+7)):
            note(at+offset,pitch,.44,.145,0,'bass')
            if closing:
                break
        if closing:
            continue
        for j, beat in enumerate((0,.5,1,1.5,2,2.5,3,3.5)):
            jitter = float(rng.uniform(-.013,.013))
            drum(at+max(0, beat*BEAT+.018*(j%2)+jitter), 'hat', .047 if j%2 else .033, .29)
        for offset in (0,1.04):
            drum(at+offset,'kick',.145)
        for offset in (.53,1.54):
            drum(at+offset,'brush',.082,-.18)
        phrase_gain = .75 if bar % 16 >= 8 else 1
        for j,(offset,pitch) in enumerate(melody.get(bar % 8, ())):
            note(at+offset,pitch,.39,.080*phrase_gain,-.17+.20*(j%2),'mallet')

    # Une ambiance stéréo courte, qui reste compatible avec l’écoute mono.
    delay = round(.081 * SR)
    stereo[delay:, 0] += .065 * stereo[:-delay, 1].copy()
    stereo[delay:, 1] += .065 * stereo[:-delay, 0].copy()
    return stereo


def mix_envelope(music, subtitles, scenes):
    t = np.arange(len(music), dtype=np.float32) / SR
    spans = []
    for cue in subtitles:
        start, end = cue['debut'], cue['fin']
        if spans and start - spans[-1][1] < .32:
            spans[-1][1] = max(end, spans[-1][1])
        else:
            spans.append([start, end])
    gain = np.ones(len(music), dtype=np.float32)
    for start, end in spans:
        # Récupération seulement sur les vraies pauses.
        dip = np.minimum(np.clip((t-start+.12)/.12, 0, 1), np.clip((end+.34-t)/.34, 0, 1))
        gain = np.minimum(gain, 1-.47*dip)
    impact = scenes['moments']['ouverture']['impact']
    gain = np.minimum(gain, 1-.64*np.maximum(0,1-np.abs(t-impact)/.24))
    cabinet = next(scene['debut'] for scene in scenes['scenes'] if scene['id']=='cabinet')
    gain *= 1-.16*np.clip((t-cabinet)/.55,0,1)
    gain *= np.minimum(np.clip(t/.18,0,1), np.clip((t[-1]-t)/.95,0,1))
    return music * gain[:, None]


def main():
    media = json.loads(ff('ffprobe','-v','error','-show_entries','format=duration','-of','json',MASTER).stdout)
    duration = float(media['format']['duration'])
    montage = json.loads((OUT/'montage.json').read_text())
    subtitles = json.loads((OUT/'sous-titres.json').read_text())
    music = compose(duration)
    wavfile.write(STEM, SR, music)
    raw_lufs, _ = levels(STEM)
    music *= 10 ** ((-25.4-raw_lufs)/20)
    mixed_stem = mix_envelope(music, subtitles, montage)
    wavfile.write(STEM, SR, mixed_stem.astype(np.float32))
    bed_lufs, bed_peak = levels(STEM)
    graph = ('[0:a]aresample=48000,pan=stereo|c0=0.707*c0|c1=0.707*c0[dialogue];'
             '[dialogue][1:a]amix=inputs=2:duration=first:normalize=0[a]')
    ff('ffmpeg','-nostdin','-v','error','-y','-i',MASTER,'-i',STEM,
       '-filter_complex',graph,'-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac',
       '-b:a','192k','-ar',SR,'-movflags','+faststart',FINAL)
    result_lufs, result_peak = levels(FINAL)
    assert -17 < result_lufs < -13 and result_peak <= -1
    report = {'duree_s':duration,'fond_lufs':bed_lufs,'fond_crete_dbtp':bed_peak,'mix_lufs':result_lufs,
              'mix_crete_dbtp':result_peak,'tempo_bpm':120,'image_reencodee':False,
              'musique':'composition originale instrumentale pour Le Corps Parle.fr'}
    (OUT/'controle-mix-musical.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
