"""Nouvelle mise en scène : CACA monobloc, vraie coupe, cuvette et Léa debout."""
from copy import deepcopy
from pathlib import Path
import json
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import label
from scipy.interpolate import PchipInterpolator
import yaml

from dialogues import VOICES,lines
from toonstudio.drawing import cover,font,remove_flat_background

ROOT=Path(__file__).resolve().parent
NICHE=ROOT.parents[1]
ART=ROOT/'art/v2'
INK='#6D383B'
CORAL='#E75261'
BLOOD='#D63748'

def save_cfg(path,cfg):
    path.mkdir(parents=True,exist_ok=True)
    (path/'personnage.yaml').write_text(yaml.safe_dump(cfg,allow_unicode=True,sort_keys=False))

def caca():
    body=remove_flat_background(Image.open(ART/'caca.png'),tol=25).resize((360,460),Image.Resampling.LANCZOS)
    path=ROOT/'personnages/caca-v2';path.mkdir(exist_ok=True)
    # Le brun reste lumineux ; l'ancien corps empilé du 005 est écarté.
    a=np.asarray(body).copy();rgb=a[:,:,:3].astype(float)
    warm=(rgb[:,:,0]>rgb[:,:,1]*1.35)&(rgb[:,:,1]>rgb[:,:,2]*1.15)&(a[:,:,3]>0)
    a[warm,:3]=np.clip(rgb[warm]*[.80,.88,.92],0,255)
    body=Image.fromarray(a);body.save(path/'corps.png')
    images={'defaut':'corps.png'};poses={}
    for index in range(25):
        marked=body.copy();d=ImageDraw.Draw(marked)
        progress=index/24*3
        for k,(x,y) in enumerate(((66,265),(94,293),(124,316))):
            amount=max(0,min(1,progress-k))
            if amount:
                points=[(x+9*t,y+94*t) for t in np.linspace(0,amount,18)]
                d.line(points,fill=BLOOD,width=9,joint='curve')
        name=f'marque-{index:02d}';marked.save(path/(name+'.png'));images[name]=name+'.png'
        poses[name]={'corps':{'image':name}}
    skin='#%02X%02X%02X'%body.getpixel((215,265))[:3]
    cfg={'nom':'CACA','type':'organe','couches':[{'id':'corps','pivot':[180,460],'images':images}],
         'visage':{'couche':'corps','yeux':[218,264],'rayon_oeil':26,'ecart':2.18,'bouche':[218,330],
                    'largeur_bouche':57,'peau':skin,'pupille':.76,'trait':.10,'paupiere':.05},
         'poses':poses,'membres':{
             'bras':{'epaule_g':[20,300],'epaule_d':[338,300],'longueur':79,'epaisseur':8,'couleur':'#FFF9ED'},
             'jambes':{'hanche_g':[108,443],'hanche_d':[250,443],'longueur':65,'epaisseur':9,'couleur':'#FFF9ED','chaussure':'#FFF9ED'}},
         'mouvement':{'souplesse':.11,'respiration':.002}}
    save_cfg(path,cfg)
    cut=ROOT/'personnages/caca-coupe-v2';cut.mkdir(exist_ok=True)
    cfg=deepcopy(cfg);cfg.pop('membres');cfg['couches'][0]['images']={'defaut':'corps.png'};cfg.pop('poses')
    rgba=Image.new('RGBA',(body.width+32,body.height+32))
    edge=Image.new('L',rgba.size);edge.paste(body.getchannel('A'),(16,16))
    edge=edge.filter(ImageFilter.MaxFilter(23))
    tint=Image.new('RGBA',rgba.size,BLOOD);tint.putalpha(edge)
    rgba.alpha_composite(tint);rgba.alpha_composite(Image.open(path/'marque-24.png'),(16,16))
    rgba.save(cut/'corps.png')
    cfg['couches'][0]['pivot']=[196,476]
    cfg['visage']['yeux']=[234,280];cfg['visage']['bouche']=[234,346]
    save_cfg(cut,cfg)

def lea_debout():
    src=NICHE/'personnages/lea-aplats';cfg=deepcopy(yaml.safe_load((src/'personnage.yaml').read_text()))
    original=Image.open(src/'corps.png').convert('RGBA')
    # Tête, coiffure, yeux, nez et cou identiques. La chaise et les jambes assises ne sont pas repris.
    canvas=Image.new('RGBA',(320,800));d=ImageDraw.Draw(canvas)
    skin='#%02X%02X%02X'%original.getpixel((130,170))[:3];shirt='#B86F55'
    d.rounded_rectangle((80,238,251,810),radius=35,fill=shirt,outline='#181313',width=2)
    d.polygon([(80,302),(72,800),(255,800),(250,302)],fill=shirt)
    d.line((81,289,73,800),fill='#181313',width=2);d.line((249,289,255,800),fill='#181313',width=2)
    d.arc((117,271,225,406),25,115,fill='#6D383B',width=2)
    canvas.alpha_composite(original.crop((0,0,original.width,252)),(0,0))
    path=ROOT/'personnages/lea-debout-v2';path.mkdir(exist_ok=True);canvas.save(path/'corps.png')
    cfg['couches'][0]['pivot']=[160,560]
    cfg['bras']=[{'id':'gauche','epaule':[86,267],'cote':-1,'longueur':178,'epaisseur':27,'peau':skin,'manche':shirt,'trait':.075},
                 {'id':'droite','epaule':[244,268],'cote':1,'longueur':167,'epaisseur':27,'peau':skin,'manche':shirt,'trait':.075}]
    cfg['poses']={'defaut':{'gauche':{'epaule':30,'coude':22,'main':'ouvert'},'droite':{'epaule':20,'coude':18,'main':'ouvert'}},
                  'question':{'gauche':{'epaule':68,'coude':27,'main':'ouvert'},'droite':{'epaule':42,'coude':30,'main':'ouvert'}}}
    save_cfg(path,cfg)

def corail(source):
    image=cover(Image.open(source).convert('RGB'));pixels=np.asarray(image).copy();rgb=pixels.astype(int)
    # Le fond rouge connecté au bord reprend exactement le corail validé.
    mask=(rgb[:,:,0]>200)&(rgb[:,:,1]<143)&(rgb[:,:,2]<149)
    components,_=label(mask);outer=np.unique(np.r_[components[0,:],components[-1,:],components[:,0],components[:,-1]])
    pixels[np.isin(components,outer[outer!=0])]=[231,82,97]
    return Image.fromarray(pixels).convert('RGBA')

def coupe_jouable():
    """Coupe organique en calques cel ; le trajet de jeu est aussi celui de la cavité."""
    ys=np.array([-300,100,420,780,1150,1520,1900,2200],float)
    xs=np.array([620,590,460,620,500,560,540,540],float)
    widths=np.array([490,520,500,470,400,330,250,230],float)
    center=PchipInterpolator(ys,xs);width=PchipInterpolator(ys,widths)
    t=np.linspace(-300,2200,500);x=center(t);half=width(t)/2
    slope=center.derivative()(t);normal=1/np.sqrt(1+slope*slope)
    scale=2;image=Image.new('RGBA',(2160,3840),CORAL);d=ImageDraw.Draw(image)
    def boundary(extra,side,sel=slice(None)):
        r=half+extra
        # Les bords restent des courbes simples en y, sans repli mathématique aux virages.
        return list(zip((x+side*r)[sel],t[sel]))
    def paint(extra,fill,outline=INK,line=2):
        points=boundary(extra,-1)+list(reversed(boundary(extra,1)))
        pts=[(round(a*scale),round(b*scale)) for a,b in points]
        d.polygon(pts,fill=fill)
        d.line(pts+[pts[0]],fill=outline,width=round(line*scale),joint='curve')
    paint(104,'#B65F63',line=3)
    paint(73,'#D54D68',line=2)
    paint(46,'#F38088',line=2)
    paint(0,'#F6B18F',line=3)
    # Ombre courte d'un seul côté et deux reflets retenus, dans la finition de l'estomac étalon.
    sel=(t>160)&(t<1700)
    points=boundary(6,1,sel)+list(reversed(boundary(28,1,sel)))
    d.polygon([(round(a*scale),round(b*scale)) for a,b in points],fill='#EB806E')
    for lo,hi,side in ((40,230,-1),(1040,1180,-1)):
        sel=(t>lo)&(t<hi);points=boundary(64,side,sel)
        d.line([(round(a*scale),round(b*scale)) for a,b in points],fill='#F6AAAE',width=10,joint='curve')
    image.resize((1080,1920),Image.Resampling.LANCZOS).save(ART/'coupe-final.png')
    (ART/'trajet-coupe.json').write_text(json.dumps({'y':ys.tolist(),'x':xs.tolist(),'largeur_lumiere':widths.tolist()},indent=2)+'\n')

def policier_marqueur():
    folder=ROOT/'personnages/policier'
    cfg=yaml.safe_load((folder/'personnage.yaml').read_text())
    source=NICHE/'episodes/006-antibioresistance-v3/personnages/policier-comique/corps.png'
    im=Image.open(source).convert('RGBA');d=ImageDraw.Draw(im)
    d.polygon([(218,301),(244,301),(244,329),(221,331)],fill=(0,0,0,0))
    im.save(folder/'corps-marqueur.png')
    cfg['couches'][0]['images']['marqueur']='corps-marqueur.png'
    cfg['poses']['marqueur']={'corps':{'image':'marqueur'}}
    save_cfg(folder,cfg)

def decors():
    source=ART/'rectum-propre.png'
    if not source.exists():source=ART/'rectum.png'
    room=corail(source);d=ImageDraw.Draw(room)
    d.ellipse((163,1400,956,1500),fill='#D65B69')
    d.rounded_rectangle((411,735,868,1438),radius=171,fill='#A44751',outline=INK,width=6)
    d.rounded_rectangle((446,770,830,1420),radius=145,fill='#7F3F48',outline=INK,width=4)
    d.rounded_rectangle((412,630,869,723),radius=12,fill='#E6AE72',outline=INK,width=5)
    d.rounded_rectangle((424,642,856,710),radius=7,outline='#FFF9ED',width=2)
    d.text((640,678),'SORTIE DU CACA',font=font('Fredoka',34),fill='#FFF9ED',anchor='mm')
    room.save(ART/'rectum-final.png')
    coupe_jouable()
    cover(Image.open(ART/'toilettes.png').convert('RGBA')).save(ART/'toilettes-final.png')
    # Vue de dessus, comme le gros plan de la référence, avec une eau délimitée pour les remous.
    scale=2;im=Image.new('RGBA',(1080*scale,1920*scale),'#E5E6E0');d=ImageDraw.Draw(im)
    def ellipse(box,fill,outline=INK,width=5):d.ellipse(tuple(round(x*scale) for x in box),fill=fill,outline=outline,width=width*scale)
    ellipse((-110,-355,1190,2045),'#FFF9ED',width=8)
    ellipse((-25,62,1105,1870),'#CADAD8',width=6)
    ellipse((35,170,1045,1775),'#A7D9DF',outline='#528B97',width=4)
    ellipse((105,270,980,1665),'#BCE4E7',outline='#8CCBD2',width=3)
    im.resize((1080,1920),Image.Resampling.LANCZOS).save(ART/'cuvette-vue-dessus.png')

def actor(path,x,y,scale=1,gaze=(0,0)):
    return {'perso':path,'x':x,'y':y,'echelle':scale,'regard':list(gaze)}

def build():
    office=lines('cabinet');office[-1].update({'carte':{'type':'bouton','texte':'ABONNE-TOI','couleur':'#24666D','largeur':610},'regards':{'docteure':[0,0]}})
    cfg={'titre':'La sortie est bloquée — V2','niche':'corps-humain','degrade_bas':False,'voix':VOICES,
         'bruitages':{name:{'fichier':path,'volume':volume} for name,path,volume in (
             ('toc','episodes/006-antibioresistance-v3/sons/clac.wav',.32),
             ('glisse','episodes/006-antibioresistance-v3/sons/glisse.wav',.28),
             ('ploc','episodes/006-antibioresistance/sons/ploc.wav',.43),
             ('glissade','sons/glissade.wav',.26),
             ('boing','episodes/006-antibioresistance-v3/sons/stop.wav',.22))},
         'plans':[
             {'id':'sortie','organe':'Rectum','decor':'art/v2/rectum-final.png','transition':'coupe','zoom':[1,1],
              'acteurs':{'policier':actor('personnages/policier',230,1210,1.25,(.8,.1)),
                         'caca':actor('personnages/caca-v2',625,1372,1.10,(-.8,-.2))},
              'mini_badges':[{'acteur':'caca','texte':'CACA','delai':.10,'duree':1.65,'decalage':[0,-143]},
                             {'acteur':'policier','texte':'SPHINCTER','replique':1,'duree':1.6,'decalage':[-15,-147]}],
              'repliques':lines('sortie')},
             {'id':'passage','organe':'Rectum','decor':'art/v2/coupe-final.png','transition':'coupe','zoom':[1,1],
              'acteurs':{'caca':actor('personnages/caca-coupe-v2',520,1120,.66,(.4,.5))},'repliques':lines('passage')},
             {'id':'cuvette','decor':'art/v2/cuvette-vue-dessus.png','transition':'coupe','zoom':[1,1],
              'acteurs':{'caca':actor('personnages/caca-coupe-v2',555,1290,1.05,(.1,-.3))},'repliques':lines('cuvette')},
             {'id':'toilettes','decor':'art/v2/toilettes-final.png','transition':'coupe','zoom':[1,1],
              'acteurs':{'lea':{**actor('personnages/lea-debout-v2',811,1830,1.62,(-.8,.6)),'pose':'question'}},'repliques':lines('toilettes')},
             {'id':'cabinet','decor':'art/cabinet-010.png','transition':'coupe','zoom':[1,1],
              'acteurs':{'lea':actor('personnages/lea-aplats',703,1612,1.06,(-.85,-.5)),
                         'docteure':actor('personnages/docteure-aplats',309,1612,1.08,(.8,.5))},'repliques':office}]}
    (ROOT/'episode.yaml').write_text(yaml.safe_dump(cfg,allow_unicode=True,sort_keys=False))

def sons():
    folder=ROOT/'sons';folder.mkdir(exist_ok=True)
    source=NICHE/'episodes/006-antibioresistance-v3/sons/glisse.wav'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',str(source),
        '-af','atempo=0.5,atempo=0.5,atempo=0.9,afade=t=in:d=0.10,afade=t=out:st=1.25:d=0.43',
        '-ar','48000','-ac','2',str(folder/'glissade.wav')],check=True)

if __name__=='__main__':
    caca();lea_debout();policier_marqueur();decors();sons();build()
