"""Réveil, repas des bactéries, réaction au petit-déjeuner et conclusion au cabinet."""
from argparse import ArgumentParser
import json
import math
from pathlib import Path
import random

from PIL import Image, ImageDraw

from toonstudio.arms import draw_arm
from toonstudio.drawing import clamp,ease_in_out
from toonstudio.episode import action_track
from toonstudio.sous_titres import CaptionedEpisode

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'out'


def qtime(t,a,b):
    return ease_in_out(clamp((t-a)/(b-a)))


class Episode009(CaptionedEpisode):
    def __init__(self):
        super().__init__(ROOT)
        self.buffet=next(s['t0'] for s in self.shots if s['id']=='buffet')
        self.breakfast=next(s['t0'] for s in self.shots if s['id']=='petit-dejeuner')
        self.office=next(s['t0'] for s in self.shots if s['id']=='cabinet')
        buffet=[line for line in self.lines if line['shot']=='buffet']
        self.bite=self.buffet+.82
        self.share=buffet[1]['t1']+.10
        self.reply=next(l['t0'] for l in self.lines if l['shot']=='petit-dejeuner' and l['qui']=='lea')
        self.lines[0]['sfx']=['glisse@0.14']
        buffet[0]['sfx']=['ploc@0.82']
        buffet[1]['sfx']=['glisse@0.19']
        buffet[2]['sfx']=['ploc@0.44']
        breakfast=next(l for l in self.lines if l['shot']=='petit-dejeuner')
        breakfast['reactions']={'lea':'inquiet'}
        self.lines[-1]['sfx']=['ploc@0.15']
        self.action('reveil','cerveau',(0,0,0,-4,.96),(.30,0,-14,4,1.09),(.69,0,0,0,1),
                    (1.28,0,-8,-2,1.02),(1.67,0,0,0,1))
        self.action('buffet','verte',(0,-22,11,-7,.93),(.32,0,-4,3,1.04),(.63,0,0,0,1))
        red_start=buffet[1]['t0']-self.buffet
        self.action('buffet','rouge',(0,14,0,0,1),(red_start-.1,14,0,0,1),
                    (red_start+.17,-4,-15,-9,1.05),(red_start+.49,0,0,0,1))
        signature=self.niche['direction_artistique']['signature']['positions']
        self.original_positions=signature
        self.room_positions=[[x,180+round(y*.18)] for x,y in signature]
        rng=random.Random(990)
        self.crumbs=[(rng.randint(245,913),rng.randint(963,1390),rng.randint(6,13),rng.randint(-35,35)) for _ in range(24)]

    def action(self,scene,actor,*beats):
        self.actions[(scene,actor)]=action_track(
            (dict(t=t,dx=x,dy=y,angle=a,echelle=s) for t,x,y,a,s in beats),actor)

    def _watermark(self,frame,t):
        self.niche['direction_artistique']['signature']['positions']=(
            self.room_positions if t>=self.breakfast else self.original_positions)
        super()._watermark(frame,t)

    def actor_state(self,shot,name,spec,t,line,prev_lines):
        state=super().actor_state(shot,name,spec,t,line,prev_lines)
        if shot['id']=='petit-dejeuner' and name=='lea' and t>self.breakfast+.55:
            state['emo']='degoute'
        return state

    @staticmethod
    def puff(layer,x,y,q,scale=1):
        draw=ImageDraw.Draw(layer)
        opacity=round(79*math.sin(math.pi*clamp(q)))
        for dx,dy,r in ((0,0,24),(26,-6,23),(48,4,18),(21,17,20)):
            cx=x+(dx+115*q)*scale
            cy=y+(dy-34*math.sin(math.pi*q))*scale
            size=(r+14*q)*scale
            draw.ellipse((cx-size,cy-size,cx+size,cy+size),fill=(102,169,83,opacity))

    def brain_gesture(self,layer,t,face):
        x,y=face
        stretch=math.sin(math.pi*clamp((t+.10)/1.15))
        for side in (-1,1):
            shoulder=(x+side*202,y+76)
            draw_arm(layer,shoulder,side,
                     {'longueur':163,'epaisseur':16,'peau':'#FFF9ED','manche':'#FFF9ED','trait':.15},
                     114+47*stretch,-13*side,'poing')

    @staticmethod
    def morsel(draw,x,y,scale=1):
        points=[(x-13*scale,y-7*scale),(x+12*scale,y-11*scale),(x+17*scale,y+5*scale),(x-6*scale,y+10*scale)]
        draw.polygon(points,fill='#E8C28E',outline='#6D383B',width=2)

    def microbe_meal(self,layer,t,faces):
        draw=ImageDraw.Draw(layer)
        for x,y,size,_ in self.crumbs:
            self.morsel(draw,x,y,size/13)
        for who in ('verte','rouge'):
            x,y=faces[who]
            at=self.bite if who=='verte' else self.share+.46
            eat=qtime(t,at-.33,at+.11)*(1-qtime(t,at+.20,at+.62))
            shoulder=(x-63,y+58)
            wrist=draw_arm(layer,shoulder,-1,
                           {'longueur':89,'epaisseur':12,'peau':'#FFF9ED','manche':'#FFF9ED','trait':.15},
                           -26-39*eat,-68-35*eat,'poing')
            if who=='verte' or t>self.share+.42:
                phase=(t-at)%1.5
                size=max(.05,1-qtime(phase,.13,.39))
                self.morsel(draw,wrist[0]+5,wrist[1]-8,.78*size)
        transfer=qtime(t,self.share,self.share+.48)
        if self.share<=t<self.share+.52:
            ax,ay=faces['verte']
            bx,by=faces['rouge']
            x=ax+(bx-ax)*transfer
            y=ay+52+(by-ay)*transfer-102*math.sin(math.pi*transfer)
            self.morsel(draw,x,y,1.05)
        for i in range(4):
            q=(t-self.buffet-1.1-i*.44)/2.8
            if 0<q<1:
                x,y=faces['verte']
                self.puff(layer,x+63,y-55-126*q,q,.67)

    def breakfast_gesture(self,layer,t,faces):
        d=ImageDraw.Draw(layer)
        phase=qtime(t,self.breakfast+.36,self.breakfast+.91)
        x,y=faces['lea']
        draw_arm(layer,(x+50,y+175),1,
                 {'longueur':132,'epaisseur':22,'peau':'#BE936F','manche':'#B56E55','trait':.12},
                 -15-143*phase,-6*phase,'poing')
        fx,fy=faces['ami']
        for i in range(3):
            q=(t-self.breakfast-i*.36)/1.45
            if 0<q<1:
                self.puff(layer,fx+26,fy+47,q,1.20)
        # La table masque les mains de repos et laisse les gestes au niveau des visages.
        d.rounded_rectangle((42,1411,1038,1492),radius=13,fill='#CDA57D',outline='#6D383B',width=6)
        d.rectangle((74,1484,98,1920),fill='#6D5F5A',outline='#6D383B',width=4)
        d.rectangle((984,1484,1008,1920),fill='#6D5F5A',outline='#6D383B',width=4)
        for x in (296,790):
            d.ellipse((x-111,1419,x+111,1470),fill='#FFF9ED',outline='#6D383B',width=4)
            d.ellipse((x-87,1428,x+87,1460),outline='#B3C2CC',width=3)
            d.polygon([(x-38,1444),(x+9,1429),(x+48,1450)],fill='#E6BE76',outline='#6D383B',width=2)
            d.line((x-131,1436,x-131,1499),fill='#6D383B',width=5)
            for dx in (-7,0,7):
                d.line((x-131+dx,1417,x-131+dx,1441),fill='#6D383B',width=3)

    def _actor_labels(self,frame,shot,t,placed,view):
        faces={a['name']:a['face'] for a in placed}
        layer=Image.new('RGBA',frame.size)
        if shot['id']=='reveil':
            self.brain_gesture(layer,t,faces['cerveau'])
        elif shot['id']=='buffet':
            self.microbe_meal(layer,t,faces)
        elif shot['id']=='petit-dejeuner':
            self.breakfast_gesture(layer,t,faces)
        if view!=(0,0,1080,1920):
            layer=layer.crop(view).resize(frame.size,Image.Resampling.LANCZOS)
        frame.alpha_composite(layer)
        super()._actor_labels(frame,shot,t,placed,view)


def main():
    parser=ArgumentParser()
    parser.add_argument('--apercu',action='store_true')
    args=parser.parse_args()
    e=Episode009()
    OUT.mkdir(exist_ok=True)
    e.save_subtitles(OUT)
    montage={'duree':e.duration,
             'moments':{'reveil':{'étirement':.4},'buffet':{'impact':e.bite,'partage':e.share},
                        'petit-dejeuner':{'réaction':e.breakfast+.78},'cabinet':{'cta':e.lines[-1]['t0']}},
             'scenes':[{'id':s['id'],'debut':s['t0'],'fin':s['t1']} for s in e.shots],
             'repliques':[{k:l[k] for k in ('qui','dit','t0','t1')} for l in e.lines]}
    (OUT/'montage.json').write_text(json.dumps(montage,ensure_ascii=False,indent=2)+'\n')
    print(f'{e.duration:.2f} s · {len(e.lines)} prises · petit-déjeuner {e.breakfast:.2f} s · cabinet {e.office:.2f} s',flush=True)
    if args.apercu:
        e.preview(OUT,[.4,e.buffet+.9,e.share+.21,e.breakfast+.9,e.reply+.65,e.office+.8,e.lines[-1]['t0']+.8])
        return
    issues=e.controle(OUT)
    if issues:
        raise SystemExit('\n'.join(issues))
    e.render(OUT/'image-et-voix.mp4',preview_every=300)

if __name__=='__main__':
    main()
