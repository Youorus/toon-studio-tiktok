"""Plan de montage et texte français de l’épisode."""
from pathlib import Path
import yaml

ROOT = Path(__file__).parent
OUT = ROOT / 'episode.yaml'
STYLE = yaml.safe_load((ROOT.parents[1] / 'niche.yaml').read_text())['direction_artistique']


def replica(qui, cues, jeu, emotion='neutre', **other):
    text = ' '.join(piece.strip() for piece in cues.split('|'))
    other.setdefault('pause', .22)
    return dict(qui=qui, dit=text, sous_titres=cues, jeu=f'[{jeu}] {text}', emotion=emotion, **other)


def acteur(name, x, y, s, **other):
    return dict(perso='personnages/'+name, x=x, y=y, echelle=s, **other)


def plan(id, decor, actors, *lines):
    return dict(id=id, decor='decors/'+decor+'.png', transition='coupe', zoom=[1,1], acteurs=actors, repliques=list(lines))


def cabinet():
    casting = STYLE['casting']
    return {
        'lea': acteur(casting['lea']['rig'],713,1645,1.04, regard=[-.85,-.5]),
        'docteure': acteur(casting['docteure']['rig'],328,1645,1.08,regard=[.8,.5]),
    }


def construire():
    config = {
      'titre': 'La bactérie qui n’a pas bougé', 'niche': 'corps-humain', 'degrade_bas': False,
      'legendes_y': STYLE['legendes_y'], 'palette': {'accent': STYLE['abonnement_final']['couleur']},
      'voix': {
        'estomac': {'voix':'blase','stabilite':.38},
        'gelule': {'voix':'ado_garcon','stabilite':.32},
        'peau': {'voix':'diva','stabilite':.44},
        'resistante': {'voix':'lascar','stabilite':.36},
        'globule': {'voix':'chef','stabilite':.44},
        'lea': {'voix':STYLE['casting']['lea']['voix'],'stabilite':.45},
        'docteure': {'voix':STYLE['casting']['docteure']['voix'],'stabilite':.48},
      },
      'bruitages': {
        'ploc': {'fichier':'sons/ploc.wav','volume':.38},
        'alerte': {'fichier':'sons/alerte.wav','volume':.37},
        'passage': {'fichier':'sons/passage.wav','volume':.34},
      },
      'plans': [
        plan('la-vieille-boite','estomac',{
          'estomac':acteur('estomac',821,811,1,regard=[-.85,.12]),
          'gelule':acteur('gelule',681,1014,1.08,regard=[.8,-.25])},
          replica('estomac',"Oh, la gélule qui revient ! | Léa a encore pioché | dans son vieux traitement.",'weary','inquiet',sfx=['ploc@0.61']),
          replica('gelule',"J’ai une tête d’antidouleur ? | Je sers à traiter | certaines infections bactériennes.",'baffled','fache',reactions={'estomac':'gene'}),
          replica('estomac',"Elle a juste mal au crâne. | Et toi, t’as une ordonnance pour aujourd’hui ?",'dryly','malicieux'),
          replica('gelule',"Non. Apparemment, | son placard fait des consultations.",'deadpan','fatigue',pause=.65),
        ),
        plan('la-breche','plaie',{
          'peau':acteur('peau',226,657,1,regard=[.85,.22]),
          'resistante':acteur('resistante',570,817,1.01,regard=[-.8,0]),
          'sensible1':acteur('bacterie',750,799,.80),
          'sensible2':acteur('bacterie',838,957,.71),
          'sensible3':acteur('bacterie',491,1027,.70),
          'globule':acteur('globule',288,961,1.04,regard=[.85,0])},
          replica('peau',"Quelques jours plus tard… | Aïe ! Léa s’est râpé le genou. | J’ai une brèche !",'startled','choque',sfx=['alerte@1.68']),
          replica('resistante',"J’ai vu de la lumière. | Je me suis permis.",'cheeky','malicieux',reactions={'peau':'fache'}),
          replica('peau',"Tu ressors. | Et tu dis à tes copines | que c’est complet.",'irritated','fache'),
          replica('resistante',"Trop tard, | on a déjà lancé les invitations.",'amused','content',sfx=['ploc@0.88']),
          replica('globule',"Globule blanc à l’entrée ! | J’essaie de les contenir.",'brisk','fache',reactions={'peau':'inquiet'}),
          replica('peau',"Le problème, | c’est qu’elles sont déjà plus nombreuses.",'worried','inquiet',pause=.55),
        ),
        plan('cette-fois','estomac',{
          'estomac':acteur('estomac',821,811,1,regard=[-.85,.12]),
          'gelule':acteur('gelule',681,1014,1.08,regard=[.8,-.25])},
          replica('estomac',"Encore toi ?",'confused','choque',sfx=['ploc@0.45']),
          replica('gelule',"Cette fois, j’ai une ordonnance. | C’est pour son infection, | pas pour son mal de tête.",'assured','content',pause=.52),
        ),
        plan('celles-qui-restent','plaie',{
          'globule':acteur('globule',270,858,1.03,regard=[.85,0]),
          'resistante':acteur('resistante',665,797,1.08,regard=[-.8,0]),
          'sensible1':acteur('bacterie',510,617,.78),
          'sensible2':acteur('bacterie',833,666,.72),
          'sensible3':acteur('bacterie',467,993,.72),
          'clone1':acteur('resistante',812,599,.69),
          'clone2':acteur('resistante',870,944,.65),
          'clone3':acteur('resistante',558,1034,.60)},
          replica('globule',"Tiens, les vertes disparaissent. | On a enfin | un peu de calme.",'relieved','content',sfx=['passage@0.55']),
          replica('resistante',"Elles, peut-être. | Moi, je résiste | à cet antibiotique.",'smug','malicieux',reactions={'globule':'choque'}),
          replica('globule',"T’étais déjà là, toi ?",'surprised','choque'),
          replica('resistante',"Depuis le début. | Et maintenant, j’ai de la place pour ma famille.",'amused','content',sfx=['ploc@1.55','ploc@2.1']),
          replica('globule',"Super. | J’aurais dû poser mon vendredi.",'deadpan','fatigue',pause=.62),
        ),
        plan('au-cabinet','cabinet-abonne-toi',cabinet(),
          replica('lea',"Docteure, ma plaie s’aggrave. | C’est moi qui suis devenue résistante ?",'worried','inquiet',reactions={'docteure':'inquiet'}),
          replica('docteure',"Ce sont les bactéries. | Certaines résistent | à cet antibiotique, | survivent et peuvent se multiplier.",'warm explaining','content',reactions={'lea':'neutre'}),
          replica('docteure',"Prendre des antibiotiques | quand ils sont inutiles | favorise les bactéries résistantes.",'calm explaining','neutre',reactions={'lea':'inquiet'}),
          replica('lea',"Et mon ancienne boîte, | je la garde au cas où ?",'curious','inquiet'),
          replica('docteure',"Rapporte-la à la pharmacie. | Si on te prescrit un antibiotique, | suis la dose | et la durée prévues.",'reassuring','content',reactions={'lea':'neutre'}),
          replica('docteure',"Pour ta plaie, on réévalue. | Un prélèvement peut | nous aider à choisir | un traitement qui agit.",'matter-of-fact','content'),
          replica('docteure',"Abonne-toi. | Ici, même les bactéries | doivent rendre des comptes.",'dry smile','malicieux',
                  regards={'docteure':[0,0]},sfx=['ding@.13'], pause=.55,
                  carte=STYLE['abonnement_final']),
        ),
      ],
    }
    clinic=config['plans'][-1]
    clinic['decor']=STYLE['cabinet']
    clinic['zoom']=[1,1.018]
    for shot, organ in zip(config['plans'][:-1], ('estomac', 'peau', 'estomac', 'peau')):
        shot['organe'] = organ
    for line in clinic['repliques']:
        line['regards']={'lea':[-.85,-.5], 'docteure':[.8,.5], **line.get('regards',{})}
    return config


if __name__=='__main__':
    OUT.write_text(yaml.safe_dump(construire(),allow_unicode=True,sort_keys=False,width=108))
