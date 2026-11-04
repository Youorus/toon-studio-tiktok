"""Mise en scène de l'arrivage, de l'appel partagé et de la consultation."""
from argparse import ArgumentParser
import json
import math
from pathlib import Path
import random

from PIL import Image, ImageChops, ImageDraw

from toonstudio.drawing import affine_paste, clamp, ease_in_out, transform_point
from toonstudio.episode import action_track
from toonstudio.sous_titres import CaptionedEpisode

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'out'
INK='#6D383B'
PINK='#EF9695'
METAL='#FFF9ED'
STOMACH_POCKET=[(638,950),(953,950),(943,1000),(924,1080),(892,1145),(858,1192),
                (803,1250),(731,1304),(650,1333),(565,1352),(445,1354),(330,1331),
                (239,1313),(204,1290),(234,1262),(338,1250),(435,1240),(509,1213),
                (563,1164),(596,1106),(624,1043)]


def eased(t,start,end):
    return ease_in_out(clamp((t-start)/(end-start)))


def split_point(x,y):
    return (x-210)*1080/850,846+(y-440)*1074/950


def utensil(layer,wrist,angle,kind):
    d=ImageDraw.Draw(layer)
    tip=transform_point((0,-94),(0,0),wrist,angle)
    d.line((wrist,tip),fill=INK,width=12)
    d.line((wrist,tip),fill=METAL,width=6)
    if kind=='fourchette':
        for dx in (-13,0,13):
            a=transform_point((dx,-92),(0,0),wrist,angle)
            b=transform_point((dx,-121),(0,0),wrist,angle)
            d.line((a,b),fill=INK,width=8)
            d.line((a,b),fill=METAL,width=4)
        d.line([transform_point((x,-92),(0,0),wrist,angle) for x in (-13,13)],fill=INK,width=9)
    else:
        points=[transform_point(p,(0,0),wrist,angle) for p in ((-5,-54),(17,-78),(15,-119),(0,-120))]
        d.polygon(points,fill=METAL,outline=INK,width=3)


def arm(layer,shoulder,elbow,wrist,tone=PINK):
    d=ImageDraw.Draw(layer)
    d.line((shoulder,elbow,wrist),fill=INK,width=22,joint='curve')
    d.line((shoulder,elbow,wrist),fill=tone,width=14,joint='curve')
    x,y=wrist
    d.ellipse((x-12,y-9,x+12,y+9),fill=tone,outline=INK,width=3)


class Episode008(CaptionedEpisode):
    def __init__(self):
        super().__init__(ROOT)
        self.assets={n:Image.open(ROOT/'art'/f'{n}.png').convert('RGBA')
                     for n in ('burger','frites','poulet','sac','soda','telephone')}
        arr=[line for line in self.lines if line['shot']=='arrivage']
        self.call=next(s['t0'] for s in self.shots if s['id']=='appel')
        self.office=next(s['t0'] for s in self.shots if s['id']=='cabinet')
        positions=self.niche['direction_artistique']['signature']['positions']
        self.anatomy_positions=positions
        self.clinic_positions=[[x,180+round(y*.18)] for x,y in positions]
        self.fries=arr[1]['t0']+.60
        self.chicken=arr[2]['t0']+.23
        self.soda=arr[3]['t0']+.18
        self.ring=max(arr[-1]['t0']+.5,self.call-.61)
        self.foods=self.food_cues(arr)
        self.pocket_masks={}
        for split in (False,True):
            mask=Image.new('L',(1080,1920))
            points=[split_point(x,y) for x,y in STOMACH_POCKET] if split else STOMACH_POCKET
            ImageDraw.Draw(mask).polygon(points,fill=255)
            self.pocket_masks[split]=mask
        for line,sfx in zip(arr,(['ploc@1.29'],['glisse@0.09','ploc@1.36'],['ploc@0.99'],
                                 ['plouf@1.08'],[f"ring@{self.ring-arr[-1]['t0']:.3f}"])):
            line['sfx']=sfx
        self.lines[len(arr)]['sfx']=['ring@0.07']
        self.moves('arrivage','estomac',(.17,0,0,0,1),(.44,1,-10,-4,1.06),(1.05,0,0,0,1),
                   (self.chicken-.12,0,0,0,1),(self.chicken+.34,1,-8,4,1.08),
                   (self.chicken+.71,0,0,0,1))
        self.moves('appel','cerveau',(0,0,0,-5,.93),(.32,0,-8,2,1.05),(.75,0,0,0,1))

    def food_cues(self,arr):
        rng=random.Random(821)
        events=[('burger',arr[1]['t0']-.15,426,1291),
                ('burger',arr[1]['t0']+.46,567,1310)]
        for i in range(7):
            events.append(('frites',self.fries+i*.24,482+(i%4)*78,1260-(i//4)*43))
        for i in range(5):
            events.append(('poulet',self.chicken+i*.25,566+(i%4)*75,1206-(i//4)*55))
        for i in range(6):
            events.append(('burger',self.soda+1.4+i*.25,553+(i%5)*67,1176-(i//5)*65))
        return [(name,t,x+rng.randrange(-14,15),y+rng.randrange(-12,13),rng.randrange(-31,32),
                 rng.uniform(.31,.40)) for name,t,x,y in events]

    def moves(self,shot,actor,*keys):
        self.actions[(shot,actor)]=action_track(
            (dict(t=t,dx=x,dy=y,angle=a,echelle=z) for t,x,y,a,z in keys),actor)

    def _watermark(self,frame,t):
        self.niche['direction_artistique']['signature']['positions']=(
            self.clinic_positions if t>=self.office else self.anatomy_positions)
        super()._watermark(frame,t)

    def place(self,layer,name,x,y,angle,scale):
        img=self.assets[name]
        affine_paste(layer,img,(img.width/2,img.height/2),(x,y),angle,sx=scale,sy=scale)

    def pile(self,layer,t,split=False):
        # Le liquide monte autour de l'arrivage, dans la poche et en dessous du visage.
        rise=eased(t,self.soda,self.soda+2.0)
        if split or rise>.015:
            level=1235-206*rise
            wave=[(x,level+9*math.sin(t*4+x/92)) for x in range(145,1050,25)]
            points=wave+[(1045,1440),(145,1440)]
            if split:
                points=[split_point(x,y) for x,y in points]
            liquid=Image.new('RGBA',layer.size)
            d=ImageDraw.Draw(liquid)
            d.polygon(points,fill=(208,117,95,145))
            d.line(points[:-2],fill=(255,186,153,205),width=6)
            liquid.putalpha(ImageChops.multiply(liquid.getchannel('A'),self.pocket_masks[split]))
            layer.alpha_composite(liquid)
        d=ImageDraw.Draw(layer)
        for name,start,x,y,angle,scale in self.foods:
            if t<start:
                continue
            if split:
                self.place(layer,name,*split_point(x,y),angle,scale*.94)
                continue
            f=clamp((t-start)/.76)
            rx=(1-f)**2*513+2*(1-f)*f*785+f*f*x
            ry=398+(y-398)*f**1.45
            bounce=max(0,t-start-.76)
            ry-=abs(math.sin(bounce*19))*30*math.exp(-bounce*8)
            self.place(layer,name,rx,ry,angle+(1-f)*(-68 if angle<0 else 86),scale*(.8+.2*f))
            if .76<t-start<.96:
                q=(t-start-.76)/.20
                for side in (-1,1):
                    cx=rx+side*(16+q*60)
                    cy=ry-4-82*q*(1-q)
                    r=5*(1-q)
                    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill='#FFF0D3')

    def call_pose(self,layer,actor,face,t):
        fx,fy=face
        pulse=4*math.sin(t*5)
        if actor=='estomac':
            wrist=(fx+158,fy+76+pulse)
            phone=(fx+165,fy+38+pulse)
            arm(layer,(fx+120,fy+135),(fx+172,fy+113),wrist)
            self.place(layer,'telephone',*phone,18,.60)
        else:
            wrist=(fx-225,fy+104+pulse)
            phone=(fx-218,fy+52+pulse)
            arm(layer,(fx-187,fy+155),(fx-242,fy+139),wrist)
            self.place(layer,'telephone',*phone,-17,.69)
        x,y=wrist
        ImageDraw.Draw(layer).ellipse((x-12,y-9,x+12,y+9),fill=PINK,outline=INK,width=3)

    def _actor_labels(self,frame,shot,t,placed,view):
        faces={actor['name']:actor['face'] for actor in placed}
        layer=Image.new('RGBA',frame.size)
        if shot['id']=='arrivage':
            self.pile(layer,t)
            fx,fy=faces['estomac']
            if t<self.ring:
                bite=eased(t,.13,1.19)
                retreat=eased(t,1.25,1.72)
                wrist=(fx-134+77*bite-56*retreat,fy+180-78*bite+51*retreat)
                angle=-28+43*bite-31*retreat
                arm(layer,(fx-102,fy+112),(fx-143,fy+177),wrist)
                utensil(layer,wrist,angle,'fourchette')
                shrink=1-eased(t,1.15,1.41)
                if shrink>.01:
                    tip=transform_point((0,-119),(0,0),wrist,angle)
                    self.place(layer,'burger',*tip,-14+26*bite,.39*shrink)
                wrist=(fx+133,fy+159)
                arm(layer,(fx+116,fy+115),(fx+161,fy+165),wrist)
                utensil(layer,wrist,18,'couteau')
            else:
                self.call_pose(layer,'estomac',faces['estomac'],t)
            soda=t-self.soda
            if 0<soda<1.3:
                q=clamp(soda/.96)
                x=520+188*q
                y=550+558*q**1.5
                self.place(layer,'soda',x,y,-15+108*q,.78*(1-eased(soda,.91,1.30)))
        elif shot['id']=='appel':
            self.pile(layer,t,split=True)
            for actor in ('cerveau','estomac'):
                self.call_pose(layer,actor,faces[actor],t)
        else:
            x,y=695,1242
            self.place(layer,'sac',x,y,-5,.48)
            d=ImageDraw.Draw(layer)
            for sx,sy in ((x-61,y+24),(x+56,y+27)):
                d.ellipse((sx-11,sy-12,sx+11,sy+12),fill='#BE936F',outline='#593F37',width=3)
                d.arc((sx-6,sy-8,sx+6,sy+4),4,160,fill='#593F37',width=2)
        frame.alpha_composite(layer)
        super()._actor_labels(frame,shot,t,placed,view)


def main():
    parser=ArgumentParser()
    parser.add_argument('--apercu',action='store_true')
    args=parser.parse_args()
    e=Episode008()
    OUT.mkdir(exist_ok=True)
    e.save_subtitles(OUT)
    markers={'arrivage':{'impact':e.fries+.76,'poulet':e.chicken+.76,'soda':e.soda+.9,'appel':e.ring},
             'appel':{'partage':e.call},'cabinet':{'cta':e.lines[-1]['t0']}}
    montage={'duree':e.duration,'moments':markers,
             'scenes':[{'id':s['id'],'debut':s['t0'],'fin':s['t1']} for s in e.shots],
             'repliques':[{k:l[k] for k in ('qui','dit','t0','t1')} for l in e.lines]}
    (OUT/'montage.json').write_text(json.dumps(montage,indent=2,ensure_ascii=False)+'\n')
    print(f'{e.duration:.2f} s · {len(e.lines)} prises · appel à {e.call:.2f} s · cabinet à {e.office:.2f} s',flush=True)
    if args.apercu:
        e.preview(OUT,[.49,e.fries+.7,e.chicken+1,e.soda+1.4,e.call+.7,e.office+.8,e.lines[-1]['t0']+.8])
        return
    problems=e.controle(OUT)
    if problems:
        raise SystemExit('\n'.join(problems))
    e.render(OUT/'image-et-voix.mp4',preview_every=300)

if __name__=='__main__':
    main()
