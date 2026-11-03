# Il bouge… mais il n’avance pas

Épisode 004 · Ton corps, expliqué · 3 novembre 2026

Deux spermatozoïdes agitent leur flagelle. Un seul avance franchement. Au cabinet, Léa apprend ce que le spermogramme mesure et ce qu’un premier résultat permet de conclure.

## Référence et choix éditorial

Le [TikTok de Dr Healthcare](https://www.tiktok.com/@dr..healthcare1/video/7559266279207587094) associe un sketch sur le spermogramme, autour de 0–53 s, et un sketch sur la constipation. Cet épisode développe le premier sujet avec un dialogue écrit pour Toon Studio. La différence de progression se voit dans la trompe puis sous un microscope schématique. Le cabinet ajoute la distinction entre forme et mobilité et revient sur la portée de l’examen. La fin comprend l’invitation orale et visuelle à s’abonner.

La référence est archivée dans le [corpus de l’audit](../../../../audits/dr-healthcare/corpus/7559266279207587094.mp4). Le rendu utilise des illustrations originales générées avec Recraft, des calques préparés pour Toon Studio, des voix françaises ElevenLabs et des bruitages locaux. Le schéma grossit volontairement les cellules pour montrer le trajet et la différence de progression.

## Vérification des faits

| Élément du film | Source |
| --- | --- |
| Les spermatozoïdes remontent vers les trompes et la rencontre avec l’ovule s’y fait habituellement. | [Assurance Maladie, fécondation et développement](https://www.ameli.fr/assure/sante/devenir-parent/grossesse/grossesse-en-bonne-sante/grossesse/premiers-symptomes-grossesse) |
| Mobilité et morphologie sont des mesures distinctes. La mobilité progressive décrit un déplacement, au-delà du mouvement sur place. | [Association européenne d’urologie, guide clinique](https://uroweb.org/guidelines/sexual-and-reproductive-health/chapter/male-infertility) · [Manuel de laboratoire de l’OMS](https://www.who.int/publications/b/59107) |
| Un seul résultat n’établit pas l’infertilité. Un premier spermogramme anormal est à confirmer. | [Assurance Maladie, bilan de l’infertilité](https://www.ameli.fr/assure/sante/devenir-parent/concevoir-un-enfant/sterilite-pma-infertilite/bilan-medical-infertilite-sterilite) · [Association européenne d’urologie, guide clinique](https://uroweb.org/guidelines/sexual-and-reproductive-health/chapter/male-infertility) |

Les deux cellules du sketch servent à comparer des mouvements. Elles ne représentent ni un seuil clinique ni un diagnostic de morphologie.

## Fabrication

- [Épisode, répliques et animation](episode.yaml). Le trajet de Malo, le mouvement sur place de Nino et les réactions sont réglés indépendamment des répliques. Les flagelles restent attachés au cou pendant l’ondulation.
- Les visuels Recraft sont dans art/. Le [script de préparation](preparer_art.py) construit le détourage, les rigs, le décor de microscope et trois bruitages courts. Les teintes chaudes de la trompe et de l’utérus contrastent avec le vert-bleu de la consultation. Les deux personnages humains ont été créés pour cet épisode.
- Le [script de rendu](produire.py) utilise les prises ElevenLabs du cache Toon Studio, aligne les groupes de mots sur ces prises et exporte les sous-titres incrustés ainsi que le SRT. Les prises suivent quatre profils vocaux du studio.
- Recraft a fourni neuf images en huit appels pour **0,315 $** d’après le journal du studio, variantes de décor comprises. Le relevé ElevenLabs retrouve **457 crédits** pour les douze répliques dans l’historique du forfait Creator. [Reçu de consommation](cout.json)

Depuis la racine de Toon Studio.

```sh
projet=niches/corps-humain/episodes/004-le-spermogramme
PYTHONPATH=. .venv/bin/python "$projet/preparer_art.py"
PYTHONPATH=. .venv/bin/python "$projet/produire.py"
```

## Sorties

- [MP4 sous-titré](out/Il-bouge-mais-il-navance-pas.mp4)
- [Planche tirée du MP4](out/planche.jpg)
- [Sous-titres séparés](out/sous-titres.srt)
- [Contrôle technique](out/controle-final.json)
