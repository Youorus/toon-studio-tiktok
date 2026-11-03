"""Prépare les calques animables et le plan de tournage."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import label
import yaml

from dialogues import VOICES, lines
from toonstudio.drawing import font, remove_flat_background

ROOT=Path(__file__).resolve().parent
NICHE=ROOT.parents[1]
STYLE=yaml.safe_load((NICHE/'niche.yaml').read_text())['direction_artistique']


def prepare_actor(name, height, eye, radius, color=None):
    if name=='uterus':
        image=Image.new('RGBA',(300,200))
    else:
        cut=remove_flat_background(Image.open(ROOT/'art'/f'{name}.png'),tol=25)
        data=np.array(cut)
        components,count=label(data[:,:,3]>65)
        largest=np.argmax(np.bincount(components.ravel(),minlength=count+1)[1:])+1
        data[components!=largest,3]=0
        if color:
            saturated=(data[:,:,0]>190)&(data[:,:,1]<160)&(data[:,:,2]<155)
            data[saturated,1]=np.minimum(232,data[saturated,1].astype(int)+51)
            data[saturated,2]=np.minimum(228,data[saturated,2].astype(int)+46)
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


def cabinet():
    image=Image.open(NICHE/STYLE['cabinet']).convert('RGBA')
    draw=ImageDraw.Draw(image)
    for y,text in ((546,'Un doute ?'),(579,'Parles-en'),(612,'sans filtre.')):
        draw.text((808,y),text,font=font('Caveat',30),fill='#405854',anchor='mm')
    image.save(ROOT/'art'/'cabinet-007.png')


def person(path,x,y,scale,gaze):
    return {'perso':path,'x':x,'y':y,'echelle':scale,'regard':gaze}


def build():
    anatomy={'uterus':person('personnages/uterus',519,545,1.1,[0,.8]),
             'placenta':person('personnages/placenta',322,1088,.99,[.73,.10]),
             'foetus':person('personnages/foetus',701,1287,.99,[-.8,0])}
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
            {'id':'passage','decor':'art/uterus-interieur.png','organe':'Utérus','zoom':[1,1],'transition':'coupe',
             'acteurs':anatomy,'repliques':lines('passage'),'mini_badges':[
                 {'acteur':'placenta','texte':'Placenta','delai':.65,'duree':1.65,'decalage':[-25,-108]},
                 {'acteur':'foetus','texte':'Fœtus','replique':2,'delai':.10,'duree':1.65,'decalage':[42,-137]},
             ]},
            {'id':'cabinet','decor':'art/cabinet-007.png','zoom':[1,1.015],'transition':'coupe',
             'acteurs':clinic,'repliques':clinic_lines},
        ],
    }

if __name__=='__main__':
    prepare_actor('uterus',200,(.5,.44),35,'#FB625F')
    prepare_actor('placenta',257,(.54,.43),24)
    prepare_actor('foetus',364,(.42,.34),24,'#FF8D8B')
    cabinet()
    (ROOT/'episode.yaml').write_text(yaml.safe_dump(build(),allow_unicode=True,sort_keys=False))
