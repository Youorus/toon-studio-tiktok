"""Contrôles locaux reproductibles du MP4 livré ; aucun appel à un fournisseur."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'out'
MOVIE=OUT/'La-sortie-est-bloquee-Le-Corps-Parle.mp4'

def main():
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(MOVIE)]))
    montage=json.loads((OUT/'montage.json').read_text())
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert (video['width'],video['height'],video['r_frame_rate'])==(1080,1920,'30/1')
    assert audio['channels']==2 and audio['sample_rate']=='48000'
    assert abs(float(probe['format']['duration'])-montage['duree'])<1/30
    subprocess.run(['ffmpeg','-nostdin','-v','error','-xerror','-i',str(MOVIE),'-f','null','-'],check=True)
    times=[0,2.04,4.36,8.78,16.6,22.19,22.76,22.80,23.45,24.9,25.16,30.60,30.63,39.6,45.80,46.23]
    board=Image.new('RGB',(1080,2024),'#E75261');d=ImageDraw.Draw(board)
    for i,t in enumerate(times):
        path=OUT/f'qa-{i:02d}.png'
        subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-ss',str(t),'-i',str(MOVIE),'-frames:v','1','-vf','scale=270:480',str(path)],check=True)
        im=Image.open(path);x=i%4*270;y=i//4*506;board.paste(im,(x,y))
        d.text((x+5,y+484),f'{t:.2f} s',fill='#FFF9ED')
    board.save(OUT/'controle-livraison.jpg',quality=93)
    report={'source':'MP4 final réellement décodé','sha256_master':sha256(MOVIE.read_bytes()).hexdigest(),
            'stream_probe':probe,'frames_extracted_seconds':times,'profile':'lcp-1.2.0',
            'full_decode_passed':True,'new_recraft_generations':0,
            'note':'Ouvrir la planche et revoir les gestes. Les mesures ne remplacent pas une revue du jeu et du son.'}
    (OUT/'controle-livraison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('Décodage complet réussi · 16 repères du master final · '+report['sha256_master'],flush=True)

if __name__=='__main__':main()
