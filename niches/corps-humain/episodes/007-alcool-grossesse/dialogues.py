"""Texte français original et direction des prises de l'épisode 007."""
from toonstudio import voice

VOICES = {
    'uterus': {'voix':'diva','stabilite':.38},
    'placenta': {'voix':'blase','stabilite':.35},
    'foetus': {'voix':'ado_garcon','stabilite':.32},
    'lea': {'voix':'patiente','stabilite':.45},
    'docteure': {'voix':'mere','stabilite':.48},
}
SCENES = {
    'passage': [
        ('uterus','Euh… Placenta ? | Pourquoi ça sent l’apéro ici ?', 'startled, then dry disbelief', 'choque', .13),
        ('placenta','De l’alcool. | Il est passé du sang de Léa | jusqu’ici.', 'deadpan, clipped and clear', 'fatigue', .16),
        ('foetus','Un colis pour moi ? | J’ai rien commandé, hein !', 'snappy, offended, humorous', 'choque', .13),
        ('uterus','Bah refuse le colis !', 'impatient and punchy', 'fache', .11),
        ('placenta','Je suis un placenta, | pas un videur de boîte.', 'deadpan, punch the last phrase', 'fatigue', .55),
    ],
    'cabinet': [
        ('lea','J’ai bu avant de savoir | que j’étais enceinte. | Qu’est-ce que je fais ?', 'natural, quietly worried', 'inquiet', .19),
        ('docteure','Parles-en à ta sage-femme | ou à ton médecin. | Vous pourrez faire le point ensemble.', 'warm, calm, conversational', 'neutre', .19),
        ('docteure','L’alcool traverse le placenta. | On ne connaît pas de dose sans risque. | Pendant la grossesse, | c’est zéro alcool.', 'clear and reassuring, emphasize zero', 'neutre', .23),
        ('docteure','Abonne-toi, | ton corps a encore des trucs à te dire.', 'smiling and brisk, direct to camera', 'content', .45),
    ],
}

def lines(ident):
    return [
        {'qui':who,'dit':text.replace(' | ',' '),'sous_titres':text,'jeu':f"[{direction}] {text.replace(' | ',' ')}",
         'emotion':emotion,'pause':pause}
        for who,text,direction,emotion,pause in SCENES[ident]
    ]

if __name__ == '__main__':
    from concurrent.futures import ThreadPoolExecutor

    def take(line):
        settings=VOICES[line['qui']]
        result=voice.tts(settings['voix'],line['jeu'],settings['stabilite'])
        print(line['qui'],result['audio'].name,flush=True)

    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(take,[line for ident in SCENES for line in lines(ident)]))
