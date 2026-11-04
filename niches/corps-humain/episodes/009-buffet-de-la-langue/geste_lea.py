"""Un bras continu, composé derrière la table ; main pleine devant le nez."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from toonstudio.drawing import affine_paste, clamp
from toonstudio.episode import _h

INK = '#181313'
SHIRT = '#B86E57'
SKIN = '#BE936F'


def points(progress):
    """Poignet sur une courbe, coude obtenu par une articulation à deux segments."""
    u = clamp(progress)
    u = u*u*(3-2*u)
    a, b, c, d = (np.array(p, float) for p in
                  ((233, 438), (110, 418), (76, 250), (139, 160)))
    wrist = (1-u)**3*a + 3*(1-u)**2*u*b + 3*(1-u)*u*u*c + u**3*d
    shoulder = np.array((220., 249.))
    delta = wrist-shoulder
    distance = np.linalg.norm(delta)
    segment = 110.
    theta = math.atan2(-delta[0], delta[1]) - math.acos(np.clip(distance/(2*segment), -1, 1))
    elbow = shoulder + segment*np.array((-math.sin(theta), math.cos(theta)))
    return shoulder, elbow, wrist


@lru_cache(maxsize=64)
def native_arm(progress):
    scale = 3
    image = Image.new('RGBA', (276*scale, 741*scale))
    draw = ImageDraw.Draw(image)
    shoulder, elbow, wrist = points(progress)
    def xy(p): return tuple(round(float(v)*scale) for v in p)
    def ellipse(p, radius, fill):
        x, y = xy(p); r = radius*scale
        draw.ellipse((x-r,y-r,x+r,y+r), fill=fill)

    # Quatre doigts rapprochés, un pouce de côté : aucun trou ni anneau.
    hand = [(-11,3),(-14,-9),(-22,-20),(-21,-24),(-18,-25),(-10,-18),
            (-13,-33),(-11,-37),(-7,-37),(-3,-21),(-5,-37),(-2,-40),
            (2,-39),(4,-21),(5,-35),(9,-36),(12,-33),(11,-19),
            (15,-28),(19,-28),(21,-25),(17,-6),(11,4)]
    draw.polygon([xy(wrist+q) for q in hand], fill=SKIN)
    outline=[xy(wrist+q) for q in hand]
    draw.line(outline+[outline[0]],fill=INK,width=5,joint='curve')
    for a,b in (((-3,-21),(-2,-12)),((4,-21),(5,-11)),((11,-19),(10,-10))):
        draw.line((xy(wrist+a),xy(wrist+b)),fill=INK,width=3)

    # L'union des manches évite la jonction de deux tubes superposés au coude.
    path = [xy(p) for p in (shoulder, elbow, wrist)]
    for color,width in ((INK,37),(SHIRT,33)):
        draw.line(path, fill=color, width=width*scale, joint='curve')
        for p in (shoulder,elbow,wrist): ellipse(p,width/2,color)
    # Raccord à l'épaule et petit bord de manche, sans masquer les doigts.
    ellipse(shoulder,15.5,SHIRT)
    direction=(wrist-elbow)/np.linalg.norm(wrist-elbow)
    across=np.array((-direction[1],direction[0]))
    for offset in (-7.,-1.):
        center=wrist+direction*offset
        draw.line((xy(center-across*15),xy(center+across*15)),fill=INK,width=4)
    return image.resize((276,741),Image.Resampling.LANCZOS)


def draw(layer, spec, t, progress, talk):
    """Même pivot, respiration et inclinaison que le corps de Léa."""
    phase=_h('lea')%7
    softness=.08
    sy=1+.003*math.sin(t*2*math.pi/3.2+phase)+softness*.035*talk*abs(math.sin(t*11))
    sx=1-softness*.02*talk*abs(math.sin(t*11))
    angle=softness*2*math.sin(t*2*math.pi*.9+phase)
    affine_paste(layer,native_arm(progress),(138,740),(spec['x'],spec['y']),
                 angle,spec['echelle']*sx,spec['echelle']*sy)
