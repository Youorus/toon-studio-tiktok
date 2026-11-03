"""Prépare les décors, accessoires et prises de vue de la reprise 006."""
from copy import deepcopy
import math
from pathlib import Path
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.signal import butter, sosfilt
import yaml

from dialogues import SCENES, VOICES, lines
from toonstudio.drawing import cover, font, remove_flat_background

ROOT = Path(__file__).resolve().parent
NICHE = ROOT.parents[1]
OLD = ROOT.parent/'006-antibioresistance'
V2 = ROOT.parent/'006-antibioresistance-v2'
STYLE = yaml.safe_load((NICHE/'niche.yaml').read_text())['direction_artistique']
ART = ROOT/'art'
CREAM, INK = '#FFF9ED', '#181313'


def save_config(folder, cfg):
    (folder/'personnage.yaml').write_text(yaml.safe_dump(cfg,allow_unicode=True,sort_keys=False))


def stage():
    img = cover(Image.open(ART/'breche.png').convert('RGBA'))
    wall = img.crop((0,0,1080,1331)).resize((1080,1143),Image.Resampling.LANCZOS)
    decor = Image.new('RGBA',(1080,1920),'#F5888A')
    d = ImageDraw.Draw(decor)
    d.rectangle((0,1116,1080,1229),fill='#EF777D')
    for poly in (
        [(0,1425),(195,1387),(380,1407),(213,1470),(0,1508)],
        [(620,1378),(837,1337),(1080,1353),(1080,1401),(890,1415)],
        [(355,1620),(639,1569),(913,1604),(752,1664),(420,1674)],
        [(0,1768),(275,1742),(476,1786),(314,1820),(0,1816)],
    ):
        d.polygon(poly,fill='#F17D81')
    # Le décor joue sur un plateau vide. Le raccord se fait dans le rose du sol.
    gradient = np.broadcast_to(np.clip((1143-np.arange(1143))/42,0,1)[:,None],(1143,1080))
    wall.putalpha(Image.fromarray(np.rint(gradient*255).astype('uint8')))
    decor.alpha_composite(wall)
    (ROOT/'decors').mkdir(exist_ok=True)
    decor.save(ROOT/'decors'/'breche-corail.png')


def police():
    folder=ROOT/'personnages'/'policier-comique'
    folder.mkdir(parents=True,exist_ok=True)
    src=remove_flat_background(Image.open(ART/'policier-comique.png').convert('RGBA'),tol=25)
    pixels=np.array(src)
    # L'ombre bleue du dessin reste au sol, pas sur le personnage quand il roule.
    shadow=(pixels[:,:,1]>90)&(pixels[:,:,2]>100)
    shadow[:round(src.height*.91)]=False
    pixels[shadow,3]=0
    src=Image.fromarray(pixels)
    src=src.crop(src.getbbox())
    src=src.resize((round(src.width*380/src.height),380),Image.Resampling.LANCZOS)
    alpha=src.getchannel('A')
    outlined=Image.new('RGBA',src.size,INK)
    outlined.putalpha(alpha.filter(ImageFilter.MaxFilter(7)))
    outlined.alpha_composite(src)
    src=outlined
    w,h=src.size
    face=(round(w*.625),round(h*.421))
    skin=src.getpixel((face[0],face[1]+12))
    tone='#%02X%02X%02X'%skin[:3]
    fx,fy=face
    d=ImageDraw.Draw(src)
    d.arc((fx-1,fy+16,fx+25,fy+39),-105,120,fill=INK,width=3)
    d.ellipse((fx-37,fy+31,fx+8,fy+47),fill=INK)
    d.ellipse((fx+1,fy+30,fx+37,fy+46),fill=INK)
    d.polygon([(fx-33,fy+40),(fx-47,fy+32),(fx-44,fy+42),(fx-35,fy+46)],fill=INK)
    d.polygon([(fx+31,fy+35),(fx+43,fy+29),(fx+39,fy+40),(fx+32,fy+44)],fill=INK)
    seam=338
    boots=src.crop((0,seam,w,h))
    boots.save(folder/'bottes.png')
    src.paste((0,0,0,0),(0,seam+8,w,h))
    src.save(folder/'corps.png')
    stop=Image.new('RGBA',(152,214))
    d=ImageDraw.Draw(stop)
    d.rounded_rectangle((68,113,83,212),radius=4,fill='#9B6757',outline=INK,width=4)
    octagon=[(76+68*math.cos(math.pi/8+i*math.pi/4),73+68*math.sin(math.pi/8+i*math.pi/4)) for i in range(8)]
    d.polygon(octagon,fill='#B93647',outline=INK,width=6)
    inner=[(76+(x-76)*.87,73+(y-73)*.87) for x,y in octagon]
    d.line(inner+[inner[0]],fill=CREAM,width=5,joint='curve')
    d.text((76,74),'STOP',font=font('LuckiestGuy',41),fill=CREAM,anchor='mm')
    stop.save(folder/'stop.png')
    radio=Image.new('RGBA',(91,121))
    d=ImageDraw.Draw(radio)
    d.line(((65,117),(20,99),(45,57)),fill=INK,width=24,joint='curve')
    d.line(((65,117),(20,99),(45,57)),fill='#75ABBB',width=17,joint='curve')
    d.rounded_rectangle((22,21,54,70),radius=8,fill='#263841',outline=INK,width=4)
    d.line((46,23,47,3),fill=INK,width=5)
    d.ellipse((31,31,40,40),fill='#5BDD79')
    d.ellipse((35,54,54,72),fill=tone,outline=INK,width=3)
    radio.save(folder/'radio.png')
    Image.new('RGBA',(1,1)).save(folder/'vide.png')
    cfg={'nom':'Le policier de la peau','type':'humain',
         'couches':[{'id':'corps','images':{'defaut':'corps.png'},'pivot':[w//2,225]},
                    {'id':'bottes','parent':'corps','attache':[w//2,seam],
                     'pivot':[w//2,0],'z':-1,'images':{'defaut':'bottes.png'}},
                    {'id':'panneau','parent':'corps','attache':[round(w*.89),round(h*.795)],
                     'pivot':[75,192],'z':-1,'images':{'defaut':'stop.png'}},
                    {'id':'radio','parent':'corps','attache':[round(w*.40),round(h*.58)],
                     'pivot':[44,49],'z':1,'images':{'defaut':'vide.png','appel':'radio.png'}}],
         'visage':{'couche':'corps','yeux':list(face),'rayon_oeil':22,'ecart':2.28,'trait':.135,
                   'bouche':[fx+6,fy+60],'largeur_bouche':43,'peau':tone,'pupille':.78,'paupiere':.13},
         'poses':{'appel':{'radio':{'image':'appel'}},'chute':{'radio':{'image':'defaut'}}},
         'mouvement':{'souplesse':.10,'respiration':.002}}
    save_config(folder,cfg)


def clinic_detail():
    cabinet=Image.open(NICHE/STYLE['cabinet']).convert('RGBA')
    d=ImageDraw.Draw(cabinet)
    for y, text, size in ((540,'Bactéries',35),(574,'prenez un',29),(600,'ticket',29)):
        d.text((807,y),text,font=font('Caveat',size),fill='#405854',anchor='mm')
    ticket=Image.new('RGBA',(61,38))
    p=ImageDraw.Draw(ticket)
    p.rounded_rectangle((2,4,58,34),radius=4,fill='#F5D4BE',outline='#A45F54',width=2)
    p.text((30,19),'006',font=font('Caveat',23),fill='#73413A',anchor='mm')
    cabinet.alpha_composite(ticket.rotate(8,Image.Resampling.BICUBIC,expand=True),(774,621))
    cabinet.save(ROOT/'decors'/'cabinet-006.png')


def wounded_lea():
    src=NICHE/'personnages'/'lea-aplats'
    folder=ROOT/'personnages'/'lea-blessee'
    folder.mkdir(parents=True,exist_ok=True)
    body=Image.open(src/'corps.png').convert('RGBA')
    body.save(folder/'corps.png')
    cfg=yaml.safe_load((src/'personnage.yaml').read_text())
    arr=np.asarray(body)
    # Calque de costume séparé. Le contour de la jambe et le dessin du visage viennent du modèle approuvé.
    y0,y1,x0,x1=628,708,4,83
    sub=arr[y0:y1,x0:x1,:]
    patch=np.zeros_like(sub)
    purple=(sub[:,:,0]>65)&(sub[:,:,0]<148)&(sub[:,:,2]>52)&(sub[:,:,2]<133)&(sub[:,:,0]>sub[:,:,1]+12)&(sub[:,:,3]>190)
    purple[:18]=False
    patch[purple]=[193,156,125,255]
    cuff=Image.fromarray(patch)
    d=ImageDraw.Draw(cuff)
    d.rounded_rectangle((9,12,69,24),radius=5,fill='#674452',outline=INK,width=2)
    d.polygon([(37,37),(47,43),(42,52),(49,58),(43,64),(30,59),(32,48),(27,42)],
              fill='#AB3C48',outline='#6D383B',width=2)
    d.line([(35,42),(41,47),(38,53)],fill='#F28077',width=3)
    cuff.save(folder/'cheville.png')
    cfg['couches'].append({'id':'cheville','parent':'corps','attache':[x0,y0],'pivot':[0,0],
                          'z':1,'images':{'defaut':'cheville.png'}})
    save_config(folder,cfg)


def effects():
    rate=48000
    rng=np.random.default_rng(641)
    folder=ROOT/'sons'
    folder.mkdir(exist_ok=True)
    for name,duration in (('stop',.23),('coup',.32),('tombe',.39),('radio',.37),('choc',.61),
                          ('glisse',.38),('pare',.30),('clac',.16)):
        t=np.arange(round(rate*duration))/rate
        n=rng.normal(0,1,len(t))
        brush=sosfilt(butter(2,[500,4300],fs=rate,btype='bandpass',output='sos'),n)
        phase=2*np.pi*(55*t+8*(1-np.exp(-22*t)))
        attack=np.minimum(1,140*t)
        if name in ('coup','tombe','choc'):
            strength={'coup':.66,'tombe':.42,'choc':.48}[name]
            x=strength*np.sin(phase)*np.exp(-13*t)+.24*brush*np.exp(-27*t)
            if name=='choc':
                x+=.24*np.sin(phase*1.62)*np.exp(-((t-.24)/.10)**2)
        elif name=='radio':
            beep=(t<.063)|((t>.109)&(t<.166))
            x=.18*np.sin(2*np.pi*970*t)*beep+.08*brush*np.exp(-4*t)
        elif name=='glisse':
            x=.34*brush*(t/duration)**.7*(1-t/duration)**2
        elif name=='pare':
            x=(.22*np.sin(2*np.pi*705*t)+.15*np.sin(2*np.pi*1090*t))*np.exp(-14*t)+.18*brush*np.exp(-32*t)
        else:
            x=(.25*np.sin(2*np.pi*(180 if name=='stop' else 250)*t)+.24*brush)*np.exp(-28*t)
        x*=attack*np.minimum(1,60*(duration-t))
        with wave.open(str(folder/f'{name}.wav'),'wb') as wav:
            wav.setparams((1,2,rate,0,'NONE','not compressed'))
            wav.writeframes(np.clip(x*32767,-32768,32767).astype('<i2').tobytes())


def asset(name):
    return f'episodes/{OLD.name}/personnages/{name}'


def person(path,x,y,scale=1,**other):
    return dict(perso=path,x=x,y=y,echelle=scale,**other)


def build():
    stomach={'estomac':person(asset('estomac'),815,810,1.30,regard=[-.77,.15]),
             'gelule':person(asset('gelule'),690,1018,1.11,regard=[.77,-.22]),
             'intestin':person(asset('estomac'),502,1270,.75,regard=[.73,-.40],entre=3)}
    again={k:v for k,v in stomach.items() if k!='intestin'}
    guard=person('personnages/policier-comique',267,1245,.99,regard=[.78,.18])
    violet=person(asset('resistante'),618,1241,1.53,regard=[-.84,.10])
    green=person(asset('bacterie'),822,1260,1.27,regard=[-.70,.15])
    glob=person(asset('globule'),805,1219,1.46,regard=[-.77,0])
    skin={'policier':guard,'violette':violet,'verte1':green,
          'verte2':person(asset('bacterie'),927,1183,.85)}
    duel={'violette':person(asset('resistante'),452,1251,1.52,regard=[.88,-.1]),'globule':glob}
    treatment={'violette':person(asset('resistante'),435,1255,1.52,regard=[.86,-.15]),
               'gelule':person(asset('gelule'),806,1232,1.63,regard=[-.83,.10]),
               'verte1':person(asset('bacterie'),578,1286,.71),
               'verte2':person(asset('bacterie'),673,1168,.62)}
    clinic={'lea':person('personnages/lea-blessee',703,1612,1.06,regard=[-.85,-.5]),
            'docteure':person(f"personnages/{STYLE['casting']['docteure']['rig']}",309,1612,1.08,regard=[.8,.5])}
    shapes=(
        ('estomac','decors/estomac-corail.png','Estomac',stomach,[1.16,1.16],[626,901]),
        ('intrusion','decors/breche-corail.png','Peau',skin,[1,1],[540,960]),
        ('duel','decors/breche-corail.png','Peau',duel,[1.04,1.04],[569,1080]),
        ('renfort','decors/breche-corail.png','Peau',deepcopy(skin),[1,1],[540,960]),
        ('prescription','decors/estomac-corail.png','Estomac',again,[1.16,1.16],[626,901]),
        ('resistance','decors/breche-corail.png','Peau',treatment,[1,1],[540,960]),
        ('cabinet','decors/cabinet-006.png',None,clinic,[1,1.015],[540,960]),
    )
    shots=[]
    for ident,decor,organ,actors,zoom,center in shapes:
        shot={'id':ident,'decor':decor,'transition':'coupe','zoom':zoom,'centre':center,
              'acteurs':actors,'repliques':lines(ident)}
        if organ: shot['organe']=organ
        shots.append(shot)
    shots[1]['repliques'][3]['pose']='appel'
    shots[3]['repliques'][0]['pose']='appel'
    shots[6]['repliques'][-1].update(carte=STYLE['abonnement_final'],regards={'docteure':[0,0]})
    volumes={'stop':.49,'coup':.72,'tombe':.66,'radio':.34,'choc':.50,'glisse':.37,'pare':.65,'clac':.50}
    sfx={n:{'fichier':f'sons/{n}.wav','volume':v} for n,v in volumes.items()}
    for name,folder,value in (('plouf',V2,.66),('ploc',OLD,.39),('passage',OLD,.29)):
        sfx[name]={'fichier':f'episodes/{folder.name}/sons/{name}.wav','volume':value}
    return {'titre':'La bactérie qui n’a pas bougé','niche':'corps-humain','degrade_bas':False,
            'legendes_mode':'mot_capitales','legendes_y':1472,'voix':VOICES,'bruitages':sfx,'plans':shots}


if __name__=='__main__':
    stage()
    police()
    clinic_detail()
    wounded_lea()
    effects()
    (ROOT/'episode.yaml').write_text(yaml.safe_dump(build(),allow_unicode=True,sort_keys=False,width=103))
