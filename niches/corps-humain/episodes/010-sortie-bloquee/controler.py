"""Contrôles locaux reproductibles du MP4 livré ; aucun appel à un fournisseur."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'out'
MOVIE=OUT/'La-sortie-est-bloquee-Le-Corps-Parle-V2.mp4'

def main():
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(MOVIE)]))
    montage=json.loads((OUT/'montage.json').read_text())
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert (video['width'],video['height'],video['r_frame_rate'])==(1080,1920,'30/1')
    assert audio['channels']==2 and audio['sample_rate']=='48000'
    assert abs(float(probe['format']['duration'])-montage['duree'])<1/30
    subprocess.run(['ffmpeg','-nostdin','-v','error','-xerror','-i',str(MOVIE),'-f','null','-'],check=True)
    times=[0,.4,2.35,4.40,8.82,9.35,19.60,20.15,23.23,23.70,24.45,25.75,26.46,27.60,28.47,31.95,32.66,41.94,47.80,48.20]
    board=Image.new('RGB',(1080,2530),'#E75261');d=ImageDraw.Draw(board)
    for i,t in enumerate(times):
        path=OUT/f'qa-{i:02d}.png'
        subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-ss',str(t),'-i',str(MOVIE),'-frames:v','1','-vf','scale=270:480',str(path)],check=True)
        im=Image.open(path);x=i%4*270;y=i//4*506;board.paste(im,(x,y))
        d.text((x+5,y+484),f'{t:.2f} s',fill='#FFF9ED')
    board.save(OUT/'controle-livraison.jpg',quality=93)
    report={'source':'MP4 final réellement décodé','sha256_master':sha256(MOVIE.read_bytes()).hexdigest(),
            'stream_probe':probe,'frames_extracted_seconds':times,'profile':'lcp-1.2.0',
            'full_decode_passed':True,'revision':'V2','new_recraft_generations':6,
            'note':'Ouvrir la planche et revoir les gestes. Les mesures ne remplacent pas une revue du jeu et du son.'}
    (OUT/'controle-livraison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('Décodage complet réussi · 20 repères du master V2 · '+report['sha256_master'],flush=True)

if __name__=='__main__':main()
