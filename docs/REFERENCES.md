# Références datées — Le Corps Parle.fr

Ce parcours est commun à Codex, Claude, Gemini et aux autres agents ayant accès au projet. Une demande comme **« Produis depuis le dossier 2026-11-01 »** désigne le corpus privé de la niche. Lire ce document, `README-PASSATION.md`, la charte et les consignes de scénario avant la production.

## Où retrouver la vidéo

- Originaux locaux : `niches/corps-humain/downloads/AAAA-MM-JJ/`.
- Catalogue durable : `niches/corps-humain/references/catalogue.json`, avec titre, nom original, ID, caractéristiques et SHA-256.
- Copie privée serveur : section **Références** de CAlabs Studio, compte Le Corps Parle.fr.
- Les fichiers vidéo restent hors de Git ; le catalogue, les outils et les consignes sont dans GitHub.

Les dossiers représentent les dates fournies avec les fichiers ; ne pas inventer une autre date de publication. Conserver les noms d’origine. Plusieurs vidéos peuvent partager une date. Dans ce cas, lire les titres et préciser `--video <identifiant>` ; ne jamais en choisir une au hasard. Le bouton **Copier la consigne** du studio inclut l’identifiant quand il est nécessaire.

## Commandes communes aux IA

Depuis la racine Toon Studio :

```sh
# Actualiser le catalogue après un ajout local
PYTHONPATH=. .venv/bin/python -m toonstudio.references indexer

# Sauvegarder les originaux, miniatures et l'historique de téléchargement
PYTHONPATH=. .venv/bin/python -m toonstudio.references sauvegarder

# Préparer une référence : toutes les images, horodatages, audio et planches
PYTHONPATH=. .venv/bin/python -m toonstudio.references preparer 2026-11-01

# Si le fichier manque sur ce poste, le restaurer depuis le serveur puis le préparer
PYTHONPATH=. .venv/bin/python -m toonstudio.references restaurer 2026-11-01
```

Ajouter `--video <ID TikTok, ID du catalogue ou fragment unique du titre>` quand le dossier contient plusieurs vidéos. La restauration vérifie le SHA-256 avant de remettre le fichier à son emplacement. Une copie locale différente n’est pas remplacée silencieusement. Un agent sans accès SSH peut demander le téléchargement de la référence depuis le studio et la placer au chemin du catalogue ; les clés ne doivent jamais être copiées dans un chat ou un kit.

## Lire la référence avant d’animer

La commande `preparer` écrit dans `niches/corps-humain/references/analyses/<ID>/` :

- `reference.json` : identité du fichier, empreinte et nombre d’images extraites.
- `images/` : chaque image décodée, à la résolution source, sans accélérer la vidéo.
- `images-et-temps.json` : ordre des images et horodatages source.
- `caracteristiques-source.json` : caractéristiques des flux et décalages temporels source.
- `audio-reference.wav` : piste de travail pour écouter les voix, la musique et les bruitages.
- `planche-*.jpg` : repérage d’ensemble, à environ une image par seconde.
- `analyse.md` : journal à compléter avec les passages réellement examinés.

Les planches d’ensemble ne remplacent pas la lecture image par image. Examiner la chronologie complète et ouvrir les images successives autour des changements d’expression, anticipations, contacts, chutes et transitions. Écouter l’audio en continu puis revoir les passages d’action avec leurs sons. Relever le début et la fin des plans, les mots, le jeu vocal, les silences comiques, les accessoires, les trajectoires et le point exact de chaque contact. Conserver les temps source séparés de ceux de notre futur montage.

L’extraction technique n’est pas une analyse sémantique. Ne pas annoncer avoir tout regardé ou écouté si l’outil ou l’agent n’a examiné qu’un aperçu. Noter ce qui a été vérifié dans `analyse.md`. Pour un détail de finition ou de couleur, revenir à l’original ou à une image native ciblée.

## Passer à notre épisode

Reproduire fidèlement la construction, les actions, les réactions, les intentions des dialogues et l’énergie de la référence, avec notre direction artistique. Relever les répliques et préparer leur version française selon les consignes de Marc. Garder nos personnages, notre palette corail, nos voix, notre musique et notre habillage. Consulter `BIBLIOTHEQUE.yaml` avant de créer un actif.

Ajouter dans la provenance de l’épisode la date du dossier, l’ID exact, le SHA-256 de la référence, les repères source et le lien vers l’analyse. Archiver les choix de fabrication et les prises de notre production. Les inspirations ont leur bibliothèque distincte ; elles ne deviennent pas des vidéos prêtes à publier ou des preuves que leurs dessins sont les nôtres.

Le filigrane des nouveaux rendus est obligatoirement **@lecorps.parle.fr**, avec la même finition et le même mouvement validés. Le profil `lcp-1.2.0` introduit ce texte canonique ; le casting, la palette, les décors et les voix sont conservés.

## Conservation

La sauvegarde serveur relit chaque fichier depuis le bucket et compare son SHA-256. Le catalogue conserve les entrées antérieures si un fichier disparaît du poste. Une nouvelle version possède un identifiant et une empreinte distincts. Les catalogues successifs et les originaux restent sous `backups/reference-library/`, hors de la purge des productions publiées.

Le reçu `niches/corps-humain/references/recu-sauvegarde.json` est la preuve du transfert terminé. Le simple fait d’avoir indexé le dossier local ne prouve pas sa sauvegarde en ligne. Ajouter chaque nouveau lot au serveur avant de déclarer son rangement terminé.
