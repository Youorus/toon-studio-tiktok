"""Calques des personnages à table. Chaque bras visible appartient à un seul rig."""
import numpy as np
from PIL import Image, ImageDraw
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


def prepare_lea(niche,root):
    source=niche/'personnages'/'lea-aplats'
    original=Image.open(source/'corps.png').convert('RGBA')
    cfg=yaml.safe_load((source/'personnage.yaml').read_text())
    shirt=original.getpixel((157,265))[:3]
    pants=original.getpixel((180,490))[:3]
    # Reconstituer les aplats qui se trouvent sous le bras droit dessiné dans l'original.
    # La tête et le bas du corps sont issus du modèle de série.
    body=original.resize((828,2223),Image.Resampling.LANCZOS)
    draw=ImageDraw.Draw(body)
    draw.rectangle((0,211*3,828,482*3),fill=(0,0,0,0))

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
    path((113,216),(89,229,78,270,76,305),(62,353,57,384,57,410),
         (81,414,98,415,105,409),(109,372,121,309,126,272),
         (129,240,123,221,113,216),fill=shirt)
    path((110,211),(149,224,180,221,193,211),(216,216,235,232,239,254),
         (239,305,228,355,231,418),(201,432,126,444,91,428),
         (94,383,95,326,104,291),(108,269,110,239,110,211),fill=shirt)
    draw.arc((101*3,259*3,160*3,341*3),91,240,fill=INK,width=5)
    draw.arc((147*3,321*3,198*3,341*3),5,158,fill=INK,width=4)
    draw.arc((116*3,208*3,197*3,229*3),5,175,fill=INK,width=4)
    body=body.resize(original.size,Image.Resampling.LANCZOS)
    # La tête reste un collage à l'échelle d'origine, avec ses yeux dessinés.
    body.paste((0,0,0,0),(0,0,276,211))
    body.alpha_composite(original.crop((0,0,276,211)),(0,0))
    base=root/'personnages'/'lea-table'
    base.mkdir(parents=True,exist_ok=True)
    body.save(base/'corps.png')
    cfg['nom']='Léa à table'
    config(base,cfg)
