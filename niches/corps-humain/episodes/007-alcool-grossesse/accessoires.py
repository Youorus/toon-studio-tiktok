"""Accessoires dessinés en calques et pantomime d'ouverture."""
from math import sin, tau

from PIL import Image, ImageDraw

from toonstudio.drawing import affine_paste, clamp, ease_in_out

INK='#6D383B'
TISSUE='#EB8887'
CREAM='#FFF9ED'


def prepare_props(folder):
    glass=Image.new('RGBA',(100,154))
    d=ImageDraw.Draw(glass)
    d.ellipse((22,132,77,146),fill='#FFE1D8',outline=INK,width=4)
    d.rounded_rectangle((45,70,54,140),radius=3,fill='#FFE1D8',outline=INK,width=3)
    d.rounded_rectangle((16,12,84,85),radius=26,fill='#FFE2D8',outline=INK,width=5)
    d.rounded_rectangle((21,39,79,81),radius=18,fill='#9F354A')
    d.ellipse((22,34,78,45),fill='#BD5262')
    d.ellipse((17,11,83,24),fill='#FFD2C9',outline=INK,width=4)
    d.line((27,27,31,56),fill=CREAM,width=5)
    glass.save(folder/'verre.png')

    bottle=Image.new('RGBA',(100,192))
    d=ImageDraw.Draw(bottle)
    d.rounded_rectangle((21,55,79,184),radius=20,fill='#395953',outline=INK,width=5)
    d.rounded_rectangle((38,16,62,76),radius=8,fill='#395953',outline=INK,width=5)
    d.rounded_rectangle((37,9,63,24),radius=4,fill='#AD4E59',outline=INK,width=3)
    d.rounded_rectangle((27,98,73,145),radius=5,fill='#F4CDB3',outline=INK,width=3)
    d.ellipse((43,111,57,124),fill='#B65F63')
    d.line((34,76,34,93),fill='#81A097',width=4)
    bottle.save(folder/'bouteille.png')


def pantomime(layer,t,face,glass,bottle):
    # Dès la première image, le verre est levé. Le poignet plie puis revient en place.
    fx,fy=face
    drink=ease_in_out(clamp((t+.12)/.38))*(1-ease_in_out(clamp((t-.50)/.48)))
    lower=ease_in_out(clamp((t-2.62)/.67))
    rx=fx-205+132*drink-24*lower
    ry=fy+143+5*sin(t*tau*.65)+46*lower-28*drink
    bx,by=fx+244+28*lower,fy+149+5*sin(t*tau*.57)+38*lower
    draw=ImageDraw.Draw(layer)

    def arm(points):
        draw.line(points,fill=INK,width=24,joint='curve')
        draw.line(points,fill=TISSUE,width=15,joint='curve')
        for x,y in points[:1]:
            draw.ellipse((x-8,y-8,x+8,y+8),fill=TISSUE)

    arm(((fx-142,fy+42),(fx-188,fy+96),(rx+7,ry+5)))
    arm(((fx+152,fy+40),(fx+214,fy+80),(bx-12,by+12)))
    affine_paste(layer,glass,(49,109),(rx,ry),angle=7+41*drink-12*lower)
    affine_paste(layer,bottle,(51,129),(bx,by),angle=12+6*drink+13*lower,sx=.88,sy=.88)

    for x,y in ((rx+6,ry+6),(bx-10,by+9)):
        draw.ellipse((x-14,y-10,x+14,y+10),fill=TISSUE,outline=INK,width=4)
        draw.arc((x-9,y-5,x+7,y+7),4,110,fill=INK,width=2)
