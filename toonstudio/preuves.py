"""Produit deux planches de preuves à partir des vrais calques et du MP4 livré."""
from io import BytesIO
import json
from pathlib import Path
import subprocess
from textwrap import wrap

from PIL import Image, ImageDraw
import yaml

from .drawing import font

INK='#222735'
MUTED='#4A5567'
PAPER='#FBF6ED'
CORAL='#E75261'


def frame(master,time):
    raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(time),'-i',str(master),
                                 '-map','0:v:0','-frames:v','1','-c:v','png','-f','image2pipe','-'])
    return Image.open(BytesIO(raw)).convert('RGBA')


def caption(draw,text,at,size=28,color=INK):
    draw.text(at,text,font=font('Fredoka',size),fill=color)


def paste(image,source,box):
    x,y,w,h=box
    source=source.copy().convert('RGBA')
    source.thumbnail((w,h),Image.Resampling.LANCZOS)
    image.alpha_composite(source,(x+(w-source.width)//2,y+(h-source.height)//2))


def board(title,subtitle,checksum):
    img=Image.new('RGBA',(1280,1060),PAPER)
    draw=ImageDraw.Draw(img)
    draw.rectangle((0,0,1280,12),fill=CORAL)
    caption(draw,title,(60,48),48)
    caption(draw,subtitle,(60,115),28,MUTED)
    draw.line((60,174,1220,174),fill='#D9CAB9',width=2)
    caption(draw,'Le Corps Parle.fr · @lecorps.parle.fr',(60,1001),24)
    caption(draw,'SHA-256 du MP4 · '+checksum[:16],(774,1001),22,MUTED)
    return img,draw


def generate(folder,master,checksum,destination):
    config=yaml.safe_load((folder/'preuves.yaml').read_text())
    title=config['titre']
    takes=json.loads((folder/'out'/'montage.json').read_text())['repliques']
    samples=config['captures']
    images=[frame(master,sample['seconde']) for sample in samples]
    destination.mkdir(parents=True,exist_ok=True)

    img,draw=board(title,'01  ·  Calques du projet et image du master',checksum)
    draw.rounded_rectangle((60,210,676,934),radius=24,fill='#F1E6D8')
    draw.rounded_rectangle((708,210,1220,934),radius=24,fill='#E9DED2')
    for index,asset in enumerate(config['calques']):
        path=folder/asset['fichier']
        y=237+index*222
        paste(img,Image.open(path),(88,y,208,193))
        caption(draw,asset['nom'],(317,y+45),29)
        caption(draw,path.name,(317,y+91),22,MUTED)
    paste(img,images[0],(735,232,460,634))
    caption(draw,f"Master à {samples[0]['seconde']:.2f} s",(771,887),28)
    img.convert('RGB').save(destination/'01-calques-et-rendu.jpg',quality=91,optimize=True)

    img,draw=board(title,'02  ·  Images extraites du master et repères des prises',checksum)
    for index,(sample,still) in enumerate(zip(samples,images)):
        x=60+index*398
        draw.rounded_rectangle((x,206,x+364,930),radius=22,fill='#EFE4D9')
        paste(img,still,(x+12,226,340,476))
        caption(draw,f"{sample['seconde']:.2f} s · {sample['nom']}",(x+20,719),23)
        take=next((line for line in takes if line['t0']<=sample['seconde']<line['t1']),None)
        if take:
            caption(draw,f"Prise {take['qui']} · {take['t0']:.2f}–{take['t1']:.2f} s",(x+20,762),21,MUTED)
            for row,line in enumerate(wrap(take['dit'],width=31)[:4]):
                caption(draw,line,(x+20,803+row*23),19)
    img.convert('RGB').save(destination/'02-reperes-de-montage.jpg',quality=91,optimize=True)

    (destination/'texte-contestation.txt').write_text(
        f'Bonjour, je demande un réexamen de la décision sur « {title} », publiée par @lecorps.parle.fr. '
        f"{config['fabrication'].strip()} Les planches montrent les calques, les repères des prises et des images du master. "
        'Merci de réexaminer la publication.\n\n'
        'À compléter selon le formulaire\n'
        'Lien de la publication : [coller le lien]\n'
        'Motif affiché : [recopier la notification]\n'
        'Joindre 01-calques-et-rendu.jpg en premier si le formulaire accepte des images. '
        'Ajouter 02-reperes-de-montage.jpg si un deuxième emplacement est disponible.\n')
