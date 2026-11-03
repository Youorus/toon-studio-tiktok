"""Prépare les cinq scènes et les prises dirigées du script court validé."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
import re
import sys
import wave

import numpy as np
import yaml

from toonstudio import voice

HERE = Path(__file__).resolve().parent
NICHE = HERE.parents[1]
OLD = HERE.parent / '006-antibioresistance'
SCRIPT = OLD / 'relecture' / 'script-006-tiktok-court-proposition.md'
STYLE = yaml.safe_load((NICHE / 'niche.yaml').read_text())['direction_artistique']
SPEAKERS = {'L’Estomac':'estomac', 'La Gélule':'gelule', 'La Peau':'peau', 'La Violette':'violette',
            'Le Globule blanc':'globule', 'Léa':'lea', 'La Docteure':'docteure'}
DIRECTION = (
    ('startled, quick, exasperated', 'choque', .21),
    ('snappy, annoyed, incredulous', 'fache', .16),
    ('dry, pointed', 'malicieux', .28),
    ('embarrassed, sheepish', 'gene', .61),
    ('startled, urgent', 'choque', .18),
    ('casual, playful', 'content', .21),
    ('irritated, clipped', 'fache', .17),
    ('teasing, excited', 'malicieux', .59),
    ('incredulous, deadpan', 'fatigue', .28),
    ('confident, quick, cheeky', 'content', .53),
    ('relieved, bright', 'content', .23),
    ('smug, amused', 'malicieux', .27),
    ('startled, confused', 'choque', .20),
    ('playful, building excitement', 'content', 1.05),
    ('worried, conversational', 'inquiet', .26),
    ('warm, clear, conversational', 'neutre', .27),
    ('curious, natural', 'inquiet', .24),
    ('warm, emphatic, lightly amused', 'content', .31),
    ('friendly, smiling', 'content', .62),
)
CAPTIONS = (
    "Oh non, pas elle ! | Léa a ressorti | ses vieux antibios !",
    "Calme-toi ! | J’ai une tête d’antidouleur ?",
    "Elle a mal au crâne. | T’as une ordonnance ?",
    "Non… | Hé hé hé !",
    "Aïe ! | Léa s’est râpé le genou ! | J’ai une brèche !",
    "J’ai vu de la lumière. | Je me suis permis !",
    "Tu ressors ! | Y a plus de place !",
    "Trop tard, ma belle ! | On va faire la fête !",
    "Encore toi ?!",
    "Eh ouais ! | Cette fois, j’ai une ordonnance. | C’est pour son infection !",
    "Ah ! Les vertes disparaissent ! | On va enfin souffler !",
    "Moi, cet antibiotique | me fait rien ! Ha ha !",
    "Attends… | T’étais déjà là ?!",
    "Depuis le début, mon pote ! | Et maintenant… | J’appelle toute la famille !",
    "Docteure, j’ai pris mes antibiotiques. | Pourquoi j’ai toujours | mon infection ?",
    "Des bactéries peuvent résister | à cet antibiotique. | Elles peuvent survivre | et se multiplier. | On va vérifier | ce qui cause ton infection | et adapter le traitement | si besoin.",
    "Et en prendre pour rien, | ça aggrave le problème ?",
    "Oui, ça favorise | les bactéries résistantes. | Et un antibiotique, | ça soigne pas | un mal de tête !",
    "Abonne-toi pour comprendre | ton corps en t’amusant.",
)


def actor(name, x, y, scale=1, **kwargs):
    path = 'personnages/' + name
    if not name.endswith('-aplats'):
        path = f'episodes/{OLD.name}/{path}'
    return dict(perso=path, x=x, y=y, echelle=scale, **kwargs)


def plan(name, decor, organ, actors, lines, zoom=(1, 1)):
    shot = dict(id=name, decor=f'decors/{decor}.png', transition='coupe', zoom=list(zoom), acteurs=actors, repliques=lines)
    if organ:
        shot['organe'] = organ
    return shot


def read_script():
    entries = re.findall(r'^\*\*([^*]+)\*\*[^\n]*? — (.+)$', SCRIPT.read_text(), re.M)
    assert len(entries) == len(DIRECTION) == len(CAPTIONS)
    assert all(text == ' '.join(group.strip() for group in subtitles.split('|'))
               for (_, text), subtitles in zip(entries, CAPTIONS))
    return [
        dict(qui=SPEAKERS[name], dit=text, sous_titres=subtitles,
             jeu=f'[{cue}] {text}', emotion=emotion, pause=pause)
        for (name, text), (cue, emotion, pause), subtitles in zip(entries, DIRECTION, CAPTIONS)
    ]


def build():
    template = yaml.safe_load((NICHE/'production/modele-episode/episode.yaml').read_text())
    voices = template['voix']
    for name in ('lea', 'docteure'):
        voices[name]['voix'] = STYLE['casting'][name]['voix']
    l = read_script()
    l[0]['reactions'] = {'gelule': 'inquiet'}
    l[1]['reactions'] = {'estomac': 'gene'}
    l[2]['reactions'] = {'gelule': 'gene'}
    l[3]['reactions'] = {'estomac': 'fatigue'}
    l[4]['reactions'] = {'violette': 'content'}
    l[5]['reactions'] = {'peau': 'fache'}
    l[6]['reactions'] = {'violette': 'malicieux'}
    l[7]['reactions'] = {'peau': 'choque'}
    l[9]['reactions'] = {'estomac': 'malicieux'}
    l[10]['reactions'] = {'violette': 'malicieux'}
    l[11]['reactions'] = {'globule': 'choque'}
    l[12]['reactions'] = {'violette': 'malicieux'}
    l[13]['reactions'] = {'globule': 'inquiet'}
    l[14]['reactions'] = {'docteure': 'inquiet'}
    l[15]['reactions'] = {'lea': 'neutre'}
    l[17]['reactions'] = {'lea': 'gene'}
    l[18].update(regards={'docteure': [0, 0]}, carte=STYLE['abonnement_final'])
    for line in l[14:]:
        line['regards'] = {'lea': [-.85, -.5], 'docteure': [.8, .5], **line.get('regards', {})}

    stomach = {'estomac': actor('estomac', 821, 811, regard=[-.85, .12]),
               'gelule': actor('gelule', 681, 1014, 1.08, regard=[.8, -.25])}
    skin = {'peau': actor('peau', 226, 657, regard=[.85, .22]),
            'violette': actor('resistante', 570, 817, 1.01, regard=[-.8, 0]),
            'verte1': actor('bacterie', 738, 799, .80),
            'verte2': actor('bacterie', 811, 957, .71),
            'verte3': actor('bacterie', 491, 1027, .70)}
    aftermath = {'globule': actor('globule', 270, 858, 1.03, regard=[.85, 0]),
                 'violette': actor('resistante', 665, 797, 1.08, regard=[-.8, 0]),
                 'verte1': actor('bacterie', 510, 617, .78),
                 'verte2': actor('bacterie', 833, 666, .72),
                 'verte3': actor('bacterie', 467, 993, .72),
                 'clone1': actor('resistante', 812, 599, .65),
                 'clone2': actor('resistante', 830, 944, .64),
                 'clone3': actor('resistante', 549, 1034, .57)}
    clinic = {'lea': actor(STYLE['casting']['lea']['rig'], 713, 1645, 1.04, regard=[-.85, -.5]),
              'docteure': actor(STYLE['casting']['docteure']['rig'], 328, 1645, 1.08, regard=[.8, .5])}
    sfx = deepcopy(template['bruitages'])
    sfx['plouf'] = {'fichier':'sons/plouf.wav', 'volume': .67}
    sfx['alerte'] = {'fichier':f'episodes/{OLD.name}/sons/alerte.wav', 'volume': .27}
    return dict(titre='La bactérie qui n’a pas bougé', niche='corps-humain', degrade_bas=False, voix=voices,
                bruitages=sfx, plans=[
        plan('ouverture','estomac-corail','Estomac',stomach,l[:4],(1,1.015)),
        plan('breche','peau-corail','Peau',skin,l[4:8]),
        plan('ordonnance','estomac-corail','Estomac',deepcopy(stomach),l[8:10],(1,1.02)),
        plan('survivante','peau-corail','Peau',aftermath,l[10:14]),
        plan('cabinet','cabinet-abonne-toi',None,clinic,l[14:],(1,1.018)),
    ])


def make_plouf():
    rate = 48000
    t = np.arange(round(rate * .49)) / rate
    rng = np.random.default_rng(166)
    noise = np.convolve(rng.normal(0, 1, t.size), np.ones(12) / 12, mode='same')
    phase = 2 * np.pi * (66 * t + 105 * (1 - np.exp(-9 * t)) / 9)
    env = np.minimum(1, 110 * t) * np.exp(-12 * t)
    drops = sum(np.sin(2 * np.pi * hz * t) * np.exp(-((t - time) / .012) ** 2)
                for hz, time in ((410,.075),(575,.112),(319,.162)))
    sample = (.49 * np.sin(phase) + .29 * noise) * env + .065 * drops
    dest = HERE/'sons'/'plouf.wav'
    dest.parent.mkdir(exist_ok=True)
    with wave.open(str(dest), 'wb') as wav:
        wav.setparams((1,2,rate,0,'NONE','not compressed'))
        wav.writeframes((sample * 32767).clip(-32768,32767).astype('<i2').tobytes())


def record(config):
    jobs = [l for s in config['plans'] for l in s['repliques']]
    def take(line):
        settings = config['voix'][line['qui']]
        clip = voice.tts(settings['voix'], line['jeu'], settings['stabilite'])
        print(line['qui'], f"{voice.duration(clip['audio']):.2f} s", flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(take, jobs))


if __name__ == '__main__':
    cfg = build()
    (HERE/'episode.yaml').write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False, width=104))
    make_plouf()
    if '--voix' in sys.argv:
        record(cfg)
