"""Calques des personnages à table. Chaque bras visible appartient à un seul rig."""
from copy import deepcopy
import math

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation
import yaml

SKIN='#C9946C'
LEA_SKIN='#BE936F'
INK='#181313'


def config(folder,data):
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'personnage.yaml').write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False))


def flat_skin(image):
    data=np.array(image)
    rgb=data[:,:,:3].astype(int)
    yy=np.arange(image.height)[:,None]
    light=(rgb.min(axis=2)>170)&(rgb[:,:,0]>rgb[:,:,2]+12)
    warm=(rgb[:,:,0]>150)&(rgb[:,:,1]>95)&(rgb[:,:,0]>rgb[:,:,1]+25)&(rgb[:,:,1]>rgb[:,:,2]+15)&(yy>190)
    skin=(light|warm)&(yy<505)&(data[:,:,3]>120)
    data[skin,:3]=[201,148,108]
    return Image.fromarray(data)


def retain_colors(image,polygon,colors):
    a=np.asarray(image)
    mask=Image.new('L',image.size)
    ImageDraw.Draw(mask).polygon(polygon,fill=255)
    region=np.asarray(mask)>0
    rgb=a[:,:,:3].astype(int)
    colored=np.zeros(region.shape,bool)
    for color in colors:
        colored|=np.linalg.norm(rgb-np.array(color),axis=2)<34
    selected=binary_dilation(colored&region,iterations=2)&region
    out=a.copy()
    out[:,:,3]=np.where(selected,a[:,:,3],0)
    return Image.fromarray(out)


def prepare_lea(niche,root):
    source=niche/'personnages'/'lea-aplats'
    original=Image.open(source/'corps.png').convert('RGBA')
    cfg=yaml.safe_load((source/'personnage.yaml').read_text())
    shirt=original.getpixel((157,265))[:3]
    pants=original.getpixel((180,490))[:3]
    upper_left=retain_colors(original,
        [(103,231),(126,249),(112,348),(104,385),(64,385),(73,327),(83,264)],
        (shirt,(190,147,111)))
    resting_left=retain_colors(original,
        [(68,362),(115,374),(96,425),(95,450),(84,474),(51,482),(31,462),(36,439),(52,411)],
        (shirt,(190,147,111)))

    # Reconstituer les aplats qui se trouvent sous le bras droit dessiné dans l'original.
    # La tête et le bas du corps sont issus du modèle de série.
    body=original.resize((828,2223),Image.Resampling.LANCZOS)
    draw=ImageDraw.Draw(body)
    draw.rectangle((94*3,224*3,259*3,479*3),fill=(0,0,0,0))
    draw.rectangle((31*3,410*3,110*3,482*3),fill=(0,0,0,0))

    def path(start,*curves,fill):
        pts=[start]
        for curve in curves:
            if len(curve)==2:
                pts.append(curve)
                continue
            ax,ay,bx,by,ex,ey=curve
            x,y=pts[-1]
            pts.extend(((1-t)**3*x+3*(1-t)**2*t*ax+3*(1-t)*t*t*bx+t**3*ex,
                        (1-t)**3*y+3*(1-t)**2*t*ay+3*(1-t)*t*t*by+t**3*ey)
                       for t in np.linspace(1/30,1,30))
        points=[(round(x*3),round(y*3)) for x,y in pts]
        draw.polygon(points,fill=fill)
        draw.line(points+[points[0]],fill=INK,width=6,joint='curve')

    path((56,429),(99,414,211,419,247,426),(266,446,272,482,252,504),
         (215,527,140,525,98,507),(47,488),(28,463,29,441,56,429),fill=pants)
    path((116,218),(149,222,176,226,193,219),(216,221,235,232,239,254),
         (239,305,228,355,231,418),(201,432,126,444,91,428),
         (94,383,95,326,104,291),(108,269,113,239,116,218),fill=shirt)
    draw.arc((101*3,259*3,160*3,341*3),91,240,fill=INK,width=5)
    draw.arc((147*3,321*3,198*3,341*3),5,158,fill=INK,width=4)
    draw.arc((116*3,208*3,197*3,229*3),5,175,fill=INK,width=4)
    body=body.resize(original.size,Image.Resampling.LANCZOS)
    body.alpha_composite(upper_left)
    # La tête reste un collage à l'échelle d'origine, avec ses yeux dessinés.
    body.paste((0,0,0,0),(0,0,276,224))
    body.alpha_composite(original.crop((0,0,276,224)),(0,0))
    base=root/'personnages'/'lea-table'
    base.mkdir(parents=True,exist_ok=True)
    body.save(base/'corps.png')
    cfg['nom']='Léa à table'
    config(base,cfg)

    # Rig de premier plan, composé après la table. Le bras droit d'origine est absent du corps.
    folder=root/'personnages'/'lea-bras'
    folder.mkdir(parents=True,exist_ok=True)
    Image.new('RGBA',original.size).save(folder/'vide.png')
    resting_left.save(folder/'avant-bras-gauche.png')
    for name,h,shape in [('bras-droit',142,0),('avant-bras-droit',142,1)]:
        im=Image.new('RGBA',(60*3,h*3))
        d=ImageDraw.Draw(im)
        d.rounded_rectangle((10*3,5*3,50*3,134*3),radius=19*3,fill=shirt,outline=INK,width=6)
        if shape:
            d.rectangle((10*3,112*3,50*3,132*3),fill=shirt,outline=INK,width=5)
            for x in range(16,49,8):
                d.line((x*3,115*3,x*3,130*3),fill=INK,width=3)
        im.resize((60,h),Image.Resampling.LANCZOS).save(folder/f'{name}.png')
    for pose in ('repos','pince'):
        im=Image.new('RGBA',(56*3,68*3))
        d=ImageDraw.Draw(im)
        d.rounded_rectangle((11*3,3*3,43*3,43*3),radius=12*3,fill=LEA_SKIN,outline=INK,width=5)
        if pose=='repos':
            for i in range(4):
                x=12+i*8
                d.rounded_rectangle((x*3,29*3,(x+9)*3,(55-i*2)*3),radius=4*3,fill=LEA_SKIN,outline=INK,width=4)
        else:
            # L'index et le pouce forment une pince. Le regard reste dégagé.
            d.ellipse((14*3,28*3,44*3,58*3),fill=LEA_SKIN,outline=INK,width=5)
            d.ellipse((24*3,35*3,37*3,47*3),fill=(0,0,0,0),outline=INK,width=4)
            for x in (16,24):
                d.line((x*3,12*3,x*3,27*3),fill=INK,width=3)
        im.resize((56,68),Image.Resampling.LANCZOS).save(folder/f'main-{pose}.png')
    foreground={
        'nom':'Bras de Léa au premier plan','type':'humain',
        'couches':[
            {'id':'corps','images':{'defaut':'vide.png'},'pivot':[138,740]},
            {'id':'avant-bras-gauche','parent':'corps','attache':[0,0],'pivot':[0,0],
             'images':{'defaut':'avant-bras-gauche.png'},'z':1},
            {'id':'bras-droit','parent':'corps','attache':[222,249],'pivot':[30,20],
             'images':{'defaut':'bras-droit.png'},'z':2},
            {'id':'avant-bras-droit','parent':'bras-droit','attache':[30,130],'pivot':[30,13],
             'images':{'defaut':'avant-bras-droit.png'},'z':3},
            {'id':'main-droite','parent':'avant-bras-droit','attache':[30,123],'pivot':[27,8],
             'images':{'defaut':'main-repos.png','pince':'main-pince.png'},'z':4},
        ],
        'poses':{'pince':{'main-droite':{'image':'pince'}}},
        'mouvement':cfg['mouvement'],
    }
    config(folder,foreground)


def prepare_friend_hands(root,image,movement):
    folder=root/'personnages'/'ami-mains'
    folder.mkdir(parents=True,exist_ok=True)
    skin=(201,148,108)
    hands=retain_colors(image,
        [(38,353),(106,365),(178,411),(242,421),(279,450),(281,492),
         (225,491),(189,459),(86,443),(42,425)],(skin,))
    hands.save(folder/'mains.png')
    Image.new('RGBA',image.size).save(folder/'vide.png')
    config(folder,{
        'nom':'Mains de l’ami au premier plan','type':'humain',
        'couches':[{'id':'corps','images':{'defaut':'vide.png'},'pivot':[image.width//2,image.height-1]},
                   {'id':'mains','parent':'corps','attache':[0,0],'pivot':[0,0],
                    'images':{'defaut':'mains.png'},'z':1}],
        'mouvement':movement,
    })


def arm_angles(progress):
    # Trajectoire de poignet dans le repère du modèle de Léa, puis articulation à deux segments.
    start=np.array([125.0,445.0])
    c1=np.array([224.0,387.0])
    c2=np.array([225.0,207.0])
    end=np.array([132.0,157.0])
    t=progress
    wrist=(1-t)**3*start+3*(1-t)**2*t*c1+3*(1-t)*t*t*c2+t**3*end
    dx,dy=wrist-np.array([222.0,249.0])
    distance=math.hypot(dx,dy)
    upper,forearm=110.0,110.0
    bend=math.acos(np.clip((distance*distance-upper*upper-forearm*forearm)/(2*upper*forearm),-1,1))
    shoulder=math.atan2(-dx,dy)-math.acos(np.clip((upper*upper+distance*distance-forearm*forearm)/(2*upper*distance),-1,1))
    return {'bras-droit':math.degrees(shoulder),'avant-bras-droit':math.degrees(bend)}
