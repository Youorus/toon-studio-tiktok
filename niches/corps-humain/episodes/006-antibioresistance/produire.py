"""Plan de jeu animé et export avec les sous-titres de la série."""
from argparse import ArgumentParser
from pathlib import Path

from PIL import Image, ImageDraw

from toonstudio.drawing import ease_in_out
from toonstudio.episode import action_track
from toonstudio.sous_titres import CaptionedEpisode

ROOT = Path(__file__).parent


def pose(t, dx=None, dy=None, angle=None, echelle=None, courbe=None):
    return {key: value for key, value in locals().items() if value is not None}


def bind_actions(ep):
    starts = {s['id']:s['t0'] for s in ep.shots}
    lines = {s:[l for l in ep.lines if l['shot']==s] for s in starts}
    def cue(shot, line, after=0):
        return lines[shot][line]['t0']-starts[shot]+after
    def track(shot, name, *keys):
        ep.actions[(shot,name)] = action_track(keys,f'{shot}/{name}')

    for shot in ('la-vieille-boite','cette-fois'):
        track(shot,'gelule',
            pose(0,-202,-791,11,.51),
            pose(.25,-204,-753,15),
            pose(.64,-226,-480,20,.63,'lineaire'),
            pose(.94,-191,-332,-15,.78),
            pose(1.25,-90,-148,23,.95),
            pose(1.57,8,-33,-9,1.03),
            pose(1.91,0,0,0,1))
    shot='la-vieille-boite'
    track(shot,'estomac',
        pose(.36,0,0,0), pose(.70,5,-14,-7), pose(1.23,0,0,0),
        pose(cue(shot,2,1.42),5,2,6),pose(cue(shot,2,2.18),0,0,0))

    shot='la-breche'
    track(shot,'peau',pose(.68,0,0,0),pose(1.33,13,-14,-9),pose(2.03,0,0,0),
          pose(cue(shot,2,.48),15,-8,7),pose(cue(shot,2,1.2),0,0,0))
    track(shot,'resistante',
        pose(0,-35,-350,-18,.008),
        pose(2.96,-28,-283,-18,.6),
        pose(3.45,-45,-204,10,.7),
        pose(4.34,-29,-70,-8,.94),
        pose(4.94,0,0,0,1),
        pose(cue(shot,3,.62),-14,-19,-6),
        pose(cue(shot,3,1.44),0,0,0))
    for i,(name,dx,dy,line_index) in enumerate((
        ('sensible1',-164,-225,1), ('sensible2',72,-325,3), ('sensible3',-138,-290,3)
    )):
        t=cue(shot,line_index,.63 + i*.24)
        track(shot,name,pose(0,dx,dy,-15,.008),pose(t,dx,dy,-15,.008),
              pose(t+.26,dx*.8,dy*.8,-12,.70),pose(t+.78,dx*.4,dy*.35,13,.94),
              pose(t+1.18,0,0,0,1))
    t=cue(shot,4,-.6)
    track(shot,'globule',pose(0,-210,76,-8,.008),pose(t,-210,76,-8,.008),
          pose(t+.35,-140,33,8,.67),pose(t+.86,5,-10,-6,1.03),pose(t+1.13,0,0,0,1),
          pose(cue(shot,5,.52),-15,-18,6),pose(cue(shot,5,1.28),0,0,0))

    shot='celles-qui-restent'
    for i,name in enumerate(('sensible1','sensible2','sensible3')):
        t=.95+i*.33
        track(shot,name,pose(t,0,0,0,1),pose(t+.28,-6,-13,-12,.69),
              pose(t+.62,16,12,16,.008))
    track(shot,'resistante',pose(.60,0,0,0,1),pose(1.00,11,-13,-12),pose(1.44,0,0,0),
          pose(cue(shot,1,1.04),8,-12,-6),pose(cue(shot,1,1.71),0,0,0))
    for i,(name,dx,dy) in enumerate((
        ('clone1',-110,149),('clone2',-160,-89),('clone3',100,-137)
    )):
        t=cue(shot,3,2.02+i*.41)
        track(shot,name,pose(0,dx,dy,10,.009),pose(t,dx,dy,10,.009),
              pose(t+.28,dx*.45,dy*.46,12,.76),pose(t+.74,0,0,0,1))
    track(shot,'globule',
          pose(.54,0,0,0),pose(1.03,-13,-13,-9),pose(1.59,0,0,0),
          pose(cue(shot,2,.23),14,2,7),pose(cue(shot,2,.92),0,0,0),
          pose(cue(shot,4,.44),-13,13,-6),pose(cue(shot,4,1.17),0,0,0))
    shot='au-cabinet'
    track(shot,'lea',
          pose(cue(shot,0,1.2),0,0,1.9),pose(cue(shot,0,2.1),0,0,0),
          pose(cue(shot,3,.3),0,0,1.7),pose(cue(shot,3,1.14),0,0,0))
    track(shot,'docteure',
          pose(cue(shot,1,.33),0,0,1.4),pose(cue(shot,1,1.28),0,0,0),
          pose(cue(shot,4,.72),0,0,1.6),pose(cue(shot,4,1.62),0,0,0),
          pose(cue(shot,6,.9),0,0,-1.7),pose(cue(shot,6,1.84),0,0,0))
    return starts


class Antibiotiques(CaptionedEpisode):
    def __init__(self, folder):
        super().__init__(folder)
        self.starts = bind_actions(self)

    def _caption(self, frame, line, t):
        if line['shot']=='celles-qui-restent':
            local=t-self.starts[line['shot']]
            if .48<local<2.22:
                for lag in (0,.14,.28):
                    q=(local-.48-lag)/1.46
                    if 0<q<1:
                        w=ease_in_out(q)
                        x=888-586*w
                        y=663+285*w
                        r=35+184*w
                        overlay=Image.new('RGBA',frame.size)
                        d=ImageDraw.Draw(overlay)
                        d.arc((x-r,y-r,x+r,y+r),86,255, fill=(155,225,222,round(155*(1-q))),width=8)
                        frame.alpha_composite(overlay)
        super()._caption(frame,line,t)


def main():
    parser=ArgumentParser()
    parser.add_argument('--planche',action='store_true')
    args=parser.parse_args()
    e=Antibiotiques(ROOT)
    out=ROOT/'out'
    out.mkdir(exist_ok=True)
    e.save_subtitles(out)
    print(f'{e.duration:.2f} s · {len(e.lines)} prises · {len(e.cues)} sous-titres',flush=True)
    if args.planche:
        offsets=[[.36,1.7,6.2,15.8],[.4,4.3,8.8,13.6,16.7,20.1],
                 [.65,3.5],[.3,1.3,2.6,5.9,12.8,14.2],[1.2,7,21,32]]
        times=[s['t0']+t for s,values in zip(e.shots,offsets) for t in values if s['t0']+t<s['t1']]
        e.preview(out,times)
    else:
        problems=e.controle(out)
        if problems:
            raise SystemExit('\n'.join(problems))
        e.render(out/'La-bacterie-qui-na-pas-bouge.mp4',preview_every=240)


if __name__=='__main__':
    main()
