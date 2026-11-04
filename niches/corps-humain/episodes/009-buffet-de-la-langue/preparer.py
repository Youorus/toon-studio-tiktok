"""Réutilise la bibliothèque et prépare la bouche, le repas et les variantes du 009."""
from copy import deepcopy
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
import yaml

from dialogues import VOICES, lines
from toonstudio.drawing import font, remove_flat_background

ROOT=Path(__file__).resolve().parent
NICHE=ROOT.parents[1]
ART=ROOT/'art'
STYLE=yaml.safe_load((NICHE/'niche.yaml').read_text())['direction_artistique']
INK='#6D383B'


def save_rig(name,image,eye,radius,skin,mouth=None):
    folder=ROOT/'personnages'/name
    folder.mkdir(parents=True,exist_ok=True)
    image.save(folder/'corps.png')
    cfg={'nom':name,'type':'humain' if name=='ami' else 'organe',
         'couches':[{'id':'corps','images':{'defaut':'corps.png'},'pivot':[image.width//2,image.height-1]}],
         'visage':{'couche':'corps','yeux':eye,'rayon_oeil':radius,'ecart':2.20,'trait':.13,
                   'bouche':mouth or [eye[0],eye[1]+radius*1.9],'peau':skin,'paupiere':.09,'pupille':.76},
         'mouvement':{'souplesse':.30 if name!='ami' else .10,'respiration':.004}}
    (folder/'personnage.yaml').write_text(yaml.safe_dump(cfg,allow_unicode=True,sort_keys=False))


def characters():
    src=NICHE/'episodes'/'006-antibioresistance'/'personnages'/'bacterie'
    image=Image.open(src/'corps.png').convert('RGBA')
    pixels=np.asarray(image).copy()
    rgb=pixels[:,:,:3].astype(int)
    green=(rgb[:,:,1]>rgb[:,:,0]+16)&(rgb[:,:,1]>rgb[:,:,2]+15)&(pixels[:,:,3]>0)
    # Même silhouette et mêmes contours que le 006, avec les aplats verts de la palette.
    light=green&(pixels[:,:,1]>190)
    shade=green&~light
    pixels[light,:3]=[91,221,121]
    pixels[shade,:3]=[49,185,88]
    image=Image.fromarray(pixels)
    folder=ROOT/'personnages'/'verte'
    folder.mkdir(parents=True,exist_ok=True)
    image.save(folder/'corps.png')
    cfg=deepcopy(yaml.safe_load((src/'personnage.yaml').read_text()))
    cfg['visage']['peau']='#5BDD79'
    cfg['visage']['trait']=.13
    (folder/'personnage.yaml').write_text(yaml.safe_dump(cfg,allow_unicode=True,sort_keys=False))

    image=remove_flat_background(Image.open(ART/'microbe-rouge.png'),tol=25)
    data=np.asarray(image).copy()
    white=(data[:,:,:3].min(axis=2)>220)&(data[:,:,3]>0)
    data[white,:3]=[248,108,106]
    image=Image.fromarray(data)
    image=image.resize((round(image.width*232/image.height),232),Image.Resampling.LANCZOS)
    save_rig('rouge',image,[round(image.width*.36),105],25,'#F86C6A')

    image=remove_flat_background(Image.open(ART/'ami-source.png'),tol=25)
    data=np.asarray(image).copy()
    white=(data[:,:,:3].min(axis=2)>246)&(data[:,:,:3].max(axis=2)-data[:,:,:3].min(axis=2)<4)
    data[white,3]=0
    image=Image.fromarray(data)
    image=image.resize((round(image.width*674/image.height),674),Image.Resampling.LANCZOS)
    x,y=round(image.width*.40),round(image.height*.185)
    skin='#%02X%02X%02X'%image.getpixel((x,y))[:3]
    save_rig('ami',image,[x,y],19,skin,[x-1,y+43])


def mouth():
    image=Image.new('RGB',(2160,3840),'#E75261')
    draw=ImageDraw.Draw(image)

    def shape(start,*curves,fill,outline='#6D383B',width=5):
        points=[start]
        for segment in curves:
            if len(segment)==2:
                points.append(segment)
                continue
            ax,ay,bx,by,ex,ey=segment
            x,y=points[-1]
            points.extend(((1-t)**3*x+3*(1-t)**2*t*ax+3*(1-t)*t*t*bx+t**3*ex,
                           (1-t)**3*y+3*(1-t)**2*t*ay+3*(1-t)*t*t*by+t**3*ey)
                          for t in np.linspace(1/32,1,32))
        pts=[(round(x*2),round(y*2)) for x,y in points]
        draw.polygon(pts,fill=fill)
        draw.line(pts+[pts[0]],fill=outline,width=width*2,joint='curve')

    shape((106,366),(223,299,859,296,972,370),(1050,594,1061,1325,893,1517),
          (688,1693,282,1614,133,1416),(31,1246,16,655,106,366),fill='#C65060')
    shape((158,401),(307,351,810,351,925,407),(963,628,958,1112,882,1349),
          (707,1516,301,1527,175,1345),(74,1118,76,601,158,401),fill='#B94656',width=4)
    for i in range(8):
        x=148+i*98
        top=354+round(abs(i-3.5)*5)
        points=[(x,top),(x+88,top-3),(x+88,top+133),(x+75,top+149),
                (x+45,top+140),(x+13,top+151),(x+3,top+132)]
        pts=[(a*2,b*2) for a,b in points]
        draw.polygon(pts,fill='#FFF9ED')
        draw.line(pts+[pts[0]],fill=INK,width=7,joint='curve')
    shape((539,847),(411,769,238,804,152,1002),(69,1192,202,1439,476,1501),
          (712,1551,981,1434,989,1190),(994,955,775,766,539,847),fill='#EE6576',width=7)
    shape((535,886),(398,805,247,901,208,1064),(164,1228,282,1408,490,1452),
          (667,1500,863,1416,902,1237),(963,1031,767,841,535,886),fill='#EF7D86',outline='#EF7D86',width=1)
    groove=[(538+10*np.sin(q*3),849+361*q) for q in np.linspace(0,1,60)]
    draw.line([(round(x*2),round(y*2)) for x,y in groove],fill='#B65F63',width=8,joint='curve')
    rng=np.random.default_rng(933)
    for i in range(25):
        x,y=rng.uniform(230,907),rng.uniform(929,1381)
        if abs(x-540)<26:
            continue
        r=rng.uniform(4,8)
        draw.ellipse(((x-r)*2,(y-r*.5)*2,(x+r)*2,(y+r*.5)*2),fill='#E77C87')
    image.resize((1080,1920),Image.Resampling.LANCZOS).save(ART/'bouche-corail.png')


def rooms():
    image=Image.new('RGB',(1080,1920),'#E4E2D7')
    d=ImageDraw.Draw(image)
    d.rectangle((0,1485,1080,1920),fill='#8D8C84')
    d.line((0,1480,1080,1480),fill='#345C62',width=17)
    d.rounded_rectangle((122,214,431,591),radius=8,fill='#D7AF89',outline=INK,width=7)
    d.rectangle((138,232,415,574),fill='#91D3DF',outline=INK,width=4)
    d.line((277,232,277,574),fill='#D7AF89',width=14)
    d.line((138,399,415,399),fill='#D7AF89',width=13)
    image.save(ART/'petit-dejeuner.png')
    image=Image.open(NICHE/STYLE['cabinet']).convert('RGBA')
    d=ImageDraw.Draw(image)
    for y,text in ((537,'Dents et langue,'),(571,'tout doux.'),(606,'Chaque jour.')):
        d.text((807,y),text,font=font('Caveat',26),fill='#405854',anchor='mm')
    image.save(ART/'cabinet-009.png')


def person(path,x,y,scale,gaze):
    return {'perso':path,'x':x,'y':y,'echelle':scale,'regard':gaze}


def build():
    clinic={role:person('personnages/'+STYLE['casting'][role]['rig'],x,1612,scale,gaze)
            for role,x,scale,gaze in (('lea',703,1.06,[-.85,-.5]),('docteure',309,1.08,[.8,.5]))}
    office=lines('cabinet')
    office[-1].update(carte=STYLE['abonnement_final'],regards={'docteure':[0,0]})
    return {'titre':'Le buffet de la langue','niche':'corps-humain','degrade_bas':False,'voix':VOICES,
        'bruitages':{
            'ploc':{'fichier':'episodes/006-antibioresistance/sons/ploc.wav','volume':.35},
            'glisse':{'fichier':'episodes/006-antibioresistance-v3/sons/glisse.wav','volume':.27},
            'stop':{'fichier':'episodes/006-antibioresistance-v3/sons/stop.wav','volume':.28},
        },
        'plans':[
            {'id':'reveil','organe':'Cerveau','decor':'art/cerveau-corail.png','transition':'coupe','zoom':[1,1],
             'acteurs':{'cerveau':person('episodes/008-estomac-sature/personnages/cerveau',540,1114,1.15,[0,0])},
             'repliques':lines('reveil')},
            {'id':'buffet','organe':'Bouche','decor':'art/bouche-corail.png','transition':'coupe','zoom':[1,1],
             'acteurs':{'verte':person('personnages/verte',363,1199,1.46,[.7,0]),
                        'rouge':person('personnages/rouge',747,1333,1.06,[-.7,0])},
             'mini_badges':[{'acteur':'verte','texte':'Bactéries','delai':.13,'duree':1.8,'decalage':[4,-170]}],
             'repliques':lines('buffet')},
            {'id':'petit-dejeuner','decor':'art/petit-dejeuner.png','transition':'coupe','zoom':[1.4,1.4],'centre':[540,1270],
             'acteurs':{'ami':person('personnages/ami',299,1665,1.03,[.8,0]),
                        'lea':person('personnages/lea-aplats',793,1665,.86,[-.8,-.1])},
             'repliques':lines('petit-dejeuner')},
            {'id':'cabinet','decor':'art/cabinet-009.png','transition':'coupe','zoom':[1,1],
             'acteurs':clinic,'repliques':office},
        ],
    }


if __name__=='__main__':
    characters()
    mouth()
    rooms()
    Image.new('RGB',(1080,1920),'#E75261').save(ART/'cerveau-corail.png')
    (ROOT/'episode.yaml').write_text(yaml.safe_dump(build(),allow_unicode=True,sort_keys=False))
