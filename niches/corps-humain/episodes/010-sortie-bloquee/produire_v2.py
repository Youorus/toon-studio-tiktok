"""Révision de mise en scène : marche, blocage, poussées, marqueur, glissade, sang et réaction."""
from argparse import ArgumentParser
import json
import math
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import numpy as np
from scipy.interpolate import PchipInterpolator
from PIL import Image,ImageDraw

from toonstudio.drawing import clamp,ease_in_out,affine_paste
from toonstudio.episode import action_track
from toonstudio.sous_titres import CaptionedEpisode

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'out'
INK='#181313'
BLOOD='#D63748'

def q(t,a,b):return ease_in_out(clamp((t-a)/(b-a)))

def fluid(beats):
    ts=np.array([p[0] for p in beats]);f=PchipInterpolator(ts,[p[1:] for p in beats])
    at=np.unique(np.r_[ts,np.arange(ts[0],ts[-1],1/60)])
    return action_track([dict(t=float(t),dx=float(v[0]),dy=float(v[1]),angle=float(v[2]),echelle=float(v[3]),courbe='lineaire')
                         for t,v in zip(at,f(at))],'mouvement V2')

def arm(layer,shoulder,wrist,bend=1):
    """Deux segments de longueur stable : le coude plie, la paume reste au contact."""
    sx,sy=shoulder;tx,ty=wrist;dx,dy=tx-sx,ty-sy
    distance=max(.1,math.hypot(dx,dy));length=max(92,distance/2+.1)
    rise=math.sqrt(max(0,length*length-(distance/2)**2))
    elbow=((sx+tx)/2-dy/distance*rise*bend,(sy+ty)/2+dx/distance*rise*bend)
    d=ImageDraw.Draw(layer)
    for a,b,color,w in ((shoulder,elbow,'#59A5CF',21),(elbow,wrist,'#F1A96E',14)):
        d.line((a,b),fill=INK,width=w+4,joint='curve');d.line((a,b),fill=color,width=w,joint='curve')
        r=w/2
        for x,y in (a,b):d.ellipse((x-r,y-r,x+r,y+r),fill=color,outline=INK,width=2)
    d.rounded_rectangle((tx-10,ty-17,tx+10,ty+17),radius=8,fill='#F1A96E',outline=INK,width=2)
    for yy in (-5,2,9):d.line((tx-5,ty+yy,tx+5,ty+yy),fill='#805045',width=1)

class Episode010V2(CaptionedEpisode):
    def __init__(self):
        super().__init__(ROOT)
        self.byshot={s['id']:s for s in self.shots}
        self.room=self.byshot['sortie'];self.dialogue=[l for l in self.lines if l['shot']=='sortie']
        self.open=self.dialogue[1]['t0']+.20
        self.contact=self.dialogue[2]['t0']+.22
        self.push=self.dialogue[3]['t0']+.12
        self.mark=self.dialogue[5]['t0']+self.dialogue[5]['parole']+.04
        self.release=min(self.dialogue[6]['t0']+self.dialogue[6]['parole']-.15,self.room['t1']-.55)
        self.actions[('sortie','caca')]=fluid([
            (0,218,8,-4,1),(.34,196,-4,2,1),(1.50,27,0,0,1),
            (self.open+.13,0,0,0,1),(self.contact-.12,-13,0,3,1),
            (self.contact,0,3,6,1),(self.contact+.13,-17,-10,-4,1),
            (self.contact+.40,-6,0,0,1),(self.push+.16,8,2,3,1),
            (self.push+.43,14,4,2,1),(self.push+.72,-5,0,0,1),
            (self.mark-.15,-5,0,0,1),(self.mark+1.06,-5,0,0,1),
            (self.release-.22,-8,3,-3,1),(self.release,18,-5,7,1),
            (self.release+.13,59,-16,13,1),(self.release+.42,134,18,19,1)])
        self.actions[('sortie','policier')]=fluid([
            (0,0,0,0,1),(self.open,0,0,-1,1),(self.open+.30,0,0,0,1),
            (self.push-.38,0,0,0,1),(self.push,50,-3,4,1),
            (self.push+.22,74,4,8,1),(self.push+.56,64,0,2,1),
            (self.push+.85,61,0,0,1),(self.mark-.28,61,0,0,1),
            (self.mark+.50,69,-2,2,1),(self.mark+1.13,61,0,0,1),
            (self.release-.28,61,0,-3,1),(self.release,89,4,10,1),
            (self.release+.18,113,-5,13,1),(self.release+.47,86,0,-2,1)])
        route=json.loads((ROOT/'art/v2/trajet-coupe.json').read_text())
        center=PchipInterpolator(route['y'],route['x'])
        duration=self.byshot['passage']['t1']-self.byshot['passage']['t0']
        times=np.array([0,.20,.52,.91,1.31,1.72,duration-.04])
        heights=np.array([330,395,650,1030,1370,1680,2140])
        beats=[]
        for t,y in zip(times,heights):
            angle=float(np.clip(-math.degrees(math.atan(float(center.derivative()(y))))*.6,-23,23))
            beats.append((float(t),float(center(y))-520,float(y+145-1120),angle,1))
        self.actions[('passage','caca')]=fluid(beats)
        self.actions[('cuvette','caca')]=fluid([(0,0,12,-20,1),(.20,0,-5,-17,1),(.55,0,1,-18,1),
            (max(.9,self.byshot['cuvette']['t1']-self.byshot['cuvette']['t0']-.02),0,0,-18,1)])
        self.markers={'sortie':{'ouverture':self.open,'impact':self.contact,'poussee':self.push,
                              'marqueur':self.mark,'liberation':self.release},
                      'passage':{'chute':self.byshot['passage']['t1']-.12},
                      'cuvette':{'réaction':self.byshot['cuvette']['t0']+.15},
                      'cabinet':{'cta':self.lines[-1]['t0']}}
        for index,name,at in ((1,'glisse',self.open),(2,'toc',self.contact),(3,'boing',self.push+.22),
                             (5,'glisse',self.mark),(6,'glisse',self.release-.06)):
            self.sound(self.dialogue[index],name,at)
        self.sound(next(l for l in self.lines if l['shot']=='passage'),'ploc',self.markers['passage']['chute'])
        self.sound(next(l for l in self.lines if l['shot']=='passage'),'glissade',self.byshot['passage']['t0']+.08)
        self.lines[-1]['sfx']=['ploc@0.12']
        self.signature=self.niche['direction_artistique']['signature']['positions']
        self.clinic_signature=[[x,180+round(y*.18)] for x,y in self.signature]
        self.stool=Image.open(ROOT/'personnages/caca-coupe-v2/corps.png').convert('RGBA')

    @staticmethod
    def sound(line,name,at):line.setdefault('sfx',[]).append(f'{name}@{max(0,at-line["t0"]):.4f}')

    def _watermark(self,frame,t):
        self.niche['direction_artistique']['signature']['positions']=(
            self.clinic_signature if t>=self.byshot['cuvette']['t0'] else self.signature)
        super()._watermark(frame,t)

    def _motion(self,name,spec,lines,li,t):
        x,y,walk,facing=super()._motion(name,spec,lines,li,t)
        if lines[0]['shot']=='sortie' and name=='caca':
            walk=1.0 if .05<t<self.contact-.20 else 0.0
            facing=-1 if t<self.contact-.20 else 1
        return x,y,walk,facing

    def actor_state(self,shot,name,spec,t,line,prev_lines):
        state=super().actor_state(shot,name,spec,t,line,prev_lines)
        if shot['id']=='sortie':
            if name=='caca':
                if t>self.contact:
                    state['gaze']=(.65,.05)
                    if line['qui']!='caca':state['emo']='inquiet'
                if self.contact<t<self.contact+.14 or self.push+.04<t<self.push+.26 or self.release-.04<t<self.release+.16:
                    state['emo']='douleur';state['blink']=False
                if t>=self.mark:
                    index=min(24,int(clamp((t-self.mark)/1.06)*24));state['pose']=f'marque-{index:02d}'
                elif line['qui']=='caca' and t<self.contact:state['pose']='hausse'
            elif name=='policier' and t>=self.push-.38:
                if self.mark-.15<t<self.mark+1.14:state['pose']='marqueur'
                elif self.push-.38<t<self.push+1.0 or self.dialogue[6]['t0']-.20<t<self.release+.43:state['pose']='travail'
                else:state['pose']='defaut'
                if self.push<t<self.push+.28 or self.release-.04<t<self.release+.15:
                    state['emo']='douleur';state['blink']=False
                elif line['qui']=='policier':state['emo']=line['emotion']
        elif shot['id']=='toilettes':
            state['gaze']=(-.8,.6)
        elif shot['id']=='cuvette':
            state['emo']='inquiet';state['gaze']=(.2,-.6)
        return state

    @staticmethod
    def decor(layer,name):return {'name':name,'img':layer,'pos':(0,0),'face':(0,0),'face_r':0,'sortant':True}

    def _place_actors(self,shot,lines,li,line,t,chars):
        placed=super()._place_actors(shot,lines,li,line,t,chars)
        if shot['id']=='sortie':
            # CACA au fond, gardien devant, comme au contact dans la référence.
            placed.sort(key=lambda a:0 if a['name']=='caca' else 1)
            layer=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(layer)
            opening=q(t,self.open-.06,self.open+.58);width=round(365*(1-.92*opening))
            d.rounded_rectangle((449,774,449+width,1413),radius=min(133,max(9,width//3)),fill='#E9B77F',outline='#6D383B',width=4)
            if width>70:
                d.line((449+width*.52,789,449+width*.52,1400),fill='#AD785A',width=2)
                d.ellipse((449+width-42,1080,449+width-28,1094),fill='#6D383B')
            placed.insert(0,self.decor(layer,'porte'))
            for actor in placed:
                if actor['name']=='caca' and t>self.release+.05:
                    alpha=1-q(t,self.release+.08,self.release+.43)
                    image=actor['img'].copy();image.putalpha(image.getchannel('A').point(lambda v:round(v*alpha)))
                    actor['img']=image;actor['sortant']=True
        elif shot['id']=='passage':
            for actor in placed:actor['sortant']=t>shot['t0']+.25
        elif shot['id']=='cuvette':
            layer=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(layer)
            s=t-shot['t0']
            d.ellipse((233,692,860,1450),fill=(214,55,72,110))
            d.arc((237,719,846,1470),50,160,fill=(214,55,72,170),width=23)
            d.arc((269,756,838,1420),235,305,fill=(214,55,72,185),width=19)
            for k in range(4):
                r=(s*.6+k*.24)%1;rx=230+170*r;ry=270+200*r
                d.ellipse((550-rx,1070-ry,550+rx,1070+ry),outline=(214,55,72,round(65*(1-r))),width=6)
            placed.insert(0,self.decor(layer,'eau-rouge'))
        elif shot['id']=='toilettes':
            layer=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(layer)
            d.ellipse((80,1173,485,1258),fill=(214,55,72,76))
            affine_paste(layer,self.stool,(196,230),(280,1218),-13,sx=.30,sy=.13)
            placed.insert(0,self.decor(layer,'caca-dans-cuvette'))
        return placed

    def _actor_labels(self,frame,shot,t,placed,view):
        if shot['id']=='sortie':
            faces={a['name']:a['face'] for a in placed};fx,fy=faces['policier'];cx,cy=faces['caca']
            layer=Image.new('RGBA',frame.size);d=ImageDraw.Draw(layer)
            if t>=self.push-.38:
                first=q(t,self.push-.38,self.push+.06)*(1-q(t,self.push+.58,self.push+1.0))
                last=q(t,self.dialogue[6]['t0']-.20,self.dialogue[6]['t0']+.12)*(1-q(t,self.release+.09,self.release+.43))
                reach=max(first,last)
                if self.mark-.15<t<self.mark+1.14:
                    progress=clamp((t-self.mark)/1.06)*3
                    stroke=min(2,int(progress));part=progress-stroke
                    x,y=((66,265),(94,293),(124,316))[stroke]
                    target=(cx+(x-218+9*part)*1.1,cy+(y-279.6+94*part)*1.1)
                    arm(layer,(fx+44,fy+140),target,1)
                    d.line((target[0]-13,target[1]-36,target[0]+1,target[1]+10),fill=INK,width=12)
                    d.line((target[0]-13,target[1]-36,target[0]+1,target[1]+10),fill=BLOOD,width=7)
                elif reach>0:
                    for rear in (True,False):
                        shoulder=(fx+(-70+55*reach if rear else 44),fy+(144 if rear else 140))
                        rest=(shoulder[0]+8,shoulder[1]+66)
                        target=(cx-194,cy+(112 if rear else 74))
                        end=tuple(a+(b-a)*reach for a,b in zip(rest,target))
                        arm(layer,shoulder,end,1)
                if self.push-.1<t<self.push+.65 or self.release-.2<t<self.release+.2:
                    d.ellipse((fx-62,fy-16,fx-48,fy+7),fill='#91D3DF',outline='#6D383B',width=2)
            if self.contact<t<self.contact+.22:
                r=1-(t-self.contact)/.22
                for k in range(3):
                    xx=cx+165+k*14;yy=cy-37+k*23;d.line((xx,yy,xx+21*r,yy-13*r),fill='#FFF9ED',width=4)
            if view!=(0,0,1080,1920):layer=layer.crop(view).resize(frame.size,Image.Resampling.LANCZOS)
            frame.alpha_composite(layer)
        super()._actor_labels(frame,shot,t,placed,view)

def main():
    parser=ArgumentParser();parser.add_argument('--apercu',action='store_true');parser.add_argument('--remixer-audio',action='store_true');args=parser.parse_args()
    episode=Episode010V2();OUT.mkdir(exist_ok=True);episode.save_subtitles(OUT)
    montage={'revision':'V2','duree':episode.duration,'moments':episode.markers,
             'scenes':[{'id':s['id'],'debut':s['t0'],'fin':s['t1']} for s in episode.shots],
             'repliques':[{k:l[k] for k in ('qui','dit','t0','t1')} for l in episode.lines]}
    (OUT/'montage.json').write_text(json.dumps(montage,ensure_ascii=False,indent=2)+'\n')
    print(f'V2 · {episode.duration:.2f} s · {len(episode.lines)} prises',flush=True)
    if args.remixer_audio:
        existing=OUT/'image-et-voix-V2.mp4'
        with TemporaryDirectory(dir=OUT) as temp:
            temp=Path(temp)
            subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',str(existing),'-map','0:v:0','-an','-c:v','copy',str(temp/'v.mp4')],check=True)
            episode._encode(temp,temp/'nouveau-mix.mp4')
            (temp/'nouveau-mix.mp4').replace(existing)
    elif args.apercu:
        episode.preview(OUT,[.4,episode.open+.35,episode.contact+.10,episode.push+.20,
            episode.mark+.22,episode.release+.13,episode.byshot['passage']['t0']+.65,
            episode.byshot['cuvette']['t0']+.30,episode.byshot['toilettes']['t0']+.80,
            episode.byshot['cabinet']['t0']+.8,episode.lines[-1]['t0']+.80])
    else:
        issues=episode.controle(OUT)
        if issues:raise SystemExit('\n'.join(issues))
        episode.render(OUT/'image-et-voix-V2.mp4',preview_every=240)

if __name__=='__main__':main()
