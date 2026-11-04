"""Réutilise la bibliothèque et prépare la bouche, le repas et les variantes du 009."""
from copy import deepcopy
from pathlib import Path

import numpy as np
from PIL import Image,ImageChops,ImageDraw,ImageFilter
import yaml

from dialogues import VOICES, lines
from costumes import flat_skin,prepare_lea
from toonstudio.drawing import cover,font,remove_flat_background
from scipy.ndimage import label

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
    image=flat_skin(image)
    x,y=round(image.width*.40),round(image.height*.185)
    skin='#%02X%02X%02X'%image.getpixel((x,y))[:3]
    save_rig('ami',image,[x,y],19,skin,[x-1,y+43])
    prepare_lea(NICHE,ROOT)


def mouth():
    image=cover(Image.open(ART/'bouche-reprise-source.png').convert('RGB'))
    data=np.asarray(image).copy()
    rgb=data.astype(int)
    corners=np.array([rgb[2,2],rgb[2,-3],rgb[-3,2],rgb[-3,-3]])
    base=np.median(corners,axis=0)
    close=np.linalg.norm(rgb-base,axis=2)<37
    components,_=label(close)
    border=np.unique(np.r_[components[0,:],components[-1,:],components[:,0],components[:,-1]])
    outer=np.isin(components,border[border!=0])
    data[outer]=[231,82,97]
    dark=rgb.max(axis=2)<82
    data[dark]=[109,56,59]
    blue=(rgb[:,:,2]>rgb[:,:,0]+18)&(rgb[:,:,1]>rgb[:,:,0]+17)
    data[blue]=[182,95,99]
    image=Image.fromarray(data).convert('RGBA')
    dirty_mouth(image)
    image.convert('RGB').save(ART/'bouche-corail-v2.png')


def dirty_mouth(image):
    # Dépôt de langue stylisé, limité à la surface où les microbes mangent.
    mask=Image.new('L',image.size)
    ImageDraw.Draw(mask).polygon(
        [(100,1132),(175,1040),(351,1024),(537,1082),(682,1021),(875,1042),(966,1151),
         (918,1517),(817,1711),(539,1816),(271,1722),(133,1505)],fill=255)
    layer=Image.new('RGBA',image.size)
    coating=Image.new('L',image.size)
    coating_draw=ImageDraw.Draw(coating)
    rng=np.random.default_rng(4909)
    patches=((267,1106,107,44),(535,1119,115,38),(805,1110,108,49),
             (293,1399,97,58),(644,1458,158,68),(477,1623,143,57))
    for x,y,rx,ry in patches:
        for _ in range(8):
            dx,dy=rng.uniform(-rx*.64,rx*.64),rng.uniform(-ry*.55,ry*.55)
            r=rng.uniform(.47,.82)
            coating_draw.ellipse((x+dx-rx*r,y+dy-ry*r,x+dx+rx*r,y+dy+ry*r),fill=255)
    coating=ImageChops.multiply(coating,mask)
    rim=ImageChops.subtract(coating.filter(ImageFilter.MaxFilter(5)),coating)
    border=Image.new('RGBA',image.size,(164,136,88))
    border.putalpha(rim.point(lambda value:round(value*.23)))
    layer.alpha_composite(border)
    film=Image.new('RGBA',image.size,(218,203,162))
    film.putalpha(coating.point(lambda value:round(value*.43)))
    layer.alpha_composite(film)
    draw=ImageDraw.Draw(layer)
    for _ in range(68):
        x,y=rng.integers(171,910),rng.integers(1055,1680)
        r=rng.integers(3,8)
        draw.ellipse((x-r,y-r*.58,x+r,y+r*.58),fill=(145,111,69,103))
    alpha=ImageChops.multiply(layer.getchannel('A'),mask).filter(ImageFilter.GaussianBlur(.45))
    layer.putalpha(alpha)
    image.alpha_composite(layer)
    # Petits débris et plaque visibles sur les contacts dents-gencives.
    draw=ImageDraw.Draw(image)
    for x,y,side in ((300,270,-1),(460,218,-1),(653,266,1),(791,348,1),
                     (890,475,1),(925,627,1),(206,420,-1),(155,568,-1)):
        draw.polygon([(x,y),(x+side*12,y+8),(x+side*7,y+30),(x-side*4,y+25)],
                     fill='#D5BC75',outline='#9C7455',width=2)
    for x,y in ((203,842),(838,911),(365,1026),(777,1092),(607,1570)):
        draw.polygon([(x-10,y-7),(x+10,y-11),(x+13,y+6),(x-5,y+12)],
                     fill='#89AA65',outline='#6D7351',width=2)


def meal():
    plate=remove_flat_background(Image.open(ART/'assiette-source.png').convert('RGBA'),tol=17)
    plate.thumbnail((322,190),Image.Resampling.LANCZOS)
    plate.save(ART/'assiette.png')
    mug=Image.new('RGBA',(140*3,149*3))
    draw=ImageDraw.Draw(mug)
    ink='#6D383B'
    draw.ellipse((83*3,37*3,137*3,106*3),fill='#FFF9ED',outline=ink,width=9)
    draw.ellipse((96*3,51*3,124*3,90*3),fill=(0,0,0,0),outline=ink,width=7)
    draw.rounded_rectangle((10*3,31*3,108*3,123*3),radius=20*3,fill='#FFF9ED',outline=ink,width=9)
    draw.ellipse((10*3,14*3,108*3,51*3),fill='#E9D4BD',outline=ink,width=9)
    draw.ellipse((19*3,23*3,99*3,43*3),fill='#704739')
    draw.arc((21*3,54*3,54*3,106*3),100,210,fill='#C9BBA5',width=8)
    mug.resize((140,149),Image.Resampling.LANCZOS).save(ART/'tasse.png')


def rooms():
    image=Image.new('RGB',(1080,1920),'#E4E2D7')
    d=ImageDraw.Draw(image)
    d.rectangle((0,1485,1080,1920),fill='#8D8C84')
    d.line((0,1480,1080,1480),fill='#345C62',width=17)
    d.rounded_rectangle((122,214,431,591),radius=8,fill='#D7AF89',outline=INK,width=7)
    d.rectangle((138,232,415,574),fill='#91D3DF',outline=INK,width=4)
    d.line((277,232,277,574),fill='#D7AF89',width=14)
    d.line((138,399,415,399),fill='#D7AF89',width=13)
    d.rounded_rectangle((465,661,936,871),radius=9,fill='#D7AF89',outline=INK,width=5)
    d.rounded_rectangle((478,674,923,858),radius=4,fill='#345C62',outline=INK,width=3)
    d.text((700,705),'PENSÉE DU MATIN',font=font('Fredoka',23),fill='#FFF9ED',anchor='mm')
    d.line((516,728,886,728),fill='#91D3DF',width=2)
    for y,text in ((765,'Le café réveille.'),(817,'Ton haleine aussi.')):
        d.text((700,y),text,font=font('Caveat',44),fill='#FFF9ED',anchor='mm')
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
             'acteurs':{'cerveau':person('personnages/cerveau',540,1114,.65,[0,0])},
             'repliques':lines('reveil')},
            {'id':'buffet','organe':'Bouche','decor':'art/bouche-corail-v2.png','transition':'coupe','zoom':[1,1],
             'acteurs':{'verte':person('personnages/verte',363,1199,1.46,[.7,0]),
                        'rouge':person('personnages/rouge',747,1333,1.06,[-.7,0])},
             'mini_badges':[{'acteur':'verte','texte':'Bactéries','delai':.13,'duree':1.8,'decalage':[4,-170]}],
             'repliques':lines('buffet')},
            {'id':'petit-dejeuner','decor':'art/petit-dejeuner.png','transition':'coupe','zoom':[1.3,1.3],'centre':[540,1270],
             'acteurs':{'ami':person('personnages/ami',299,1665,1.03,[.8,0]),
                        'lea':person('personnages/lea-table',793,1665,.86,[-.8,-.1])},
             'repliques':lines('petit-dejeuner')},
            {'id':'cabinet','decor':'art/cabinet-009.png','transition':'coupe','zoom':[1,1],
             'acteurs':clinic,'repliques':office},
        ],
    }


if __name__=='__main__':
    characters()
    mouth()
    meal()
    rooms()
    Image.new('RGB',(1080,1920),'#E75261').save(ART/'cerveau-corail.png')
    (ROOT/'episode.yaml').write_text(yaml.safe_dump(build(),allow_unicode=True,sort_keys=False))
