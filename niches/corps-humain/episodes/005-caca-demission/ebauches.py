"""Storyboard, modèles et animatique des gags. À exécuter depuis Toon Studio."""
from pathlib import Path
import math
import subprocess
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw
import yaml

from toonstudio.drawing import cover, ease_in_out, font, remove_flat_background
from toonstudio.rig import load as load_character

ROOT = Path(__file__).parent
ART = ROOT / 'art'
OUT = ROOT / 'out'
OLD = ROOT.parent / '004-le-spermogramme'
W, H, FPS = 540, 960, 24
INK, CREAM, TEAL = '#2E202A', '#FFF4DA', '#23656D'
DURATION = 21.5


def image(path):
    with Image.open(path) as src:
        return src.convert('RGBA')


def sprite(name, width, height, source=ART):
    original = remove_flat_background(image(source / f'{name}.png'), tol=24)
    original.thumbnail((width, height), Image.Resampling.LANCZOS)
    return original


def previous_sprite(character):
    img, _ = character.render(emo='content')
    img.thumbnail((232, 340), Image.Resampling.LANCZOS)
    return img


def draw_text(d, xy, text, size=26, fill=INK, anchor='mm', outline=0):
    f = font('Fredoka', size)
    try:
        f.set_variation_by_name('SemiBold')
    except (ValueError, OSError):
        pass
    d.multiline_text(xy, text, fill=fill, font=f, anchor=anchor, align='center',
                     stroke_width=outline, stroke_fill=INK, spacing=3)


def line(d, points, color=INK, width=5):
    d.line(points, fill=color, width=width, joint='curve')
    r = width / 2
    for x, y in (points[0], points[-1]):
        d.ellipse((x-r, y-r, x+r, y+r), fill=color)


def place(frame, layer, x, y, angle=0):
    if angle:
        layer = layer.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    frame.alpha_composite(layer, (round(x - layer.width / 2), round(y - layer.height / 2)))


def paper(label, sub=''):
    p = Image.new('RGBA', (205, 122))
    d = ImageDraw.Draw(p)
    d.rounded_rectangle((3, 3, 200, 117), radius=12, fill='#FFF4DC', outline=INK, width=5)
    draw_text(d, (102, 42), label, 28)
    if sub:
        draw_text(d, (102, 82), sub, 19, '#9A4650')
    return p


class Boards:
    def __init__(self):
        self.colon = cover(image(ART / 'colon.png'), W, H)
        self.organic = sprite('caca-b', 140, 205)
        self.swirl = sprite('caca', 160, 170)
        previous = yaml.safe_load((OLD / 'episode.yaml').read_text())
        self.cabinet_shot = next(shot for shot in previous['plans'] if shot['id'] == 'la-question')
        self.cabinet = cover(image(OLD / self.cabinet_shot['decor']))
        self.cabinet_caption_y = round(previous['legendes_y'] * H / self.cabinet.height)
        self.cabinet_chars = {
            name: load_character(OLD / spec['perso'])
            for name, spec in self.cabinet_shot['acteurs'].items()
        }
        self.parcel = paper('LIVRAISON', 'RETARDÉE')
        self.tag = paper('PARPAING', '12 KG').resize((128, 76), Image.Resampling.LANCZOS)

    def colon_room(self, door_open=0):
        p = self.colon.copy()
        d = ImageDraw.Draw(p)
        d.ellipse((224, 698, 511, 754), fill='#A45152')
        d.rounded_rectangle((349, 425, 493, 718), radius=52, fill='#914752', outline=INK, width=6)
        d.rounded_rectangle((360, 436, 482, 713), radius=45, fill='#42303D', outline=INK, width=3)
        if door_open < 1:
            w = round(116 * (1 - door_open))
            d.rounded_rectangle((361, 439, 361 + max(w, 13), 709), radius=min(42, max(4,w//4)),
                                fill='#B9D9C2', outline=INK, width=4)
            if w > 50:
                d.rounded_rectangle((375, 477, 455, 529), radius=10, fill='#E2EACF', outline=TEAL, width=2)
                d.ellipse((454, 577, 465, 590), fill='#D68150', outline=INK, width=2)
        d.rounded_rectangle((353, 366, 490, 411), radius=15, fill='#235F64', outline=INK, width=4)
        draw_text(d, (421, 388), 'SORTIE', 27, '#FFF4DA')
        return p

    def colon_face(self, p, expression):
        d = ImageDraw.Draw(p)
        for x,y in ((112, 475), (150, 468)):
            d.ellipse((x-17,y-21,x+17,y+21), fill=CREAM, outline='#6C373E', width=3)
            d.ellipse((x+2,y-3,x+10,y+7), fill=INK)
            if expression != 'surpris':
                d.pieslice((x-16,y-20,x+16,y+21),180,360,fill='#EF927C',outline='#A95859',width=2)
        d.arc((111, 496, 157, 518), 10, 150, fill='#6C373E', width=4)

    def caca(self, p, x, y, *, mode='souple', eyes='neutre', glasses=0, valise=False, stubble=False,
             hands='repos', shake=0, seat=False, body='b', helmet=False, hammer=0):
        d = ImageDraw.Draw(p)
        y += shake
        body_h = 176 if mode == 'brique' else 194
        if seat:
            d.rounded_rectangle((x-65,y+25,x+68,y+108),radius=12,fill='#A7B9AA',outline=INK,width=4)
            d.rounded_rectangle((x-68,y+87,x+69,y+103),radius=5,fill='#DFB789',outline=INK,width=4)
            for dx in (-50,48):
                line(d,[(x+dx,y+101),(x+dx,y+140)],'#543239',6)
        if hands == 'haut':
            goals = [(x-104,y-89),(x+108,y-102)]
        elif hands == 'bordereau':
            goals = [(x-83,y+51),(x+66,y+9)]
        elif hands == 'croises':
            goals = [(x+22,y+34),(x-23,y+48)]
        else:
            goals = [(x-88,y+55),(x+88,y+47)]
        for side, (ex,ey) in zip((-1,1),goals):
            mid = (x+side*79,y+16 if hands=='haut' else y+54)
            line(d,[(x+side*28,y+20),mid,(ex,ey)],INK,8)
            d.ellipse((ex-10,ey-9,ex+10,ey+9),fill=CREAM,outline=INK,width=3)
        for side in (-1,1):
            foot_y=y+body_h//2+29
            line(d,[(x+side*29,y+54),(x+side*38,foot_y)],INK,7)
            d.rounded_rectangle((x+side*38-16,foot_y-4,x+side*38+17,foot_y+13),radius=8,
                                fill=CREAM,outline=INK,width=3)
        if mode == 'brique':
            d.polygon([(x-72,y-60),(x-42,y-84),(x+72,y-84),(x+55,y-60)],fill='#BE7961',outline=INK,width=4)
            d.polygon([(x+55,y-60),(x+72,y-84),(x+72,y+56),(x+55,y+79)],fill='#784047',outline=INK,width=4)
            d.rounded_rectangle((x-72,y-61,x+56,y+81),radius=7,fill='#AA654F',outline=INK,width=5)
            for xoff,yoff in [(-53,-31),(20,12),(-43,47),(27,58)]:
                line(d,[(x+xoff,y+yoff),(x+xoff+8,y+yoff+4),(x+xoff+15,y+yoff+2)],'#75404A',2)
        else:
            s = self.organic if body == 'b' else self.swirl
            place(p, s, x, y)
        d = ImageDraw.Draw(p)
        if hands == 'croises':
            line(d,[(x-48,y+24),(x-27,y+41),(x+20,y+30)],INK,6)
            line(d,[(x+46,y+19),(x+26,y+36),(x-21,y+39)],INK,6)
            for dx,dy in ((20,30),(-21,39)):
                d.ellipse((x+dx-7,y+dy-7,x+dx+7,y+dy+7),fill=CREAM,outline=INK,width=2)
        face_y = y-28 if body=='b' or mode=='brique' else y+5
        for i, dx in enumerate((-18,19)):
            ex=x+dx
            d.ellipse((ex-15,face_y-20,ex+15,face_y+17), fill=CREAM,outline=INK,width=3)
            px=ex+(5 if eyes!='choque' else 0)
            d.ellipse((px-4,face_y-4,px+4,face_y+6),fill=INK)
            if eyes=='fache':
                line(d,[(ex-13,face_y-23+(i*4)),(ex+12,face_y-18-(i*4))],INK,4)
        if eyes=='choque':
            d.ellipse((x-13,face_y+24,x+13,face_y+49),fill='#44232A',outline=INK,width=3)
        else:
            d.arc((x-18,face_y+18,x+16,face_y+37),0,180,fill=INK,width=4)
        if stubble:
            for dx,dy in ((-24,39),(-17,46),(-8,42),(0,46),(9,41),(16,46),(24,38)):
                d.ellipse((x+dx-1,face_y+dy-1,x+dx+2,face_y+dy+2),fill='#44232A')
        if glasses > 0:
            fy=face_y + 40*(1-glasses)
            gx=x+43*(1-glasses)
            for dx in (-19,19):
                d.rounded_rectangle((gx+dx-18,fy-17,gx+dx+18,fy+12),radius=7,fill='#1B2637',outline=INK,width=3)
                line(d,[(gx+dx-12,fy-10),(gx+dx-1,fy-10)],'#8DC8C7',2)
            line(d,[(gx-4,fy-4),(gx+5,fy-4)],INK,4)
        if valise:
            xx,yy=goals[1]
            d.rounded_rectangle((xx-35,yy+10,xx+30,yy+68),radius=8,fill='#558B87',outline=INK,width=4)
            d.arc((xx-15,yy,xx+11,yy+25),180,360,fill=INK,width=4)
            line(d,[(xx-18,yy+16),(xx-18,yy+62)],'#B2CCAD',3)
        if helmet:
            d.pieslice((x-54,y-108,x+56,y-26),180,360,fill='#F8C465',outline=INK,width=4)
            d.rounded_rectangle((x-59,y-70,x+65,y-60),radius=4,fill='#F8C465',outline=INK,width=3)
        if helmet:
            hx=x+99-45*hammer
            hy=y-8+31*hammer
            line(d,[(x+87,y+45),(hx,hy)],'#D5A979',8)
            d.rounded_rectangle((hx-19,hy-13,hx+17,hy+10),radius=5,fill='#8BA49E',outline=INK,width=3)

    def clinic(self, t, final=False, phone=False):
        p = self.cabinet.copy()
        emotions = {'lea': 'content' if phone or final else 'inquiet',
                    'docteure': 'malicieux' if final else 'content'}
        for index, (name, spec) in enumerate(self.cabinet_shot['acteurs'].items()):
            character = self.cabinet_chars[name]
            mirror = spec.get('miroir', False)
            gx, gy = (0, 0) if final and name == 'docteure' else spec['regard']
            blink = (t + 0.7 * index) % 3.5 < 0.10
            layer, (ax, ay) = character.render(emo=emotions[name], gaze=(-gx if mirror else gx, gy), blink=blink, t=t)
            if mirror:
                layer = layer.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                ax = layer.width - ax
            s = spec['echelle'] * character.scale
            layer = layer.resize((int(layer.width * s), int(layer.height * s)), Image.Resampling.LANCZOS)
            p.alpha_composite(layer, (int(spec['x'] - ax * s), int(spec['y'] - ay * s)))
        p = p.resize((W, H), Image.Resampling.LANCZOS)
        d = ImageDraw.Draw(p)
        if phone:
            p.alpha_composite(paper('PETIT POINT ?', 'Dans 2 min').resize((176,105)),(278,227))
        if final:
            d.rounded_rectangle((108,225,432,286),radius=23,fill=TEAL,outline=INK,width=3)
            draw_text(d,(270,254),'ABONNE-TOI',35,'#FFF4DA')
            draw_text(d,(270,313),'TON CORPS, EXPLIQUÉ',17,TEAL)
        return p

    def scene(self, t, captions=True):
        caption_y = 821
        if t>=18.6:
            p=self.clinic(t, final=True)
            words='« Abonne-toi… »'
            caption_y = self.cabinet_caption_y
        elif 15.8<=t<17.6:
            p=self.clinic(t, phone=True)
            words='« Non. Là, j’ai une\nurgence… en interne. »'
            caption_y = self.cabinet_caption_y
        elif 11.7<=t<14.2:
            p=self.clinic(t)
            words='« Quand tu te retiens souvent,\nl’envie peut passer. »'
            caption_y = self.cabinet_caption_y
        elif t>=17.6:
            q=t-17.6
            p=self.colon_room(door_open=min(0.94,q*2.1))
            self.colon_face(p,'surpris')
            self.caca(p,323,596,mode='brique',eyes='choque',hands='haut',
                      shake=-abs(math.sin(math.pi*2*q))*29)
            d=ImageDraw.Draw(p)
            for i in range(11):
                x=163+(i*43)%310
                y=437+(i*31)%94+(q*85)
                d.polygon([(x-4,y),(x,y-8),(x+4,y),(x,y+8)],fill='#F4CA73')
            words='« LIBÉREZ LE PRISONNIER ! »'
        elif t>=14.2:
            q=t-14.2
            p=self.colon_room()
            self.colon_face(p,'neutre')
            hit=max(0,math.sin(q*math.tau*1.85))
            self.caca(p,309,599,mode='brique',eyes='choque',helmet=True,hammer=hit)
            if hit>.84:
                draw_text(ImageDraw.Draw(p),(419,616),'TOC !',26,CREAM,outline=2)
            words='« JE SUIS DEVENU\nDU CARRELAGE, LÀ ! »'
        elif t>=8.15:
            q=t-8.15
            p=self.colon_room()
            self.colon_face(p,'neutre')
            hard=q>=0.88
            shake=0 if hard else -5*math.sin(q*12)
            self.caca(p,306+min(q,.88)*13,590,mode='brique' if hard else 'souple',
                      eyes='choque' if hard else 'fache',shake=shake)
            if 0.87<=q<=1.28:
                draw_text(ImageDraw.Draw(p),(435,644),'TOC !',42,CREAM,outline=4)
            if q>=1.55:
                place(p,self.tag,367,674,angle=-8)
            words='« Tu peux construire\nun pavillon avec mon cul ! »' if q>=1.55 else ''
        elif t>=5.5:
            q=t-5.5
            p=self.colon_room()
            self.colon_face(p,'neutre')
            self.caca(p,312,590,eyes='fache',hands='croises',seat=True,stubble=True)
            d=ImageDraw.Draw(p)
            if q < 0.78:
                draw_text(d,(270,260),'LE LENDEMAIN',24,CREAM,outline=3)
            if 1.05<=q<1.55:
                for x in (217,264,311,358,405):
                    d.rounded_rectangle((x,447,x+12,750),radius=6,fill='#71858C',outline=INK,width=3)
                d.rounded_rectangle((205,448,426,463),radius=4,fill='#778D92',outline=INK,width=3)
            if 0.78<=q<1.78:
                f=ease_in_out(min((q-.78)/.21, 1, (1.78-q)/.21))
                p=cover(p.crop((round(155*f), round(259*f), W, H-round(17*f))), W, H)
            words='« Vingt-quatre heures\nque j’suis en garde à vue ! »'
        else:
            p=self.colon_room()
            self.colon_face(p,'neutre')
            entry=min(1,t/0.85)
            x=276+38*ease_in_out(entry)
            self.caca(p,x,588,eyes='fache' if t>=2.5 else 'neutre',
                      glasses=max(0,1-(t-1.25)/1.12) if t>1.25 else 1,
                      valise=t<2.5,hands='bordereau' if t>=2.5 else 'repos',
                      shake=-math.sin(math.pi*entry)*12)
            if t>=2.5:
                q=ease_in_out(min(1,(t-2.5)/.48))
                piece=self.parcel.resize((round(205*max(.15,q)),round(122*max(.15,q))),Image.Resampling.LANCZOS)
                place(p,piece,325,673+28*(1-q),angle=-9)
                if q>0.75:
                    ImageDraw.Draw(p).ellipse((379, 610, 399, 628), fill=CREAM, outline=INK, width=3)
            words='« Bon allez, c’est bon,\nmoi j’me casse ! »' if t<2.5 else '« JE SUIS PAS UN COLIS\nAMAZON, MOI ! »'
        if captions and words:
            draw_text(ImageDraw.Draw(p),(270,caption_y),words,28,CREAM,outline=3)
        return p

    def storyboard(self):
        data=[
            (.85,'01  OUVERTURE','Le Caca part avec valise et lunettes.'),
            (3.85,'02  LE BORDEREAU','Il dégaine son avis de retard.'),
            (6.78,'03  GARDE À VUE','Les barreaux claquent pendant ½ s.'),
            (10.35,'04  LE PARPAING','TOC, silence, puis étiquette.'),
            (12.85,'05  AU CABINET','La docteure explique le risque.'),
            (15.10,'06  LE CARRELAGE','Insert éclair, deux coups de marteau.'),
            (18.13,'07  LA VICTOIRE','Une seconde de fanfare, coupée net.'),
            (20.02,'08  FIN AU CABINET','Sourire en coin et badge dans le plan.'),
        ]
        out=Image.new('RGB',(1200,1242),'#172B2D')
        d=ImageDraw.Draw(out)
        draw_text(d,(44,27),'MON CACA A POSÉ SA DÉMISSION',43,CREAM,anchor='lt')
        draw_text(d,(46,82),'ÉBAUCHE DE MISE EN SCÈNE  /  8 IMAGES CLÉS',21,'#9ECBC1',anchor='lt')
        for i,(t,title,note) in enumerate(data):
            x,y=45+(i%4)*282,133+(i//4)*538
            out.paste(self.scene(t).convert('RGB').resize((246,437),Image.Resampling.LANCZOS),(x,y))
            draw_text(d,(x,y+448),title,22,CREAM,anchor='lt')
            draw_text(d,(x,y+477),note,15,'#9ECBC1',anchor='lt')
        out.save(OUT/'storyboard.jpg',quality=92)

    def casting(self):
        out=Image.new('RGBA',(1160,1015),'#162A2C')
        d=ImageDraw.Draw(out)
        draw_text(d,(42,27),'CASTING  /  ÉBAUCHE',44,CREAM,anchor='lt')
        draw_text(d,(44,85),'Le casting et le cabinet de l’épisode 004.',23,'#A6CCC2',anchor='lt')
        for i,(role,name) in enumerate((('docteure','Docteure'),('lea','Léa'))):
            x=42+i*283
            asset=previous_sprite(self.cabinet_chars[role])
            d.rounded_rectangle((x,135,x+244,563),radius=18,fill='#C7D3C7')
            place(out,asset,x+122,348)
            d=ImageDraw.Draw(out)
            draw_text(d,(x+122,581),name,25,CREAM)
            draw_text(d,(x+122,612),'MODÈLE DE L’ÉPISODE 004',16,'#A6CCC2')
        reference=self.clinic(12.85).resize((242,430),Image.Resampling.LANCZOS)
        place(out,reference,853,349)
        draw_text(d,(853,581),'Cabinet',25,CREAM)
        draw_text(d,(853,612),'DÉCOR DE L’ÉPISODE 004',16,'#A6CCC2')
        for i,(body,title) in enumerate((('a','A  /  FORME TOURBILLON'),('b','B  /  FORME ORGANIQUE'))):
            p=Image.new('RGBA',(W,300),'#D47C79')
            self.caca(p,268,139,body=body,glasses=1,valise=True)
            place(out,p,310+i*540,815)
            draw_text(d,(310+i*540,986),title,21,CREAM)
        out.convert('RGB').save(OUT/'casting.jpg',quality=92)


def preview_audio(path):
    sr=48000
    samples=np.zeros(round(DURATION*sr))
    def tone(at,length,hz,volume,decay=1):
        n=round(length*sr)
        t=np.arange(n)/sr
        envelope=np.minimum(1,t*140)*(1-t/length)**decay
        samples[round(at*sr):round(at*sr)+n]+=volume*envelope*np.sin(2*math.pi*hz*t)
    def knock(at,volume):
        for hz,v in ((138,1),(219,.55),(713,.18)):
            tone(at,.19,hz,volume*v,6)
    tone(1.05,.13,720,.12,3)
    tone(1.16,.13,950,.09,3)
    tone(6.55,.15,250,.10,7)
    tone(6.56,.2,650,.07,7)
    knock(9.03,.29)
    knock(14.36,.20)
    knock(14.91,.18)
    tone(15.83,.15,622,.11,3)
    tone(15.96,.15,831,.10,3)
    for at,length,hz,decay in ((17.6,.21,392,.4),(17.81,.27,523.25,.4),(18.08,.52,659.25,0)):
        for h,v in ((1,.12),(2,.04),(3,.026)):
            tone(at,length,hz*h,v,decay)
    with wave.open(str(path),'wb') as audio:
        audio.setparams((1,2,sr,0,'NONE','not compressed'))
        audio.writeframes((np.clip(samples,-1,1)*32767).astype('<i2').tobytes())


def render(board):
    with tempfile.TemporaryDirectory() as temp:
        wav=Path(temp)/'maquette.wav'
        preview_audio(wav)
        args=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
              '-i',str(wav),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-ar','48000',
              '-movflags','+faststart',str(OUT/'animatique.mp4')]
        with subprocess.Popen(args,stdin=subprocess.PIPE) as proc:
            for i in range(round(DURATION*FPS)):
                proc.stdin.write(board.scene(i/FPS).convert('RGB').tobytes())
            proc.stdin.close()
            if proc.wait():
                raise RuntimeError('Export animatique interrompu')


if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    b=Boards()
    b.storyboard()
    b.casting()
    render(b)
