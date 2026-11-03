"""Adaptation française, ordre et intentions des répliques de la référence."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

from toonstudio import voice

HERE = Path(__file__).resolve().parent
NICHE = HERE.parents[1]
BASE = yaml.safe_load((NICHE/'production/modele-episode/episode.yaml').read_text())['voix']
VOICES = {**BASE, 'policier': {'voix':'pere','stabilite':.33},
          'intestin': {'voix':'boloss','stabilite':.34}}
SCENES = {
    'estomac': (
        ('estomac', 'Hein ? | C’est quoi, ça, encore ?', 'startled, suspicious, sharp', 'choque', .13),
        ('gelule', 'Un antibiotique.', 'matter-of-fact, quick', 'neutre', .14),
        ('estomac', 'Un antibiotique ? Pour quoi faire ? | Léa a juste un petit mal de tête. | Qui prend un antibio | pour un mal de crâne ?', 'incredulous, annoyed, rising emphasis', 'fache', .16),
        ('intestin', 'Elle doit savoir | ce qu’elle fait.', 'relaxed, deadpan', 'neutre', .09),
        ('estomac', 'Ah bah non.', 'dry, instant reply', 'fatigue', .20),
        ('intestin', 'Bon, arrête de discuter. | On le fait passer, | ce médicament ?', 'impatient, snappy, playful', 'fache', .10),
        ('estomac', 'Ouais, ouais. | Direction l’intestin grêle. | Allez, circule !', 'resigned, brisk, dismissive', 'malicieux', .45),
    ),
    'intrusion': (
        ('policier', 'Hé, stop ! | Qui t’a laissée entrer ?', 'sharply, commanding, then incredulous', 'fache', .16),
        ('violette', 'Du calme, mon gars. | La brèche était ouverte. | Tu voulais que je sonne ?', 'casual, teasing, amused', 'malicieux', .14),
        ('violette', 'Et t’es qui pour me dire | ce que je dois faire ? | Pousse-toi !', 'dismissive, suddenly forceful', 'fache', .44),
        ('policier', 'Allô ? On est mal. | Y a une brèche | dans la peau du pied.', 'breathless, shaken, speaking into radio', 'inquiet', .20),
        ('policier', 'Les bactéries sont déjà là. | Envoyez un globule blanc. | Et vite !', 'urgent, clipped, raising voice at the end', 'choque', .51),
    ),
    'duel': (
        ('globule', 'Hé ! Comment t’as fait | pour entrer et mettre | autant de bazar ?', 'aggressive, energetic, pointed', 'fache', .17),
        ('violette', 'Du bazar ? Ah ouais ? | Attends, j’vais te montrer | ce que c’est.', 'cocky, taunting, building', 'malicieux', .18),
        ('globule', 'Vas-y, viens !', 'defiant, sharp', 'fache', .78),
    ),
    'renfort': (
        ('policier', 'Allô ? Ça empire. | Elles se multiplient à toute vitesse !', 'urgent, breathless, over the radio', 'choque', .13),
        ('policier', 'Le globule n’arrive plus | à les contenir. | Il nous faut du renfort !', 'strained, emphatic', 'inquiet', .48),
    ),
    'prescription': (
        ('estomac', 'Hein ? Encore une ?', 'incredulous, quick', 'choque', .13),
        ('gelule', 'Cette fois, | j’ai une ordonnance.', 'confident, clipped', 'content', .43),
    ),
    'resistance': (
        ('gelule', 'Toi, l’intruse ! | T’es tombée sur la mauvaise gélule !', 'bold, theatrical, threatening', 'fache', .34),
        ('violette', 'Hein ? Tu crois vraiment | que ça marche encore sur moi ?', 'mocking, unhurried, skeptical', 'malicieux', .18),
        ('violette', 'Les vertes ont disparu. | Moi, je résiste à cet antibiotique. | Tu peux toujours essayer.', 'smug, confident, lightly amused', 'content', .48),
    ),
    'cabinet': (
        ('lea', 'Docteure, y a un autre moyen | de soigner ça ? | Mon pied empire de jour en jour.', 'worried, conversational, quietly frustrated', 'inquiet', .17),
        ('docteure', 'Une piste, c’est la résistance | aux antibiotiques. | Certaines bactéries survivent | à cet antibiotique.', 'calm, direct, warm', 'neutre', .22),
        ('docteure', 'En prendre pour rien | favorise les bactéries résistantes. | Et un antibiotique, | ça ne soigne pas | un simple mal de tête.', 'clear, gently emphatic', 'content', .22),
        ('docteure', 'On va vérifier | ce qui cause ton infection | et choisir le traitement adapté.', 'reassuring, matter-of-fact', 'neutre', .32),
        ('docteure', 'Abonne-toi pour comprendre | ton corps en t’amusant.', 'warm smile, direct to camera', 'content', .55),
    ),
}


def lines(scene):
    out = []
    for actor, groups, tag, emotion, pause in SCENES[scene]:
        text = ' '.join(part.strip() for part in groups.split('|'))
        out.append(dict(qui=actor, dit=text, jeu=f'[{tag}] {text}', sous_titres=groups,
                        emotion=emotion, pause=pause))
    return out


if __name__ == '__main__':
    jobs = [line for scene in SCENES for line in lines(scene)]
    def record(line):
        spec = VOICES[line['qui']]
        take = voice.tts(spec['voix'], line['jeu'], spec['stabilite'])
        print(line['qui'], round(voice.duration(take['audio']), 2), flush=True)
    print(f'{len(jobs)} prises · {sum(len(line["dit"].split()) for line in jobs)} mots', flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(record, jobs))
