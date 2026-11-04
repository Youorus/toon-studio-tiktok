"""Porte articulée, contacts liés aux personnages, arcs continus et sons sur les gestes."""
from argparse import ArgumentParser
import json
import math
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from PIL import Image, ImageDraw

from toonstudio.drawing import clamp, ease_in_out, font
from toonstudio.episode import action_track
from toonstudio.sous_titres import CaptionedEpisode

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'out'
INK='#6D383B'

def q(t,a,b):
    return ease_in_out(clamp((t-a)/(b-a)))

def fluid(beats):
    times=np.array([p[0] for p in beats]);values=np.array([p[1:] for p in beats])
    f=PchipInterpolator(times,values)
    sample=np.unique(np.r_[times,np.arange(times[0],times[-1],1/60)])
    return action_track([dict(t=float(t),dx=float(v[0]),dy=float(v[1]),angle=float(v[2]),echelle=float(v[3]),courbe='lineaire')
                         for t,v in zip(sample,f(sample))],'action continue')

def limb(layer,start,end,bend=20):
    """Bras en deux segments et main pleine ; poignet fixé au point de contact."""
    sx,sy=start;tx,ty=end
    elbow=((sx+tx)/2-bend,(sy+ty)/2+27)
    d=ImageDraw.Draw(layer)
    for points,fill,width in (((start,elbow),'#59A5CF',28),((elbow,end),'#F1A96E',18)):
        d.line(points,fill=INK,width=width+6,joint='curve')
        d.line(points,fill=fill,width=width,joint='curve')
        for x,y in points:
            r=width/2;d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=INK,width=2)
    d.ellipse((tx-12,ty-18,tx+12,ty+18),fill='#F1A96E',outline=INK,width=3)
    d.line((tx-3,ty-11,tx-3,ty+10),fill=INK,width=2)

class Episode010(CaptionedEpisode):
    def __init__(self):
        super().__init__(ROOT)
        self.room=next(s for s in self.shots if s['id']=='sortie')
        self.dialogue=[l for l in self.lines if l['shot']=='sortie']
        self.open=self.dialogue[1]['t0']+.24
        self.contact=self.dialogue[2]['t0']+.28
        self.push=self.dialogue[3]['t0']+.28
        self.mark=self.dialogue[5]['t0']+.62
        self.release=self.dialogue[6]['t0']+self.dialogue[6]['parole']-.05
        self.actions[('sortie','caca')]=fluid([
            (0,-90,18,-5,1),(.42,-27,-12,3,1.02),(.80,0,0,0,1),
            (self.open+.12,0,0,0,1),(self.contact-.10,70,-3,6,1),
            (self.contact,92,0,9,.97),(self.contact+.13,77,-8,-4,1.02),
            (self.contact+.40,87,0,0,1),(self.push+.28,93,2,2,1),
            (self.push+.55,86,0,0,1),(self.release-.28,86,0,-2,1),
            (self.release,99,-8,5,.96),(self.release+.22,151,4,13,.89),
            (self.release+.45,180,35,21,.70)])
        self.actions[('sortie','policier')]=fluid([
            (0,0,0,0,1),(self.open,0,0,-2,1),(self.open+.38,0,0,0,1),
            (self.push-.38,0,0,0,1),(self.push-.05,60,-3,5,1),
            (self.push+.22,92,5,10,1),(self.push+.53,75,1,4,1),
            (self.push+.85,65,0,0,1),(self.mark-.28,65,0,0,1),
            (self.mark+.40,82,-3,3,1),(self.mark+1.1,65,0,0,1),
            (self.release-.28,65,0,-4,1),(self.release,103,5,12,1),
            (self.release+.22,143,-9,17,1),(self.release+.45,104,0,-3,1)])
        self.passage=next(s for s in self.shots if s['id']=='passage')
        end=self.passage['t1']-self.passage['t0']
        self.actions[('passage','caca')]=fluid([
            (0,0,-240,-7,1),(.19,0,-180,-3,1),(.53,0,145,8,.95),
            (max(.80,end-.08),0,870,21,.58)])
        self.markers={'sortie':{'ouverture':self.open,'impact':self.contact,'poussee':self.push,
                              'marqueur':self.mark,'liberation':self.release},
                      'passage':{'chute':self.passage['t1']-.14},
                      'cabinet':{'cta':self.lines[-1]['t0']}}
        self.sound(1,'glisse',self.open)
        self.sound(2,'toc',self.contact)
        self.sound(3,'toc',self.push+.22)
        self.sound(5,'glisse',self.mark+.16)
        self.sound(6,'glisse',self.release)
        p=next(l for l in self.lines if l['shot']=='passage');p['sfx']=[f'ploc@{end-.14:.4f}']
        self.lines[-1]['sfx']=['ploc@0.12']
        self.signature=self.niche['direction_artistique']['signature']['positions']
        self.clinic_signature=[[x,180+round(y*.18)] for x,y in self.signature]

    def sound(self,index,name,time):
        line=self.dialogue[index]
        line.setdefault('sfx',[]).append(f'{name}@{max(0,time-line["t0"]):.4f}')

    def _watermark(self,frame,t):
        self.niche['direction_artistique']['signature']['positions']=(
            self.clinic_signature if t>=self.passage['t1'] else self.signature)
        super()._watermark(frame,t)

    def actor_state(self,shot,name,spec,t,line,prev_lines):
        state=super().actor_state(shot,name,spec,t,line,prev_lines)
        if shot['id']=='sortie':
            if name=='caca':
                if t>=self.contact: state['emo']='douleur' if line['qui']!='caca' else line['emotion']
                if self.contact<=t<self.contact+.20:state['blink']=True
            elif name=='policier' and self.push-.38<=t<self.room['t1']:
                state['pose']='travail'
        return state

    def _place_actors(self,shot,lines,li,line,t,chars):
        placed=super()._place_actors(shot,lines,li,line,t,chars)
        if shot['id']=='passage':
            # Sortie volontaire par le bas de la coupe anatomique.
            for actor in placed:
                actor['sortant']=t>shot['t0']+.60
                # Même marque que sur le plan précédent, à l'échelle du corps en chute.
                image=actor['img'].copy();draw=ImageDraw.Draw(image)
                fx=actor['face'][0]-actor['pos'][0];fy=actor['face'][1]-actor['pos'][1]
                k=actor['face_r']/(52*1.10)
                for dx,dy in ((-83,106),(-48,134)):
                    draw.line((fx+dx*k,fy+dy*k,fx+(dx+9)*k,fy+(dy+53)*k),fill='#D45C58',width=max(3,round(8*k)))
                actor['img']=image
        if shot['id']=='sortie':
            # Le battant reste derrière les acteurs. Son pivot est sur la charnière gauche.
            layer=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(layer)
            angle=q(t,self.open-.10,self.open+.60)
            width=round(356*(1-.91*angle));height=623
            d.rounded_rectangle((541,773,541+width,773+height),radius=min(100,max(12,width//3)),
                                fill='#F1B478',outline=INK,width=7)
            if width>75:
                d.line((541+width*.48,790,541+width*.48,1380),fill='#B77657',width=3)
                d.ellipse((541+width-43,1076,541+width-29,1091),fill=INK)
            decor={'name':'battant','img':layer,'pos':(0,0),'face':(0,0),'face_r':0,'sortant':True}
            placed.insert(0,decor)
            for actor in placed:
                if actor['name']=='caca' and t>self.mark+.12:
                    image=actor['img'].copy();draw=ImageDraw.Draw(image)
                    fx=actor['face'][0]-actor['pos'][0];fy=actor['face'][1]-actor['pos'][1]
                    progress=q(t,self.mark+.12,self.mark+.80)
                    for dx,dy in ((-83,106),(-48,134)):
                        draw.line((fx+dx,fy+dy,fx+dx+9*progress,fy+dy+53*progress),fill='#D45C58',width=8)
                    actor['img']=image
                if actor['name']=='caca' and t>self.release+.12:actor['sortant']=True
        return placed

    def _actor_labels(self,frame,shot,t,placed,view):
        if shot['id']=='sortie':
            faces={a['name']:a['face'] for a in placed}
            fx,fy=faces['policier'];cx,cy=faces['caca']
            layer=Image.new('RGBA',frame.size);d=ImageDraw.Draw(layer)
            if self.push-.38<=t<self.room['t1']:
                reaching=q(t,self.push-.38,self.push+.10)*(1-q(t,self.release+.08,self.release+.40))
                if self.mark-.18<t<self.mark+1.10:
                    stroke=q(t,self.mark,self.mark+.66)
                    target=(cx-83+9*stroke,cy+106+53*stroke)
                    limb(layer,(fx+43,fy+150),target,-15)
                    d.line((target[0]-8,target[1]-33,target[0]+2,target[1]+9),fill=INK,width=14)
                    d.line((target[0]-8,target[1]-33,target[0]+2,target[1]+9),fill='#D45C58',width=8)
                    limb(layer,(fx-69,fy+158),(fx-48,fy+212),-7)
                else:
                    for offset,shoulder in ((0,(fx+43,fy+150)),(36,(fx-69,fy+158))):
                        rest=(shoulder[0]+12,shoulder[1]+68)
                        target=(cx-176,cy+132+offset)
                        end=tuple(a+(b-a)*reaching for a,b in zip(rest,target))
                        limb(layer,shoulder,end,22)
                # Une petite goutte d'effort, attachée au front du gardien.
                d.ellipse((fx-59,fy-17,fx-44,fy+6),fill='#91D3DF',outline=INK,width=2)
            if self.contact<=t<self.contact+.24:
                u=(t-self.contact)/.24
                for k in range(3):
                    x=cx+144+k*14; y=cy-56+k*26
                    d.line((x,y,x+19*(1-u),y-15*(1-u)),fill='#FFF9ED',width=5)
            # Le cadre avant cache la selle pendant sa sortie, avec une ouverture de tissu.
            if t>self.release-.08:
                fade=q(t,self.release-.08,self.release+.48)
                d.rounded_rectangle((899,789,944,1415),radius=15,fill='#9D454C',outline=INK,width=5)
                if fade>.60:
                    veil=Image.new('RGBA',frame.size)
                    ImageDraw.Draw(veil).rectangle((835,778,947,1422),fill=(157,69,76,round(255*(fade-.60)/.40)))
                    layer.alpha_composite(veil)
            if view!=(0,0,1080,1920):layer=layer.crop(view).resize(frame.size,Image.Resampling.LANCZOS)
            frame.alpha_composite(layer)
        super()._actor_labels(frame,shot,t,placed,view)

def main():
    parser=ArgumentParser();parser.add_argument('--apercu',action='store_true');args=parser.parse_args()
    e=Episode010();OUT.mkdir(exist_ok=True);e.save_subtitles(OUT)
    montage={'duree':e.duration,'moments':e.markers,
             'scenes':[{'id':s['id'],'debut':s['t0'],'fin':s['t1']} for s in e.shots],
             'repliques':[{k:l[k] for k in ('qui','dit','t0','t1')} for l in e.lines]}
    (OUT/'montage.json').write_text(json.dumps(montage,ensure_ascii=False,indent=2)+'\n')
    print(f'{e.duration:.2f} s · {len(e.lines)} prises · 0 génération Recraft',flush=True)
    if args.apercu:
        e.preview(OUT,[.40,e.open+.35,e.contact+.08,e.push+.22,e.mark+.38,e.release+.17,
                       e.passage['t0']+.38,e.passage['t1']+.65,e.lines[-3]['t0']+.9,e.lines[-1]['t0']+.8])
    else:
        issues=e.controle(OUT)
        if issues:raise SystemExit('\n'.join(issues))
        e.render(OUT/'image-et-voix.mp4',preview_every=240)

if __name__=='__main__':main()
