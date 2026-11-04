"""Répliques françaises et prises de l'épisode 008."""
from concurrent.futures import ThreadPoolExecutor

from toonstudio import voice

VOICES={
    'estomac':{'voix':'blase','stabilite':.38},
    'cerveau':{'voix':'chef','stabilite':.40},
    'lea':{'voix':'patiente','stabilite':.45},
    'docteure':{'voix':'mere','stabilite':.48},
}
SCENES={
    'arrivage':[
        ('estomac','Un burger ? | Ça, c’est dans mes cordes. | Allez, on attaque !','delighted, picking up pace, playful','content',.20),
        ('estomac','Attends… | Encore un ? | Et les frites qui débarquent derrière ?', 'surprised, quick, getting suspicious','choque',.19),
        ('estomac','Oh ! Même le poulet ? | Léa, t’as commandé | pour toute la copro ou quoi ?', 'sharp, exasperated, comic emphasis','fache',.24),
        ('estomac','Un soda en plus ? | Léa, je suis un estomac, | pas la piscine municipale !', 'startled and sarcastic, hit the punchline', 'choque',.24),
        ('estomac','Ça monte, ça monte… | Je vois même plus mes couverts. | Bon. J’appelle le cerveau.', 'strained, breathless, decisive','inquiet',.48),
    ],
    'appel':[
        ('cerveau','Allô, ici le cerveau. | Tu peux parler ?', 'businesslike, dry, then curious','neutre',.13),
        ('estomac','J’peux encore parler. | Par contre, j’ai des frites jusqu’au cou !', 'frustrated, quick, emphatic','fache',.19),
        ('cerveau','Elle a déjà mangé tout ça ? | Je lui ai envoyé le signal, moi.', 'incredulous, worried, quick','inquiet',.19),
        ('estomac','Bah renvoie-le ! | Et mets « urgent » en objet.', 'snappy, with comic timing and a dry finish','fache',.45),
        ('cerveau','On fait une pause. | On l’écoute, ce ventre.', 'firm, settling, reassuring','neutre',.38),
    ],
    'cabinet':[
        ('lea','Docteure, quand je mange vite, | j’ai le ventre hyper lourd après. | Et j’ai du mal à m’arrêter.', 'natural, concerned, no shame','inquiet',.19),
        ('docteure','Un repas très copieux ou très gras | peut te laisser cette sensation de trop-plein.', 'clear, warm and conversational','neutre',.21),
        ('docteure','Essaie de manger plus lentement | et de faire une pause en cours de repas. | Si ça revient souvent, on en reparle.', 'kind, practical, direct','neutre',.23),
        ('docteure','Abonne-toi, | ton corps a encore des trucs à te dire.', 'warm, smiling, direct to camera','content',.42),
    ],
}


def lines(scene):
    return [
        {'qui':who,'dit':text.replace(' | ',' '),'sous_titres':text,
         'jeu':f"[{direction}] {text.replace(' | ',' ')}",'emotion':emotion,'pause':pause}
        for who,text,direction,emotion,pause in SCENES[scene]
    ]


if __name__=='__main__':
    def take(line):
        settings=VOICES[line['qui']]
        result=voice.tts(settings['voix'],line['jeu'],settings['stabilite'])
        print(line['qui'],result['audio'].name,flush=True)

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(take,[line for scene in SCENES for line in lines(scene)]))
