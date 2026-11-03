"""Prépare les calques Recraft et les accents sonores de l’épisode."""
from pathlib import Path
import wave

import numpy as np
from PIL import Image, ImageDraw
import yaml

from toonstudio.drawing import cover, font, remove_flat_background

ROOT = Path(__file__).parent
NICHE = ROOT.parents[1]


def art(name):
    return Image.open(ROOT/'art'/f'{name}.png').convert('RGBA')


def recolor_background(image, original, target, rows):
    """Retouche un aplat du décor en conservant ses variations et ses bords."""
    pixels = np.array(image)
    colors = pixels[rows, :, :3].astype(np.float32)
    distance = np.abs(colors - original).max(axis=2)
    weight = np.clip((22 - distance) / 15, 0, 1)[..., None]
    colors += weight * (np.array(target) - original)
    pixels[rows, :, :3] = np.clip(colors, 0, 255).round().astype(np.uint8)
    return Image.fromarray(pixels)


def prepare_backgrounds():
    stomach = recolor_background(cover(art('estomac')), (251, 220, 176), (232, 170, 186), slice(None))
    stomach.save(ROOT/'decors'/'estomac.png')

    skin = cover(art('plaie-b'))
    skin = recolor_background(skin, (251, 227, 200), (244, 203, 199), slice(0, 438))
    skin = recolor_background(skin, (250, 172, 131), (230, 164, 164), slice(1100, None))
    skin.save(ROOT/'decors'/'plaie.png')

    cabinet = Image.open(ROOT.parent/'004-le-spermogramme'/'decors'/'cabinet.png').convert('RGBA')
    # Le petit mot reste dans le premier cadre mural et suit le travelling du décor.
    sign = Image.new('RGBA', (140 * 3, 144 * 3))
    d = ImageDraw.Draw(sign)
    handwriting = font('Caveat', 120)
    handwriting.set_variation_by_name('Bold')
    d.multiline_text((210, 208), 'Abonne-\ntoi', font=handwriting, fill='#405854',
                     anchor='mm', align='center', spacing=-8)
    d.arc((158, 307, 270, 328), 8, 158, fill='#7F9A8A', width=5)
    cabinet.alpha_composite(sign.resize((140, 144), Image.Resampling.LANCZOS), (480, 521))
    cabinet.save(NICHE/'decors'/'cabinet-abonne-toi.png')


def install(name, img, eyes, eye_r, tone, softness=.3, talking=True):
    p=ROOT/'personnages'/name
    p.mkdir(exist_ok=True,parents=True)
    img.save(p/'corps.png')
    f={
        'nom':name,'type':'organe',
        'couches':[{'id':'corps','images':{'defaut':'corps.png'},'pivot':list(eyes)}],
        'visage': {'couche':'corps','yeux':list(eyes),'rayon_oeil':eye_r,'ecart':2.18,
                    'bouche':[eyes[0],eyes[1]+round(eye_r*1.95)] if talking else None,
                    'largeur_bouche':round(eye_r*1.85),'peau':tone,'forme_oeil':1.13,
                    'pupille':.69,'paupiere':.09,'trait':.085},
        'mouvement':{'souplesse':softness,'respiration':.005},
    }
    (p/'personnage.yaml').write_text(yaml.safe_dump(f,allow_unicode=True,sort_keys=False))


def model(name, max_size, x, y, r, tone, crop=None, tint=False, talking=True):
    i=art(name)
    if crop:
        i=i.crop(tuple(round(v*(i.width if idx%2==0 else i.height)) for idx,v in enumerate(crop)))
    i=remove_flat_background(i,tol=20)
    i.thumbnail(max_size,Image.Resampling.LANCZOS)
    if tint:
        a=np.array(i)
        m=(a[:,:,3]>170)&(a[:,:,:3].min(axis=2)>178)&(a[:,:,2]<250)
        a[m,:3]=(156,225,155)
        i=Image.fromarray(a)
    install(name,i,(round(i.width*x),round(i.height*y)),r,tone,talking=talking)


def sounds():
    p=ROOT/'sons'
    p.mkdir(exist_ok=True)
    sr=48000
    for name,length,start,end,amp in (
        ('ploc',.20,340,148,.24),
        ('alerte',.24,740,495,.13),
        ('passage',.63,310,760,.10),
    ):
        t=np.arange(round(sr*length))/sr
        phase=np.pi*2*(start*t+(end-start)*t*t/(2*length))
        env=np.minimum(t*77,1)*(1-t/length)**2.9
        audio=amp*env*(np.sin(phase)+.11*np.sin(1.86*phase))
        with wave.open(str(p/f'{name}.wav'),'wb') as f:
            f.setparams((1,2,sr,0,'NONE','not compressed'))
            f.writeframes((audio*32767).astype('<i2').tobytes())


def main():
    prepare_backgrounds()
    install('estomac',Image.new('RGBA',(205,206)),(102,85),30,'#ED7981',softness=0)
    install('peau',Image.new('RGBA',(196,180)),(98,72),25,'#EE9A8E',softness=0)
    model('gelule',(112,232),.49,.39,18,'#284D63',crop=(.302,.111,.592,.879))
    model('bacterie',(200,167),.52,.46,15,'#9CE19B',tint=True,talking=False)
    model('resistante',(176,222),.59,.49,21,'#B58BCE',crop=(.17,.13,.86,.81))
    model('globule',(196,189),.51,.47,23,'#F9F8E9')
    sounds()


if __name__=='__main__':
    main()
