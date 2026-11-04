"""Calques réemployés du 005 et du 006-v3 ; aucun nouveau personnage généré."""
from copy import deepcopy
from pathlib import Path
import shutil
import numpy as np
from PIL import Image, ImageDraw
import yaml

from dialogues import VOICES, lines
from toonstudio.drawing import cover, font, remove_flat_background

ROOT = Path(__file__).resolve().parent
NICHE = ROOT.parents[1]
ART = ROOT/'art'
INK, CREAM, CORAL = '#6D383B', '#FFF9ED', '#E75261'

def save_rig(name, cfg):
    folder = ROOT/'personnages'/name
    folder.mkdir(parents=True, exist_ok=True)
    (folder/'personnage.yaml').write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))
    return folder

def characters():
    image = remove_flat_background(Image.open(NICHE/'episodes/005-caca-demission/art/caca-b.png'), tol=24)
    image = image.resize((310, 410), Image.Resampling.LANCZOS)
    folder = save_rig('caca', {
        'nom': 'La selle coincée', 'type': 'organe',
        'couches': [{'id': 'corps', 'pivot': [155, 410], 'images': {'defaut': 'corps.png'}}],
        'visage': {'couche': 'corps', 'yeux': [173, 175], 'rayon_oeil': 26, 'ecart': 2.2,
                   'bouche': [178, 242], 'largeur_bouche': 57, 'peau': '#71392E',
                   'pupille': .76, 'trait': .13, 'paupiere': .10},
        'membres': {'bras': {'epaule_g': [30, 250], 'epaule_d': [285, 250], 'longueur': 77, 'epaisseur': 9},
                    'jambes': {'hanche_g': [105, 398], 'hanche_d': [220, 398], 'longueur': 66, 'epaisseur': 10}},
        'mouvement': {'souplesse': .28, 'respiration': .003}})
    image.save(folder/'corps.png')
    src = NICHE/'episodes/006-antibioresistance-v3/personnages/policier-comique'
    cfg = deepcopy(yaml.safe_load((src/'personnage.yaml').read_text()))
    cfg['nom'] = 'Le gardien du sphincter'
    cfg['couches'] = [layer for layer in cfg['couches'] if layer['id'] in {'corps', 'bottes'}]
    cfg['couches'][0]['images']['travail']='corps-travail.png'
    cfg['poses'] = {'travail': {'corps': {'image':'travail'}}}
    folder = save_rig('policier', cfg)
    for name in ('corps.png', 'bottes.png'): shutil.copyfile(src/name, folder/name)
    image=Image.open(src/'corps.png').convert('RGBA');d=ImageDraw.Draw(image)
    # Les mains de repos sont retirées quand les bras articulés prennent le relais.
    d.polygon([(115,294),(137,298),(138,315),(153,325),(146,340),(115,337)],fill='#59A5CF')
    d.polygon([(218,301),(244,301),(244,329),(221,331)],fill=(0,0,0,0))
    image.save(folder/'corps-travail.png')

def decors():
    image = cover(Image.open(NICHE/'episodes/005-caca-demission/art/colon.png').convert('RGB'))
    data = np.array(image)
    # Réemploie les replis du côlon ; homogénéise les grands aplats rouges du plateau.
    mask = (data[:,:,0] > 208) & (data[:,:,1] < 136) & (data[:,:,2] < 141)
    data[mask] = [231,82,97]
    image = Image.fromarray(data).convert('RGBA')
    d = ImageDraw.Draw(image)
    d.ellipse((238,1360,951,1483), fill='#C95060')
    d.rounded_rectangle((498,730,942,1415),radius=174,fill='#9D454C',outline=INK,width=9)
    d.rounded_rectangle((534,765,909,1399),radius=148,fill='#71393E',outline=INK,width=7)
    d.rounded_rectangle((490,625,952,720),radius=15,fill='#F5B77C',outline=INK,width=7)
    d.rounded_rectangle((502,637,940,707),radius=9,outline=CREAM,width=3)
    d.text((721,673),'SORTIE DES SELLES',font=font('Fredoka',29),fill=CREAM,anchor='mm')
    image.save(ART/'rectum-corail.png')

    image = Image.new('RGBA',(1080,1920),CORAL)
    d = ImageDraw.Draw(image)
    # Coupe anatomique simple, ouverture inférieure lisible, tissus chauds jusque dans les coins.
    d.rounded_rectangle((270,-220,839,1685),radius=250,fill='#B65F63',outline=INK,width=12)
    d.rounded_rectangle((337,-260,776,1677),radius=200,fill='#F3A082',outline=INK,width=8)
    d.polygon([(414,1550),(448,1745),(637,1745),(686,1549)],fill='#F3A082')
    d.line((414,1548,448,1738),fill=INK,width=7)
    d.line((686,1548,637,1738),fill=INK,width=7)
    d.arc((339,1414,540,1674),260,80,fill='#E86675',width=29)
    d.arc((568,1414,768,1674),100,280,fill='#E86675',width=29)
    image.save(ART/'passage-corail.png')

    image = Image.new('RGBA',(1080,1920),'#E5E6E0');d=ImageDraw.Draw(image)
    for x in range(0,1081,180): d.line((x,0,x,1420),fill='#C6D2CF',width=4)
    for y in range(0,1421,220): d.line((0,y,1080,y),fill='#C6D2CF',width=4)
    d.polygon([(0,1420),(1080,1420),(1080,1920),(0,1920)],fill='#AFBDBA',outline=INK,width=7)
    d.rounded_rectangle((133,1030,434,1450),radius=35,fill=CREAM,outline=INK,width=7)
    d.rounded_rectangle((151,1060,414,1280),radius=22,fill='#F2F0E8',outline=INK,width=4)
    d.rounded_rectangle((209,1450,409,1777),radius=60,fill='#E3E8E2',outline=INK,width=7)
    d.ellipse((100,1320,519,1625),fill=CREAM,outline=INK,width=8)
    d.ellipse((138,1357,481,1565),fill='#91D3DF',outline=INK,width=5)
    d.ellipse((165,1380,455,1536),fill='#B3E0E3',outline='#6EABAD',width=3)
    d.ellipse((255,1427,358,1486),fill='#835243',outline=INK,width=3)
    d.line((278,1450,329,1460),fill='#D45C58',width=7)
    d.rounded_rectangle((180,606,494,831),radius=15,fill='#24666D',outline=INK,width=6)
    d.text((337,688),'ICI, ON NE',font=font('Fredoka',30),fill=CREAM,anchor='mm')
    d.text((337,744),'FAIT PAS LA QUEUE.',font=font('Fredoka',25),fill=CREAM,anchor='mm')
    image.save(ART/'toilettes.png')

    style=yaml.safe_load((NICHE/'niche.yaml').read_text())['direction_artistique']
    image=Image.open(NICHE/style['cabinet']).convert('RGBA');d=ImageDraw.Draw(image)
    for y,text in ((537,'Envie d’y aller ?'),(575,'N’attends pas.'),(612,'Ton corps a parlé.')):
        d.text((807,y),text,font=font('Caveat',25),fill='#405854',anchor='mm')
    image.save(ART/'cabinet-010.png')

def actor(path,x,y,scale=1,gaze=(0,0)):
    return {'perso':path,'x':x,'y':y,'echelle':scale,'regard':list(gaze)}

def build():
    scene = {'id':'sortie','organe':'Rectum','decor':'art/rectum-corail.png','transition':'coupe','zoom':[1,1],
        'acteurs': {'policier':actor('personnages/policier',262,1230,1.25,(.8,0)),
                    'caca':actor('personnages/caca',650,1336,1.10,(-.8,0))},
        'mini_badges':[{'acteur':'caca','texte':'Selle','delai':.1,'duree':1.65,'decalage':[0,-150]},
                       {'acteur':'policier','texte':'Sphincter','replique':1,'duree':1.8,'decalage':[-18,-138]}],
        'repliques':lines('sortie')}
    office=lines('cabinet')
    office[-1].update({'carte':{'type':'bouton','texte':'ABONNE-TOI','couleur':'#24666D','largeur':610},'regards':{'docteure':[0,0]}})
    cfg={'titre':'La sortie est bloquée','niche':'corps-humain','degrade_bas':False,'voix':VOICES,
         'bruitages':{name:{'fichier':path,'volume':volume} for name,path,volume in (
             ('toc','episodes/006-antibioresistance-v3/sons/stop.wav',.28),
             ('glisse','episodes/006-antibioresistance-v3/sons/glisse.wav',.24),
             ('ploc','episodes/006-antibioresistance/sons/ploc.wav',.39))},
         'plans':[scene,
             {'id':'passage','organe':'Rectum','decor':'art/passage-corail.png','transition':'coupe','zoom':[1,1],
              'acteurs':{'caca':actor('personnages/caca',548,1120,.65,(0,0))},'repliques':lines('passage')},
             {'id':'toilettes','decor':'art/toilettes.png','transition':'coupe','zoom':[1,1],
              'acteurs':{'lea':actor('personnages/lea-aplats',749,1660,1.02,(-.7,.7))},'repliques':lines('toilettes')},
             {'id':'cabinet','decor':'art/cabinet-010.png','transition':'coupe','zoom':[1,1],
              'acteurs':{'lea':actor('personnages/lea-aplats',703,1612,1.06,(-.85,-.5)),
                         'docteure':actor('personnages/docteure-aplats',309,1612,1.08,(.8,.5))},'repliques':office}]}
    (ROOT/'episode.yaml').write_text(yaml.safe_dump(cfg,allow_unicode=True,sort_keys=False))

if __name__=='__main__':
    ART.mkdir(parents=True,exist_ok=True)
    characters();decors();build()
