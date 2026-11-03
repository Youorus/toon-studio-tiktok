"""Rendu de la reprise, avec gestes et sons synchronisés sur les prises françaises."""
from argparse import ArgumentParser
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.interpolate import PchipInterpolator

from toonstudio.cards import actor_badge
from toonstudio.episode import action_track
from toonstudio.sous_titres import CaptionedEpisode

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'out'
APPROVED = OUT/'La-bacterie-qui-na-pas-bouge-Le-Corps-Parle-Reprise.mp4'
FINAL = OUT/'La-bacterie-qui-na-pas-bouge-Le-Corps-Parle-Policier.mp4'
W,H = 1080,1920


def pose(t,dx=0,dy=0,angle=0,size=1,curve='douce'):
    return dict(t=t,dx=dx,dy=dy,angle=angle,echelle=size,courbe=curve)


def fluid(keys):
    """Interpole les arcs sans arrêt à chaque pose, en préservant les vrais temps morts."""
    fields=('dx','dy','angle','echelle')
    beats=np.array([key['t'] for key in keys])
    values=[[key[field] for field in fields] for key in keys]
    spline=PchipInterpolator(beats,values)
    samples=np.unique(np.r_[beats,np.arange(beats[0],beats[-1],1/60)])
    return [pose(float(t),*map(float,p),curve='lineaire') for t,p in zip(samples,spline(samples))]


def follow_through(keys):
    beats,angles=zip(*keys)
    curve=PchipInterpolator(beats,angles)
    return lambda elapsed: float(curve(np.clip(elapsed,beats[0],beats[-1])))


class Reprise(CaptionedEpisode):
    def __init__(self, approved_audio=None):
        super().__init__(ROOT)
        self.approved_audio=approved_audio
        self.starts = {s['id']:s['t0'] for s in self.shots}
        self.by_shot = {name:[line for line in self.lines if line['shot']==name] for name in self.starts}
        self.moments={}
        self.sign_recoil=follow_through(((-.12,23),(.04,36),(.14,52),(.29,6),
                                         (.41,38),(.55,13),(.72,19),(.88,19),(1.10,-2),(1.32,28),(1.47,23)))
        self.boot_recoil=follow_through(((-.12,0),(.07,11),(.24,27),(.34,-18),
                                         (.43,12),(.61,0),(.86,0),(1.15,-59),(1.33,-71)))
        self.direct()

    def direct(self):
        starts, lines = self.starts,self.by_shot
        def move(shot,name,*keys):
            self.actions[(shot,name)]=action_track(keys,f'{shot}/{name}')
        def animate(shot,name,*keys):
            move(shot,name,*fluid(keys))
        def local(shot,i):
            return lines[shot][i]['t0']-starts[shot]
        def cue(shot,i,word):
            line=lines[shot][i]
            return local(shot,i)+next((a for text,a,_ in line['mots']
                                       if text.casefold().strip('….,!?;:«»')==word.casefold()),.18)
        def sound(shot,i,name,time):
            lines[shot][i].setdefault('sfx',[]).append(f'{name}@{max(0,time-local(shot,i)):.3f}')
        def badge(shot,actor,label,time,length=1.75,color='#503467',dot='#D4A5ED',offset=(0,-150)):
            spec={'acteur':actor,'point':dot,'decalage':offset}
            img=actor_badge(label,color,dot)
            self.mini_badges.setdefault(shot,[]).append((spec,starts[shot]+time,starts[shot]+time+length,img))
        def mark(shot,name,time):
            self.moments.setdefault(shot,{})[name]=starts[shot]+time
        def reactions(shot,i,**mood):
            lines[shot][i]['reactions']=mood

        for shot in ('estomac','prescription'):
            outgoing = local(shot,6)+.85 if shot=='estomac' else 0
            route=[pose(0,-206,-854,13,.55),pose(.38,-216,-780,18,.57),
                   pose(.64,-213,-598,19,.67,'lineaire'),pose(.92,-192,-359,-10,.82),
                   pose(1.14,-89,-134,16,.92),pose(1.31),pose(1.46,14,-35,-11,1.08),pose(1.70)]
            if outgoing:
                route.extend((pose(outgoing),pose(outgoing+.22,-40,-39,-22,.94),
                              pose(outgoing+.56,-160,44,-28,.85),
                              pose(outgoing+.90,-305,146,-31,.68),pose(outgoing+1.17,-454,395,14,.008)))
                sound(shot,6,'glisse',outgoing+.12)
                mark(shot,'sortie',outgoing+.75)
            move(shot,'gelule',*route)
            badge(shot,'gelule','Antibiotique',.40,1.77,'#1E4352','#91D3DF',(185,-117))
            sound(shot,0,'plouf',1.31)
            mark(shot,'impact',1.31)
            move(shot,'estomac',pose(.18),pose(.49,-9,-15,-7,1.11),pose(.93),pose(1.31),
                 pose(1.46,9,-8,7,1.06),pose(1.82))
        reactions('estomac',1,estomac='inquiet')
        reactions('estomac',3,estomac='malicieux')
        reactions('estomac',4,intestin='gene')
        reactions('estomac',5,estomac='fatigue')

        shot='intrusion'
        entry=.17
        hit=cue(shot,2,'pousse-toi')+.18
        stop=cue(shot,0,'stop')
        animate(shot,'violette',pose(0,110,-135,16,.006),pose(entry,110,-135,16,.006),
             pose(entry+.23,102,-118,17,.62),pose(entry+.55,54,-31,-10,.93),pose(entry+.84),
             pose(hit-.44),pose(hit-.22,34,-16,14,.92),pose(hit-.08,-27,-26,-9,1.04),
             pose(hit,-136,-37,-26,1.10),pose(hit+.08,-145,-22,-18,1.07),
             pose(hit+.24,-87,-13,6,1.02),pose(hit+.43,-28,-25,-7),pose(hit+.66))
        animate(shot,'policier',pose(max(.03,stop-.12)),pose(stop+.07,10,-11,7,1.03),pose(stop+.36),
             pose(hit-.10),pose(hit-.026,4,0,4),pose(hit+.043,-11,0,-11,.94),
             pose(hit+.14,-22,-45,-48,.98),pose(hit+.235,-28,-25,-73),
             pose(hit+.34,-29,37,-85,.98),pose(hit+.435,-26,21,-91,.99),
             pose(hit+.575,-23,37,-84,.99),pose(hit+.86,-23,37,-84,.99),
             pose(hit+1.04,-20,22,-58,.95),pose(hit+1.22,-13,31,-16,.91),
             pose(hit+1.35,-10,37,-9,.92),pose(hit+1.51,-10,36,-11,.92))
        badge(shot,'violette','Bactérie',.65,1.65)
        badge(shot,'policier','Policier',.13,1.60,'#1E4352','#91D3DF',(-18,-150))
        sound(shot,0,'stop',stop)
        sound(shot,2,'glisse',hit-.24)
        sound(shot,2,'coup',hit)
        sound(shot,2,'tombe',hit+.34)
        sound(shot,3,'radio',local(shot,3)+.09)
        mark(shot,'coup',hit);mark(shot,'chute',hit+.34);mark(shot,'radio',local(shot,3)+.48)
        reactions(shot,2,policier='choque')
        reactions(shot,3,violette='malicieux')
        self.greens(shot,local(shot,4)+.48,move,sound,4)
        badge(shot,'verte1','Bactéries',local(shot,4)+.81,1.60,'#2C4E37','#8FF194',(0,-138))

        shot='duel'
        final=local(shot,2)
        crash=final+lines[shot][2]['parole']+.42
        animate(shot,'globule',pose(0,233,12,-12,.77),pose(.29,98,-23,10,.93),pose(.60,0,0,0,1.06),pose(.84),
             pose(final-.19),pose(final+.18,24,-28,11,1.07),
             pose(crash-.27,24,-28,11,1.07),pose(crash-.12,-38,-41,-9,1.03),pose(crash,-160,-6,-23,1.08),
             pose(crash+.09,-174,8,-36,.91),pose(crash+.28,-121,-40,24,.96),pose(crash+.57,95,38,12,.82))
        animate(shot,'violette',pose(.2),pose(.48,-12,-16,-9,1.06),pose(.92),pose(final+.19,-43,-13,14,.92),
             pose(crash-.27,-43,-13,14,.92),pose(crash-.13,11,-30,-7,1.03),pose(crash,125,-11,27,1.08),
             pose(crash+.12,153,8,34,.93),pose(crash+.29,84,-34,-24,.95),pose(crash+.58,-22,20,-7))
        badge(shot,'globule','Globule blanc',.40,1.75,'#285259','#E9F9EB',(-13,-156))
        sound(shot,2,'glisse',crash-.19);sound(shot,2,'choc',crash)
        mark(shot,'duel',crash)
        reactions(shot,0,violette='malicieux')
        reactions(shot,1,globule='fache')

        shot='renfort'
        animate(shot,'policier',pose(0,-10,36,-11,.92),pose(.22,-11,31,-5,.93),pose(.52,-10,36,-11,.92))
        move(shot,'violette',pose(0,48,-25,-13),pose(.41,19,-12,10),pose(.78))
        sound(shot,0,'radio',.07)
        self.greens(shot,cue(shot,0,'multiplient')+.15,move,sound,0)
        mark(shot,'renfort',.53)

        shot='resistance'
        launch=cue(shot,0,'mauvaise')+.27
        parry=launch+.29
        reveal=cue(shot,2,'résiste')
        animate(shot,'gelule',pose(0,209,16,17,.73),pose(.35,61,-30,-11,.94),pose(.66),
             pose(launch-.28),pose(launch-.14,29,-16,21,.96),pose(launch,-60,-33,-29,1.10),
             pose(parry-.02,-104,-21,-39,1.04),pose(parry+.05,-77,-4,-12,.93),
             pose(parry+.17,22,-29,15,1.04),pose(parry+.43))
        animate(shot,'violette',pose(0),pose(launch-.19,15,-10,8,.99),pose(parry,-15,-11,-12,1.04),
             pose(parry+.30),pose(reveal-.12),pose(reveal+.12,7,-19,9,1.11),pose(reveal+.43))
        for i,name in enumerate(('verte1','verte2')):
            t=launch+.11+i*.07
            move(shot,name,pose(t),pose(t+.14,-28,-15,-15,.66),pose(t+.37,-41,23,24,.007))
            sound(shot,0,'ploc',t+.12)
        sound(shot,0,'glisse',launch-.16);sound(shot,0,'pare',parry)
        badge(shot,'gelule','Antibiotique',.37,1.57,'#1E4352','#91D3DF',(-41,-168))
        badge(shot,'violette','Bactérie\nrésistante',reveal-.09,2.18,offset=(-12,-170))
        mark(shot,'attaque',launch);mark(shot,'parade',parry);mark(shot,'révélation',reveal)
        reactions(shot,0,violette='malicieux')
        reactions(shot,1,gelule='choque')
        reactions(shot,2,gelule='fatigue')

        shot='cabinet'
        inj=cue(shot,0,'pied')
        cta=local(shot,4)
        move(shot,'lea',pose(.26),pose(.62,0,0,1.25),pose(1.3),
             pose(inj-.15),pose(inj+.16,2,-3,1.8),pose(inj+.70))
        move(shot,'docteure',pose(local(shot,1)),pose(local(shot,1)+.48,0,-2,1.4),
             pose(local(shot,1)+.91),pose(cta),pose(cta+.52,0,-2,-1.5,1.01),pose(cta+1.10))
        sound(shot,4,'ding',cta+.13)
        mark(shot,'pied',inj+.25);mark(shot,'cta',cta+.68)
        reactions(shot,0,docteure='inquiet')
        reactions(shot,1,lea='inquiet')

    def actor_state(self, shot, name, spec, t, line, prev_lines):
        st=super().actor_state(shot,name,spec,t,line,prev_lines)
        if name!='policier':
            return st
        if shot['id']=='intrusion':
            s=t-self.moments['intrusion']['coup']
            st['layer_angles']={'panneau':self.sign_recoil(s)+12,'bottes':self.boot_recoil(s)}
            if -.05<s<.86:
                st['emo']='douleur' if .26<s<.49 else ('fatigue' if s>=.49 else 'choque')
                st['gaze']=(.8,-.30 if s<.26 else .10)
                st['blink']=False
        elif shot['id']=='renfort':
            st['layer_angles']={'panneau':self.sign_recoil(1.5)+12,'bottes':self.boot_recoil(1.4)}
        return st

    @staticmethod
    def greens(shot,at,move,sound,line):
        for i,name in enumerate(('verte1','verte2')):
            t=at+i*.28
            move(shot,name,pose(0,-109-i*48,-151,13,.007),pose(t,-109-i*48,-151,13,.007),
                 pose(t+.25,-57,-85,-11,.63),pose(t+.51,10,-17,13,1.07),pose(t+.68))
            sound(shot,line,'ploc',t+.41)

    def _camera_frame(self, frame, shot, t):
        if shot['id']=='cabinet':
            focus=self.moments['cabinet']['pied']
            if focus-.38<=t<focus+.65:
                view=(436,1031,916,1884)
                return frame.crop(view).resize((W,H),Image.Resampling.LANCZOS),view
        return super()._camera_frame(frame,shot,t)

    def _encode(self, tmp, out):
        if self.approved_audio is None:
            return super()._encode(tmp,out)
        subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',str(tmp/'v.mp4'),
                        '-i',str(self.approved_audio),'-map','0:v:0','-map','1:a:0',
                        '-c','copy','-movflags','+faststart',str(out)],check=True)

    def _actor_labels(self,frame,shot,t,placed,view):
        name=shot['id']
        m=self.moments.get(name,{})
        overlay=Image.new('RGBA',frame.size)
        d=ImageDraw.Draw(overlay)
        x0,y0,x1,y1=view
        def pos(x,y):
            return ((x-x0)*W/(x1-x0),(y-y0)*H/(y1-y0))
        def burst(x,y,q,color):
            cx,cy=pos(x,y)
            for i in range(8):
                a=i*math.pi/4
                r=33+115*q
                reach=r+21+30*q
                d.line((cx+r*math.cos(a),cy+r*math.sin(a),cx+reach*math.cos(a),cy+reach*math.sin(a)),
                       fill=(*color,round(250*(1-q))),width=max(1,round(8*(1-q))))
        if 'impact' in m and 0<t-m['impact']<.40:
            q=(t-m['impact'])/.40
            for i,(dx,dy) in enumerate(((-130,72),(-91,121),(-34,154),(45,147),(92,113),(125,64))):
                x,y=pos(690+dx*q,1126-4*dy*q*(1-q))
                r=(10 if i in (2,3) else 7)*(1-.62*q)
                d.ellipse((x-r,y-r*1.6,x+r,y+r*1.6),fill=(255,200,162,round(250*(1-q))))
        if 'coup' in m:
            elapsed=t-m['coup']
            violet=next((a for a in placed if a['name']=='violette'),None)
            if violet and -.15<elapsed<.16:
                reach=math.sin(math.pi*max(0,min(1,(elapsed+.15)/.31)))**.8
                sx,sy=pos(violet['face'][0]-47,violet['face'][1]+14)
                contact=pos(404,1197)
                ex=sx+(contact[0]-sx)*reach
                ey=sy+(contact[1]-sy)*reach
                bend=26*reach
                points=[(sx+(ex-sx)*u,sy+(ey-sy)*u+bend*math.sin(math.pi*u))
                        for u in np.linspace(0,1,19)]
                for width,color in ((36,'#503467'),(27,'#BB95D2')):
                    d.line(points,fill=color,width=width,joint='curve')
                    r=width/2
                    d.ellipse((ex-r,ey-r,ex+r,ey+r),fill=color)
            if 0<=elapsed<.16:
                burst(404,1197,elapsed/.16,(255,237,180))
        if 'chute' in m and 0<=t-m['chute']<.24:
            q=(t-m['chute'])/.24
            for dx,dy,r in ((-55,25,13),(-91,47,9),(33,28,15),(68,43,11),(104,22,7)):
                x,y=pos(218+dx*q,1400-dy*math.sin(math.pi*q))
                d.ellipse((x-r,y-r*.55,x+r,y+r*.55),fill=(255,209,197,round(222*(1-q))))
        if 'duel' in m and 0<=t-m['duel']<.76:
            q=(t-m['duel'])/.76
            scale=.68+ .63*math.sin(min(1,q*1.5)*math.pi/2)
            alpha=round(238*min(1, q*9, (1-q)*3))
            cx,cy=pos(559,1200)
            cloud=Image.new('L',frame.size)
            mask=ImageDraw.Draw(cloud)
            for ox,oy,r in ((-120,5,95),(-55,-62,120),(66,-58,112),(139,12,77),
                            (71,72,94),(-58,84,98),(0,9,132)):
                x,y=cx+ox*scale,cy+oy*scale
                rad=r*scale
                mask.ellipse((x-rad,y-rad,x+rad,y+rad),fill=alpha)
            outline=Image.new('RGBA',frame.size,(98,62,67))
            outline.putalpha(cloud.filter(ImageFilter.MaxFilter(11)))
            overlay.alpha_composite(outline)
            puff=Image.new('RGBA',frame.size,(252,238,223))
            puff.putalpha(cloud)
            overlay.alpha_composite(puff)
            burst(559,1200,q,(255,250,226))
        if name=='resistance':
            capsule=next((a for a in placed if a['name']=='gelule'),None)
            if capsule:
                x,y=pos(*capsule['face'])
                hit=m['attaque']
                swing=max(0,1-abs(t-hit)/.29)
                grip=(x-28,y+76)
                tip=(x-105-65*swing,y-93+153*swing)
                d.line((grip,tip),fill='#181313',width=14)
                d.line((grip,tip),fill='#B9DBD4',width=7)
                d.ellipse((tip[0]-7,tip[1]-8,tip[0]+7,tip[1]+8),fill='#F0FAEB',outline='#24666D',width=2)
        if 'attaque' in m and 0<=t-m['attaque']<.43:
            q=(t-m['attaque'])/.43
            x,y=pos(748-339*q,1230)
            d.arc((x-29,y-110,x+97,y+73),110,278,fill=(235,253,247,round(235*(1-q))),width=13)
            d.arc((x-11,y-93,x+74,y+54),113,272,fill=(157,237,227,round(214*(1-q))),width=6)
        if 'parade' in m and 0<=t-m['parade']<.29:
            burst(487,1177,(t-m['parade'])/.29,(255,238,187))
        frame.alpha_composite(overlay)
        super()._actor_labels(frame,shot,t,placed,view)


def main():
    p=ArgumentParser()
    p.add_argument('--apercu',action='store_true')
    p.add_argument('--sortie',type=Path,default=FINAL)
    p.add_argument('--audio-valide',type=Path,default=APPROVED)
    args=p.parse_args()
    if not args.apercu and (not args.audio_valide.is_file() or args.audio_valide.resolve()==args.sortie.resolve()):
        p.error('Le mix approuvé doit être un fichier différent de la sortie.')
    e=Reprise(args.audio_valide)
    OUT.mkdir(exist_ok=True)
    e.save_subtitles(OUT)
    data={'duree':e.duration,'signature':e.cfg.get('filigrane',e.niche['filigrane']),
          'scenes':[{ 'id':s['id'],'debut':s['t0'],'fin':s['t1']} for s in e.shots],
          'repliques':[{k:l[k] for k in ('qui','dit','t0','t1')} for l in e.lines],
          'moments':e.moments}
    (OUT/'montage.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(f'{e.duration:.2f} s · {len(e.lines)} prises',flush=True)
    for shot in data['scenes']:
        print(shot['id'],f"{shot['debut']:.2f}–{shot['fin']:.2f}",flush=True)
    if args.apercu:
        hit=e.moments['intrusion']['coup']
        times=[.75,8.2,20.8,27,54,79.1,88,94]+[hit+d for d in (-.31,-.065,.01,.08,.16,.24,.34,.45,.64,.86,1.06,1.27,1.53)]
        times.extend(t+.07 for times in e.moments.values() for t in times.values() if t>1.5)
        e.preview(OUT,sorted(set(times)))
        return
    problems=e.controle(OUT)
    if problems:
        raise SystemExit('\n'.join(problems))
    e.render(args.sortie,preview_every=360)


if __name__=='__main__':
    main()
