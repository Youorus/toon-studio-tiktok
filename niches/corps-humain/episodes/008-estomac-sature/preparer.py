"""Prépare les nouveaux actifs et les décors du 008."""
from pathlib import Path

from PIL import Image, ImageDraw
import yaml

from dialogues import VOICES, lines
from lea_corpulence import prepare as prepare_lea
from toonstudio.drawing import font, remove_flat_background

ROOT=Path(__file__).resolve().parent
NICHE=ROOT.parents[1]
ART=ROOT/'art'
STYLE=yaml.safe_load((NICHE/'niche.yaml').read_text())['direction_artistique']
INK='#6D383B'


def props():
    sheet=Image.open(ART/'plateau-source.png').convert('RGBA')
    w,h=sheet.size
    for i,name in enumerate(('burger','frites','poulet','sac')):
        x,y=i%2*w//2,i//2*h//2
        cut=remove_flat_background(sheet.crop((x,y,x+w//2,y+h//2)),tol=25)
        cut.thumbnail((330,330),Image.Resampling.LANCZOS)
        cut.save(ART/f'{name}.png')
    phone=Image.new('RGBA',(112,168))
    d=ImageDraw.Draw(phone)
    d.rounded_rectangle((14,10,98,159),radius=22,fill='#34555A',outline=INK,width=6)
    d.rounded_rectangle((24,29,88,132),radius=9,fill='#B2CBCB',outline=INK,width=4)
    d.line((45,21,65,21),fill='#FFF9ED',width=5)
    d.ellipse((48,141,62,151),fill='#91D3DF')
    phone.save(ART/'telephone.png')
    soda=Image.new('RGBA',(114,156))
    d=ImageDraw.Draw(soda)
    d.polygon([(17,55),(100,55),(87,145),(29,145)],fill='#D45C58',outline=INK,width=5)
    d.polygon([(62,56),(66,14),(98,5),(101,13),(75,22),(71,56)],fill='#91D3DF',outline=INK,width=3)
    d.rounded_rectangle((11,43,105,64),radius=8,fill='#FFF9ED',outline=INK,width=5)
    d.ellipse((43,84,74,115),fill='#FFF9ED')
    soda.save(ART/'soda.png')


def brain():
    src=remove_flat_background(Image.open(ART/'cerveau-source.png').convert('RGBA'),tol=25)
    src=src.resize((round(src.width*360/src.height),360),Image.Resampling.LANCZOS)
    w,h=src.size
    x,y=round(.54*w),round(.47*h)
    skin='#%02X%02X%02X'%src.getpixel((x,y))[:3]
    rig={
        'nom':'Cerveau','type':'organe',
        'couches':[{'id':'corps','images':{'defaut':'corps.png'},'pivot':[w//2,h-1]}],
        'visage':{'couche':'corps','yeux':[x,y],'rayon_oeil':33,'ecart':2.21,'trait':.13,
                  'bouche':[x,y+64],'peau':skin,'paupiere':.08,'pupille':.76},
        'mouvement':{'souplesse':.45,'respiration':.008},
    }
    folder=ROOT/'personnages'/'cerveau'
    folder.mkdir(parents=True,exist_ok=True)
    src.save(folder/'corps.png')
    (folder/'personnage.yaml').write_text(yaml.safe_dump(rig,allow_unicode=True,sort_keys=False))


def backgrounds():
    room=Image.open(NICHE/STYLE['cabinet']).convert('RGBA')
    d=ImageDraw.Draw(room)
    for y,text in ((536,'Pose tes'),(566,'couverts.'),(599,'Écoute'),(629,'ton ventre.')):
        d.text((807,y),text,font=font('Caveat',28),fill='#405854',anchor='mm')
    room.save(ART/'cabinet-008.png')

    body=Image.open(NICHE/'decors'/'estomac-corail.png').convert('RGB')
    split=Image.new('RGB',(1080,1920),'#E75261')
    lower=body.crop((210,440,1060,1390)).resize((1080,1074),Image.Resampling.LANCZOS)
    split.paste(lower,(0,846))
    d=ImageDraw.Draw(split)
    d.line((0,846,1080,846),fill='#8F474B',width=13)
    d.line((0,839,1080,839),fill='#F6A09D',width=5)
    split.save(ART/'appel-corail.png')


def person(path,x,y,scale,gaze):
    return {'perso':path,'x':x,'y':y,'echelle':scale,'regard':gaze}


def build():
    stomach='episodes/006-antibioresistance/personnages/estomac'
    clinic={role:person('personnages/'+STYLE['casting'][role]['rig'],x,1612,scale,gaze)
            for role,x,scale,gaze in (('lea',703,1.06,[-.85,-.5]),('docteure',309,1.08,[.8,.5]))}
    clinic['lea']=person('personnages/lea-corpulence',710,1612,1.0,[-.85,-.5])
    office=lines('cabinet')
    office[-1].update(carte=STYLE['abonnement_final'],regards={'docteure':[0,0]})
    sfx={
        'ploc':{'fichier':'episodes/006-antibioresistance/sons/ploc.wav','volume':.46},
        'plouf':{'fichier':'episodes/006-antibioresistance-v2/sons/plouf.wav','volume':.48},
        'glisse':{'fichier':'episodes/006-antibioresistance-v3/sons/glisse.wav','volume':.26},
        'ring':{'fichier':'episodes/006-antibioresistance-v3/sons/radio.wav','volume':.45},
    }
    return {
        'titre':'Estomac en surcharge','niche':'corps-humain','degrade_bas':False,'voix':VOICES,'bruitages':sfx,
        'plans':[
            {'id':'arrivage','decor':'decors/estomac-corail.png','organe':'Estomac','transition':'coupe',
             'zoom':[1,1],'acteurs':{'estomac':person(stomach,803,801,1.28,[-.64,.32])},
             'repliques':lines('arrivage')},
            {'id':'appel','decor':'art/appel-corail.png','organe':'Cerveau','transition':'coupe','zoom':[1,1],
             'acteurs':{'cerveau':person('personnages/cerveau',540,728,.92,[.0,.69]),
                        'estomac':person(stomach,752,1254,1.18,[.0,-.7])},
             'repliques':lines('appel'),
             'mini_badges':[{'acteur':'estomac','texte':'Estomac','delai':.15,'duree':1.62,'decalage':[-260,-136]}]},
            {'id':'cabinet','decor':'art/cabinet-008.png','transition':'coupe','zoom':[1,1],
             'acteurs':clinic,'repliques':office},
        ],
    }


if __name__=='__main__':
    props()
    brain()
    backgrounds()
    prepare_lea(NICHE,ROOT/'personnages'/'lea-corpulence')
    (ROOT/'episode.yaml').write_text(yaml.safe_dump(build(),allow_unicode=True,sort_keys=False))
