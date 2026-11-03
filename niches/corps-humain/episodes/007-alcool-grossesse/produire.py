"""Direction des mouvements, apparition des badges et export de l'image de l'épisode 007."""
from argparse import ArgumentParser
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

from accessoires import pantomime
from toonstudio.episode import action_track
from toonstudio.sous_titres import CaptionedEpisode

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'out'


class Episode007(CaptionedEpisode):
    def __init__(self):
        super().__init__(ROOT)
        self.passages=[line for line in self.lines if line['shot']=='passage']
        self.envoi=self.passages[1]['t0']+.32
        self.arrivee=self.passages[2]['t0']+.12
        self.refus=self.passages[3]['t0']+.32
        self.verre=Image.open(ROOT/'art'/'verre.png').convert('RGBA')
        self.bouteille=Image.open(ROOT/'art'/'bouteille.png').convert('RGBA')
        self.passages[0]['sfx']=['glisse@0.10']
        self.passages[1]['sfx']=['glisse@0.32']
        self.passages[2]['sfx']=['pop@0.12']
        self.passages[3]['sfx']=['pop@0.32']
        self.move('uterus',(.04,0,0,0,1),(.24,0,-10,-5,1.12),(.62,0,0,0,1),
                  (self.refus-.14,0,0,0,1),(self.refus+.07,3,-6,5,1.08),(self.refus+.40,0,0,0,1))
        self.move('placenta',(self.envoi-.18,0,0,0,1),(self.envoi+.06,-5,2,-7,.97),
                  (self.envoi+.24,8,0,5,1.04),(self.envoi+.52,0,0,0,1))
        self.move('foetus',(0,0,16,3,.96),(1.08,0,0,0,1),(self.arrivee-.19,0,-7,-3,1),
                  (self.arrivee+.10,39,11,13,1.10),(self.arrivee+.27,46,-17,8,.99),
                  (self.arrivee+.52,27,-12,3,1),(self.arrivee+.84,5,0,-2,1),
                  (self.arrivee+1.16,0,0,0,1))
        self.passages[1]['reactions']={'uterus':'inquiet','foetus':'fatigue'}
        self.passages[2]['reactions']={'placenta':'fatigue','uterus':'choque'}

    def move(self,actor,*poses):
        self.actions[('passage',actor)]=action_track(
            (dict(t=t,dx=x,dy=y,angle=angle,echelle=scale) for t,x,y,angle,scale in poses),actor)

    def actor_state(self,shot,name,spec,t,line,prev_lines):
        state=super().actor_state(shot,name,spec,t,line,prev_lines)
        if name=='foetus' and t<self.arrivee-.16:
            state.update(emo='fatigue',blink=True)
        return state

    def _actor_labels(self,frame,shot,t,placed,view):
        if shot['id']=='passage':
            actors={a['name']:a for a in placed}
            px,py=actors['placenta']['face']
            fx,fy=actors['foetus']['face']
            start=(px+91,py+51)
            end=(fx+47,fy+125)
            def cord(u):
                return (start[0]+(end[0]-start[0])*u,
                        start[1]+(end[1]-start[1])*u+65*math.sin(math.pi*u))
            overlay=Image.new('RGBA',frame.size)
            draw=ImageDraw.Draw(overlay)
            pantomime(overlay,t,actors['uterus']['face'],self.verre,self.bouteille)
            points=[cord(i/36) for i in range(37)]
            for color,width in (('#6D383B',22),('#F4A29C',14),('#F7B7A7',5)):
                draw.line(points,fill=color,width=width,joint='curve')
            for index in range(4):
                q=(t-self.envoi-index*.19)/max(.4,self.arrivee-self.envoi-.57)
                if 0<q<1:
                    x,y=cord(q)
                    r=9*math.sin(math.pi*q)**.25
                    draw.ellipse((x-r,y-r,x+r,y+r),fill='#B93647',outline='#FFF9ED',width=2)
            q=t-self.arrivee
            if 0<=q<.35:
                for angle in (-2.85,-2.25,-1.7):
                    x,y=end
                    r=18+140*q
                    draw.line((x+r*math.cos(angle),y+r*math.sin(angle),
                               x+(r+25)*math.cos(angle),y+(r+25)*math.sin(angle)),
                              fill=(255,249,237,round(245*(1-q/.35))),width=7)
            frame.alpha_composite(overlay)
        super()._actor_labels(frame,shot,t,placed,view)


def main():
    parser=ArgumentParser()
    parser.add_argument('--apercu',action='store_true')
    args=parser.parse_args()
    episode=Episode007()
    OUT.mkdir(exist_ok=True)
    episode.save_subtitles(OUT)
    markers={'passage':{'gorgée':.35,'alcool':episode.envoi,'réaction':episode.arrivee,'refus':episode.refus},
             'cabinet':{'cta':episode.lines[-1]['t0']}}
    (OUT/'montage.json').write_text(json.dumps({'duree':episode.duration,'moments':markers,
        'repliques':[{k:l[k] for k in ('qui','dit','t0','t1')} for l in episode.lines]},
        indent=2,ensure_ascii=False)+'\n')
    print(f'{episode.duration:.2f} s, {len(episode.lines)} prises',flush=True)
    if args.apercu:
        episode.preview(OUT,[.30,1.18,episode.envoi+1.1,episode.arrivee+.14,episode.refus,
                             episode.shots[-1]['t0']+.8,episode.lines[-1]['t0']+.8])
        return
    issues=episode.controle(OUT)
    if issues:
        raise SystemExit('\n'.join(issues))
    episode.render(OUT/'image-et-voix.mp4',preview_every=300)

if __name__=='__main__':
    main()
