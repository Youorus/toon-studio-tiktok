"""Costume et silhouette propres au 008, avec la tête approuvée de Léa."""
from copy import deepcopy
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
import yaml

INK='#181313'
PULL='#B56E55'
PANTS='#714D5E'
SKIN='#BE936F'
CHAIR='#236873'


def prepare(niche,folder):
    source=niche/'personnages'/'lea-aplats'
    img=Image.open(source/'corps.png').convert('RGBA')
    scale=3
    body=Image.new('RGBA',(410*scale,741*scale))
    draw=ImageDraw.Draw(body)

    def shape(start,*segments,fill):
        points=[start]
        for segment in segments:
            if len(segment)==2:
                points.append(segment)
            else:
                x,y=points[-1]
                ax,ay,bx,by,ex,ey=segment
                points.extend(((1-t)**3*x+3*(1-t)**2*t*ax+3*(1-t)*t*t*bx+t**3*ex,
                               (1-t)**3*y+3*(1-t)**2*t*ay+3*(1-t)*t*t*by+t**3*ey)
                              for t in np.linspace(1/30,1,30))
        pts=[(round(x*scale),round(y*scale)) for x,y in points]
        draw.polygon(pts,fill=fill)
        draw.line(pts+[pts[0]],fill=INK,width=3*scale,joint='curve')

    # Chaise identique dans ses teintes, assise adaptée au gabarit.
    draw.rounded_rectangle((225*scale,307*scale,389*scale,554*scale),radius=8*scale,
                           fill=CHAIR,outline=INK,width=3*scale)
    for x in (221,372):
        draw.rectangle((x*scale,530*scale,(x+17)*scale,740*scale),fill=CHAIR,outline=INK,width=2*scale)

    shape((111,432),(182,424,319,424,347,452),(373,482,345,530,286,538),
          (203,539),(192,596,189,663,184,714),(115,714),
          (103,649,101,590,104,542),(84,536),(80,591,83,658,83,714),
          (15,714),(6,653,0,586,7,525),(12,472,61,449,111,432),fill=PANTS)
    draw.line([(105*scale,494*scale),(101*scale,541*scale),(115*scale,711*scale)],
              fill=INK,width=2*scale)

    # Abdomen et hanches plus amples, avec les mêmes aplats et coutures de tenue.
    shape((172,216),(134,218,110,229,100,263),(83,296,87,328,92,354),
          (81,381,73,419,89,441),(143,476,269,485,335,448),
          (366,422,366,374,349,329),(341,284,341,244,308,228),
          (277,216,257,215,240,215),(172,216),fill=PULL)
    draw.arc((131*scale,309*scale,332*scale,444*scale),32,130,fill='#8A5144',width=2*scale)

    # Avant-bras ramenés devant le sac. Les mains gardent la teinte du modèle.
    for points in (((121,273),(89,351),(128,397)),((326,276),(316,356),(258,399))):
        pts=[(x*scale,y*scale) for x,y in points]
        draw.line(pts,fill=INK,width=46*scale,joint='curve')
        draw.line(pts,fill=PULL,width=40*scale,joint='curve')
        x,y=points[-1]
        draw.rounded_rectangle(((x-14)*scale,(y-12)*scale,(x+14)*scale,(y+16)*scale),
                               radius=8*scale,fill=SKIN,outline=INK,width=2*scale)

    # Les chaussures proviennent du dessin approuvé.
    for rect,to in (((0,708,74,741),(10,708)),((74,708,151,741),(111,708))):
        shoe=img.crop(rect).resize(((rect[2]-rect[0])*scale,33*scale),Image.Resampling.LANCZOS)
        body.alpha_composite(shoe,(to[0]*scale,to[1]*scale))
    head=img.crop((0,0,276,220)).resize((276*scale,220*scale),Image.Resampling.LANCZOS)
    body.alpha_composite(head,(64*scale,0))
    body=body.resize((410,741),Image.Resampling.LANCZOS)
    folder.mkdir(parents=True,exist_ok=True)
    body.save(folder/'corps.png')

    cfg=deepcopy(yaml.safe_load((source/'personnage.yaml').read_text()))
    cfg['nom']='Léa · costume et gabarit du 008'
    cfg['couches'][0]['pivot']=[205,740]
    for eye in cfg['visage']['yeux']:
        eye[0]+=64
        eye[2]+=64
    mouth=cfg['visage']['bouche']
    mouth['zone'][0]+=64
    mouth['zone'][2]+=64
    mouth['centre'][0]+=64
    (folder/'personnage.yaml').write_text(yaml.safe_dump(cfg,allow_unicode=True,sort_keys=False))
