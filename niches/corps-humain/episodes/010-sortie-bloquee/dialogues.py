"""Adaptation française de la référence du 2025-09-23, avec conclusion au cabinet."""
from concurrent.futures import ThreadPoolExecutor
from toonstudio import voice

VOICES = {
    'caca': {'voix': 'lascar', 'stabilite': .33},
    'policier': {'voix': 'pere', 'stabilite': .33},
    'lea': {'voix': 'patiente', 'stabilite': .43},
    'docteure': {'voix': 'mere', 'stabilite': .46},
}
SCENES = {
    'sortie': [
        ('caca', 'Hé ! Je dois sortir !', 'urgent, quick, calling to the guard', 'inquiet', .12),
        ('policier', 'C’est bon, vas-y. | La voie est libre.', 'brisk, casual authority, conversational', 'content', .12),
        ('caca', 'Je suis coincé ! | J’arrive plus à bouger ! | Au secours !', 'straining, increasingly panicked, comic, articulate', 'choque', .18),
        ('policier', 'Ah ouais… | T’es dur comme du béton ! | T’as attendu trop longtemps, toi.', 'effort then incredulous, dry teasing, quick', 'inquiet', .12),
        ('caca', 'J’ai séché sur place, chef !', 'indignant, breathless, a little whiny', 'fache', .16),
        ('policier', 'Bon. Alerte rouge ! | Faut qu’elle voie | qu’il y a un souci.', 'resigned, matter-of-fact, comic emphasis on rouge', 'inquiet', 1.35),
        ('policier', 'Allez… | Une dernière poussée !', 'straining, determined, rising energy', 'fache', .15),
    ],
    'passage': [('caca', 'Hooop là !', 'sudden relieved yelp, sliding down', 'choque', .60)],
    'cuvette': [('lea', 'Du sang ?!', 'sharply surprised, genuinely concerned, quick', 'choque', .55)],
    'toilettes': [
        ('lea', 'Et pourquoi c’est aussi dur ? | Ça fait mal quand ça sort… | Je vais consulter.', 'concerned, natural spoken French, brisk', 'inquiet', .18),
    ],
    'cabinet': [
        ('docteure', 'Un caca trop dur peut irriter | et faire saigner. | Le sang peut avoir plusieurs causes : | il faut consulter.', 'clear, caring, concise, conversational, stress consulter', 'neutre', .15),
        ('lea', 'Donc, on évite de se retenir ?', 'quick, genuinely asking', 'inquiet', .10),
        ('docteure', 'Oui. Sans forcer. | Eau, fibres et mouvement aident. | Abonne-toi : | ton corps a d’autres dossiers !', 'warm, brisk, practical, then a knowing smile', 'content', .40),
    ],
}

def lines(scene):
    return [{'qui': who, 'dit': text.replace(' | ', ' '), 'sous_titres': text,
             'jeu': f'[{direction}] '+text.replace(' | ', ' '), 'emotion': emotion, 'pause': pause}
            for who, text, direction, emotion, pause in SCENES[scene]]

if __name__ == '__main__':
    def take(line):
        setting = VOICES[line['qui']]
        result = voice.tts(setting['voix'], line['jeu'], setting['stabilite'])
        print(line['qui'], result['audio'].name, flush=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(take, [line for scene in SCENES for line in lines(scene)]))
