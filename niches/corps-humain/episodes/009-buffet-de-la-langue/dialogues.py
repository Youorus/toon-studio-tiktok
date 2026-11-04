"""Répliques françaises et intentions de l'épisode 009."""
from concurrent.futures import ThreadPoolExecutor

from toonstudio import voice

VOICES={
    'cerveau':{'voix':'chef','stabilite':.40},
    'verte':{'voix':'lascar','stabilite':.36},
    'rouge':{'voix':'ado_garcon','stabilite':.32},
    'ami':{'voix':'patient','stabilite':.40},
    'lea':{'voix':'patiente','stabilite':.45},
    'docteure':{'voix':'mere','stabilite':.48},
}
SCENES={
    'reveil':[
        ('cerveau','Ah ! Enfin réveillés ! | Allez, debout là-dedans !','waking up, stretching, then cheerful','content',.20),
    ],
    'buffet':[
        ('verte','Oh, les restes ! | Personne nous a passé la brosse ? | Les gars, c’est buffet à volonté !','gleeful, cheeky, fast but articulate','content',.18),
        ('rouge','Hé, tu m’en gardes un morceau ?', 'playful, asking quickly','inquiet',.15),
        ('verte','Sers-toi, mon pote ! | Ici, on ferme jamais !', 'boastful, amused, with a laugh','malicieux',.36),
    ],
    'petit-dejeuner':[
        ('ami','Ça va ? | T’as bien dormi ?', 'warm, casual, conversational','content',.15),
        ('lea','Oui… mais ton haleine, | elle a fait nuit blanche !', 'first gentle then teasing, holding nose','degoute',.44),
    ],
    'cabinet':[
        ('lea','Docteure, ça vient d’où, cette odeur ?', 'genuinely curious and natural','inquiet',.18),
        ('docteure','Souvent, des bactéries dans la bouche. | En dégradant des résidus, | elles libèrent des composés malodorants.', 'warm, clear, conversational','neutre',.18),
        ('docteure','On brosse dents et langue en douceur. | Si ça persiste, | parles-en à ton dentiste.', 'practical, kind and direct','content',.22),
        ('docteure','Abonne-toi, | ton corps a encore des trucs à te dire.', 'smiling, warm, direct to camera','content',.42),
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
        setting=VOICES[line['qui']]
        result=voice.tts(setting['voix'],line['jeu'],setting['stabilite'])
        print(line['qui'],result['audio'].name,flush=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(take,[line for scene in SCENES for line in lines(scene)]))
