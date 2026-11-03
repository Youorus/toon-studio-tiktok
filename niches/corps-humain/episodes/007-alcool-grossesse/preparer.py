"""Prépare les calques animables et le plan de tournage."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import label
import yaml

from dialogues import VOICES, lines
from toonstudio.drawing import font, remove_flat_background
from accessoires import prepare_props

ROOT=Path(__file__).resolve().parent
NICHE=ROOT.parents[1]
STYLE=yaml.safe_load((NICHE/'niche.yaml').read_text())['direction_artistique']


def prepare_actor(name, height, eye, radius, color=None, source=None):
    if name=='uterus':
        image=Image.new('RGBA',(300,200))
    else:
        cut=remove_flat_background(Image.open(ROOT/'art'/f'{source or name}.png'),tol=25)
        data=np.array(cut)
        components,count=label(data[:,:,3]>65)
        largest=np.argmax(np.bincount(components.ravel(),minlength=count+1)[1:])+1
        data[components!=largest,3]=0
        image=Image.fromarray(data)
        image=image.crop(image.getbbox())
        image=image.resize((round(height*image.width/image.height),height),Image.Resampling.LANCZOS)
    x,y=(round(eye[0]*image.width),round(eye[1]*image.height))
    skin=color or '#%02X%02X%02X'%image.getpixel((x,y))[:3]
    pivot=[image.width//2,y if name=='uterus' else image.height-1]
    cfg={'nom':name,'type':'organe','couches':[{'id':'corps','images':{'defaut':'corps.png'},'pivot':pivot}],
         'visage':{'couche':'corps','yeux':[x,y],'rayon_oeil':radius,'ecart':2.22,'trait':.13,
                   'bouche':[x,y+round(radius*1.9)],'peau':skin,'paupiere':.13,'pupille':.8},
         'mouvement':{'souplesse':.34,'respiration':.006}}
    folder=ROOT/'personnages'/name
    folder.mkdir(parents=True,exist_ok=True)
    image.save(folder/'corps.png')
    (folder/'personnage.yaml').write_text(yaml.safe_dump(cfg,allow_unicode=True,sort_keys=False))


def anatomy_background():
    # Les creux ont leur propre aplat. Le corail est posé directement sur les 1080 × 1920 px.
    base='#E75261'
    image=Image.new('RGB',(2160,3840),base)
    draw=ImageDraw.Draw(image)
    start=(511,285)
    curves=[
        ((801,266),(971,483),(982,751)),
        ((1000,1058),(909,1324),(742,1504)),
        ((626,1627),(568,1678),(573,1919)),
        ((555,1919),(501,1919),(474,1919)),
        ((489,1710),(416,1624),(283,1490)),
        ((113,1316),(69,1078),(89,803)),
        ((110,533),(249,306),(511,285)),
    ]
    path=[start]
    for a,b,end in curves:
        x,y=path[-1]
        path.extend(((1-t)**3*x+3*(1-t)**2*t*a[0]+3*(1-t)*t*t*b[0]+t**3*end[0],
                     (1-t)**3*y+3*(1-t)**2*t*a[1]+3*(1-t)*t*t*b[1]+t**3*end[1])
                    for t in np.linspace(1/48,1,48))
    for scale,offset,color,ink,width in (
        (1,(0,0),'#D9676B','#8F474B',12),
        (.966,(-6,6),'#BA515A','#6D383B',7),
        (.935,(-12,17),'#E58486','#8F474B',5),
        (.880,(-18,35),'#F6A09D','#B65F63',5),
        (.823,(-17,65),'#F7AEAA',None,0),
    ):
        points=[(round(2*(540+(x-540)*scale+offset[0])),
                 round(2*(1050+(y-1050)*scale+offset[1]))) for x,y in path]
        draw.polygon(points,fill=color)
        if ink:
            draw.line(points,fill=ink,width=width,joint='curve')
    image.resize((1080,1920),Image.Resampling.LANCZOS).save(ROOT/'art'/'uterus-corail.png')


def cabinet():
    image=Image.open(NICHE/STYLE['cabinet']).convert('RGBA')
    draw=ImageDraw.Draw(image)
    for y,text in ((546,'Un doute ?'),(579,'Parles-en'),(612,'sans filtre.')):
        draw.text((808,y),text,font=font('Caveat',30),fill='#405854',anchor='mm')
    image.save(ROOT/'art'/'cabinet-007.png')


def person(path,x,y,scale,gaze):
    return {'perso':path,'x':x,'y':y,'echelle':scale,'regard':gaze}


def build():
    anatomy={'uterus':person('personnages/uterus',537,485,1.1,[0,.8]),
             'placenta':person('personnages/placenta',231,1079,1.02,[.73,.10]),
             'foetus':person('personnages/foetus',703,1305,.99,[-.8,0])}
    clinic={role:person('personnages/'+STYLE['casting'][role]['rig'],x,1612,scale,gaze)
            for role,x,scale,gaze in (('lea',703,1.06,[-.85,-.5]),('docteure',309,1.08,[.8,.5]))}
    # Le moteur choisit d'abord les calques de l'épisode, puis ceux de la niche.
    clinic_lines=lines('cabinet')
    clinic_lines[-1].update(carte=STYLE['abonnement_final'],regards={'docteure':[0,0]})
    return {
        'titre':'Le colis surprise du placenta','niche':'corps-humain','degrade_bas':False,'voix':VOICES,
        'bruitages':{
            'glisse':{'fichier':'episodes/006-antibioresistance-v3/sons/glisse.wav','volume':.28},
            'pop':{'fichier':'episodes/006-antibioresistance/sons/ploc.wav','volume':.43},
        },
        'plans':[
            {'id':'passage','decor':'art/uterus-corail.png','organe':'Utérus','zoom':[1,1],'transition':'coupe',
             'acteurs':anatomy,'repliques':lines('passage'),'mini_badges':[
                 {'acteur':'placenta','texte':'Placenta','delai':.65,'duree':1.65,'decalage':[-25,-108]},
                 {'acteur':'foetus','texte':'Fœtus','replique':2,'delai':.10,'duree':1.65,'decalage':[42,-137]},
             ]},
            {'id':'cabinet','decor':'art/cabinet-007.png','zoom':[1,1.015],'transition':'coupe',
             'acteurs':clinic,'repliques':clinic_lines},
        ],
    }

if __name__=='__main__':
    prepare_actor('uterus',200,(.5,.44),35,'#F6A09D')
    prepare_actor('placenta',257,(.54,.43),24)
    prepare_actor('foetus',338,(.40,.365),20,source='foetus-reprise')
    anatomy_background()
    prepare_props(ROOT/'art')
    cabinet()
    (ROOT/'episode.yaml').write_text(yaml.safe_dump(build(),allow_unicode=True,sort_keys=False))
