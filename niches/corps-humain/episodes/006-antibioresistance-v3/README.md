# La bactérie qui n’a pas bougé · Reprise

[Analyse comparative de la référence](analyse-reference.md) · [Script français](script-francais.md)

Cette version reprend les étapes du film de référence avec les décors, le casting, les voix et la signature de Le Corps Parle.fr. Recraft a réalisé les deux nouveaux dessins à partir des descriptions et de la palette. Les accessoires et la cheville de Léa sont des calques de rendu. Les 27 prises françaises ont été enregistrées avec les profils du studio.

Le montage révisé utilise le policier minimaliste de Recraft avec des yeux, une moustache, des bottes, un panneau et une radio animés en couches. Le bras de la bactérie lance le coup, les accessoires suivent l’élan et le garde reste un temps au sol avant l’appel. Le filigrane blanc « Le Corps Parle.fr » change de place. Le deuxième cadre du cabinet affiche « Bactéries, prenez un ticket » avec le numéro 006.

## Fichiers

- [MP4 révisé prêt à publier](out/La-bacterie-qui-na-pas-bouge-Le-Corps-Parle-Policier.mp4)
- [Montage précédent et mix validé](out/La-bacterie-qui-na-pas-bouge-Le-Corps-Parle-Reprise.mp4)
- [Sous-titres SRT](out/sous-titres.srt)
- [Plan de montage et repères des gestes](out/montage.json)
- [Contrôle visuel de la révision](out/controle-policier.jpg) et [contrôle technique](out/controle-policier.json)

## Reproduction locale

Depuis la racine de Toon Studio, les deux commandes reconstruisent l’image à partir des illustrations et des prises en cache. `produire.py` reprend la piste audio du montage validé avec une copie directe. L’option `--audio-valide` permet d’indiquer l’emplacement de cette source.

```sh
p=niches/corps-humain/episodes/006-antibioresistance-v3
PYTHONPATH=. .venv/bin/python "$p/preparer.py"
PYTHONPATH=. .venv/bin/python "$p/produire.py"
```

Le modèle Recraft du nouveau garde se trouve dans `art/policier-comique.png`. `dialogues.py` conserve les répliques et les indications de jeu.

## Édition musicale Cartoon

Le [master Cartoon](out/La-bacterie-qui-na-pas-bouge-Le-Corps-Parle-Cartoon.mp4) reprend l’image validée et remplace le fond par « Petites combines ». Dans une archive, la commande suivante refait l’image avec le mix livré. Le fichier `livraison/voix-et-bruitages.m4a` est la source audio séparée pour refaire le mix.

```sh
export TOON_PRISES_INDEX="$PWD/prises/index.json"
p=niches/corps-humain/episodes/006-antibioresistance-v3
PYTHONPATH=. python "$p/produire.py" --audio-valide livraison/mix-final.m4a --sortie "$p/out/reconstruction.mp4"
```
