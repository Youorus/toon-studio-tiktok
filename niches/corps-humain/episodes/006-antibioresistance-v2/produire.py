"""Anime le script court sur les prises réelles, puis exporte le master TikTok."""
from argparse import ArgumentParser
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw

from toonstudio.cards import actor_badge
from toonstudio import voice
from toonstudio.config import H, W
from toonstudio.episode import action_track
from toonstudio.sous_titres import CaptionedEpisode

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'out'
MASTER = OUT/'La-bacterie-qui-na-pas-bouge-Le-Corps-Parle.mp4'
IMPACT = 1.38


def pose(t, dx=0, dy=0, angle=0, scale=1, curve='douce'):
    return dict(t=t, dx=dx, dy=dy, angle=angle, echelle=scale, courbe=curve)


def word_time(line, word):
    for text, begin, _ in line['mots']:
        if text.casefold().strip('…!?.,;:') == word.casefold():
            return line['t0'] + begin
    raise ValueError(f'Ancre vocale absente : {word} dans {line["dit"]}')


class CorpsParle(CaptionedEpisode):
    def _timeline(self):
        super()._timeline()
        trimmed = OUT/'prises'
        trimmed.mkdir(parents=True, exist_ok=True)
        cursor = 0
        for shot in self.shots:
            shot['t0'] = cursor
            for line in self.lines:
                if line['shot'] != shot['id']:
                    continue
                source = line['audio']
                duration = voice.duration(source)
                first, last = line['mots'][0][1], line['parole']
                comic_pause = line['dit'].startswith('Non…')
                lead = min(.35, max(0, first - (.70 if comic_pause else .17)))
                tail = min(.18, max(0, duration - last - .15))
                if lead or tail:
                    clip = trimmed / f'{source.stem}-{round(lead*1000)}-{round(tail*1000)}.wav'
                    if not clip.is_file():
                        length = duration - lead - tail
                        subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',str(source),'-ss',f'{lead:.6f}',
                                        '-t',f'{length:.6f}','-ar','48000','-c:a','pcm_s16le',str(clip)],check=True)
                    line['audio'] = clip
                    line['mots'] = [(word, begin-lead, end-lead) for word,begin,end in line['mots']]
                    line['visemes'] = [(at-lead, mouth) for at,mouth in line['visemes'] if at >= lead]
                    line['parole'] -= lead
                    duration = voice.duration(clip)
                line['t0'] = cursor
                cursor += max(duration, line['parole']) + line['pause']
                line['t1'] = cursor
            shot['t1'] = cursor
        self.duration = cursor + .4

    def __init__(self):
        super().__init__(ROOT)
        self.starts = {s['id']: s['t0'] for s in self.shots}
        self.by_shot = {name: [line for line in self.lines if line['shot'] == name] for name in self.starts}
        self.key_moments = {}
        self.direct()

    def direct(self):
        starts, lines = self.starts, self.by_shot

        def animate(shot, name, *keys):
            self.actions[(shot, name)] = action_track(keys, f'{shot}/{name}')

        def badge(shot, actor, label, at, duration=1.8, offset=(0, -140),
                  color='#503467', dot='#D4A5ED', scale=1):
            spec = {'acteur':actor, 'decalage':offset, 'point':dot}
            image = actor_badge(label, color, dot)
            if scale != 1:
                image = image.resize((round(image.width*scale), round(image.height*scale)), Image.Resampling.LANCZOS)
            self.mini_badges.setdefault(shot, []).append((spec, at, at + duration, image))

        def fx(shot, line, name, offset=0):
            lines[shot][line].setdefault('sfx', []).append(f'{name}@{offset:.3f}')

        def cue(shot, line, word):
            return word_time(lines[shot][line], word) - starts[shot]

        for shot in ('ouverture', 'ordonnance'):
            animate(shot, 'gelule',
                    pose(0,-202,-791,11,.51),pose(.22,-216,-740,15,.55),
                    pose(.57,-226,-506,20,.64,'lineaire'),pose(.88,-187,-316,-12,.79),
                    pose(1.14,-91,-128,17,.92),pose(IMPACT,0,0,0,1),
                    pose(1.54,7,-39,-8,1.035),pose(1.79,0,0,0,1))
            badge(shot,'gelule','Antibiotique',starts[shot]+.2,1.98,(-236,-12),'#1E4352','#91D3DF',.88)
            fx(shot,0,'plouf' if shot=='ouverture' else 'ploc',IMPACT)
            animate(shot,'estomac',pose(.37),pose(.62,7,-12,-7),pose(1.10),
                    pose(IMPACT),pose(IMPACT+.17,8,-13,7),pose(IMPACT+.55))
            self.key_moments[shot] = {'impact': starts[shot]+IMPACT}

        shot = 'breche'
        entry = cue(shot,0,'genou') + .12
        party = cue(shot,3,'fête') - .04
        animate(shot,'peau',pose(.05),pose(.29,11,-14,-8),pose(.75),
                pose(lines[shot][2]['t0']-starts[shot]+.18,12,-6,6),
                pose(lines[shot][2]['t0']-starts[shot]+.72))
        animate(shot,'violette',pose(0,-32,-368,-18,.007),pose(entry,-32,-368,-18,.007),
                pose(entry+.32,-42,-280,-13,.53),pose(entry+.72,-30,-134,11,.87),
                pose(entry+1.02,-11,-30,-8,1.05),pose(entry+1.21))
        fx(shot,0,'alerte',.12)
        badge(shot,'violette','Bactérie',starts[shot]+entry+.48,1.95,(-34,-141))
        for i,(name,x,y) in enumerate((('verte1',-97,-172),('verte2',31,-322),('verte3',-84,-233))):
            t = party + i*.15
            animate(shot,name,pose(0,x,y,-16,.007),pose(t,x,y,-16,.007),
                    pose(t+.17,x*.55,y*.55,-16,.62),pose(t+.36,9,-9,12,1.06),pose(t+.53))
            fx(shot,3,'ploc',starts[shot]+t+.29-lines[shot][3]['t0'])
        badge(shot,'verte1','Bactéries',starts[shot]+party+.3,1.60,(4,-128),'#2C4E37','#8FF194')
        self.key_moments[shot] = {'entree': starts[shot]+entry+.75, 'fete': starts[shot]+party+.8}

        shot = 'survivante'
        gone = cue(shot,0,'disparaissent')
        reveal = cue(shot,1,'rien')
        family = cue(shot,3,'famille') - .09
        animate(shot,'globule',pose(0,-142,43,-11,.86),pose(.20,-110,23,-7,.95),
                pose(.62,8,-8,8,1.06),pose(.88),
                pose(lines[shot][2]['t0']-starts[shot]+.12,-10,-10,-8,1.08),
                pose(lines[shot][2]['t0']-starts[shot]+.66))
        badge(shot,'globule','Globule blanc',starts[shot]+.32,1.75,(65,-139),'#285259','#E9F9EB')
        for i,name in enumerate(('verte1','verte2','verte3')):
            t = gone + .17*i
            animate(shot,name,pose(t),pose(t+.17,-5,-11,-10,.70),pose(t+.46,14,6,16,.007))
        fx(shot,0,'passage',gone-.09)
        badge(shot,'violette','Bactérie\nrésistante',starts[shot]+reveal-.1,1.90,(-9,-169))
        for i,(name,x,y) in enumerate((('clone1',-105,145),('clone2',-154,-82),('clone3',95,-151))):
            t = family + i*.17
            animate(shot,name,pose(0,x,y,15,.007),pose(t,x,y,15,.007),
                    pose(t+.18,x*.55,y*.55,-11,.68),pose(t+.41,3,-9,8,1.06),pose(t+.55))
            fx(shot,3,'ploc',starts[shot]+t+.28-lines[shot][3]['t0'])
        self.key_moments[shot] = {'disparition': starts[shot]+gone+.45, 'resistance': starts[shot]+reveal+.32,
                                 'famille': starts[shot]+family+.72}
        shot = 'cabinet'
        animate(shot,'lea',pose(.12),pose(.60,0,0,1.6),pose(1.18),
                pose(lines[shot][2]['t0']-starts[shot]+.37,0,0,1.5),
                pose(lines[shot][2]['t0']-starts[shot]+.89))
        cta = lines[shot][-1]['t0'] - starts[shot]
        animate(shot,'docteure',pose(cta),pose(cta+.55,0,-2,-1.7,1.01),pose(cta+1.18))
        fx(shot,4,'ding',.14)
        self.key_moments[shot] = {'cta': starts[shot]+cta+.74}

    def _actor_labels(self, frame, shot, t, placed, view):
        if shot['id'] == 'ouverture':
            delta = t - self.starts['ouverture'] - IMPACT
            if 0 < delta < .44:
                lay = Image.new('RGBA', frame.size)
                d = ImageDraw.Draw(lay)
                x0,y0,x1,y1 = view
                for i,(dx, lift) in enumerate(((-135,70),(-98,125),(-42,144),(42,142),(93,105),(119,67))):
                    q = delta / .44
                    x = (681 + dx * q - x0) * W / (x1 - x0)
                    y = (1115 - lift * 4 * q * (1-q) - y0) * H / (y1 - y0)
                    r = (10 if i in (2,3) else 7) * (1-.65*q)
                    a = round(238*(1-q))
                    d.ellipse((x-r,y-r*1.5,x+r,y+r*1.5),fill=(255,202,165,a),outline=(137,53,62,a),width=2)
                frame.alpha_composite(lay)
        super()._actor_labels(frame, shot, t, placed, view)


def main():
    parser = ArgumentParser()
    parser.add_argument('--apercu', action='store_true')
    args = parser.parse_args()
    episode = CorpsParle()
    OUT.mkdir(exist_ok=True)
    episode.save_subtitles(OUT)
    plan = {'duree': episode.duration, 'signature': episode.niche['filigrane'],
            'scenes': [{'id':s['id'],'debut':s['t0'],'fin':s['t1']} for s in episode.shots],
            'repliques': [{k:l[k] for k in ('qui','dit','t0','t1')} for l in episode.lines],
            'moments':episode.key_moments}
    (OUT/'montage.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    print(f'{episode.duration:.2f} s · {len(episode.lines)} prises · {len(episode.cues)} sous-titres', flush=True)
    for shot in plan['scenes']:
        print(shot['id'], f"{shot['debut']:.2f}–{shot['fin']:.2f} s", flush=True)
    if args.apercu:
        times = [0.48, 1.00, 1.51]
        for keys in episode.key_moments.values():
            times.extend(t for t in keys.values() if t > 1.55)
        times.sort()
        episode.preview(OUT, times)
        return
    problems = episode.controle(OUT)
    if problems:
        raise SystemExit('\n'.join(problems))
    episode.render(MASTER, preview_every=240)


if __name__ == '__main__':
    main()
