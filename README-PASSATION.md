# Passation de production · Le Corps Parle.fr

**Compte** `@lecorps.parle.fr` · **Profil de série** `lcp-1.1.0` · **Studio** Toon Studio

Ce fichier est le point d’entrée pour Codex, Claude, Gemini ou un autre assistant. Ouvrir le dossier **toon-studio** comme espace de travail. Lire ce document, puis la [charte](docs/DIRECTION-ARTISTIQUE.md) et le [guide de production](docs/PRODUCTION.md). Les instructions récentes de Marc priment. Toute évolution du socle approuvé demande une validation et une nouvelle version du profil.

- **Sur le Mac** `/Users/marc./Documents/ChatGPT/postly/toon-studio`
- **Dépôt** [Youorus/toon-studio-tiktok](https://github.com/Youorus/toon-studio-tiktok)
- **Réglages et empreintes** [niche.yaml](niches/corps-humain/niche.yaml) et [profil-verrou.json](niches/corps-humain/profil-verrou.json)
- **Épisodes étalons** [006 pour les actions et le montage](niches/corps-humain/episodes/006-antibioresistance-v3/), [007 révisé pour le corail en plein cadre et le jeu d’accessoires](niches/corps-humain/episodes/007-alcool-grossesse/) et [008 pour l’appel en écran partagé et une variante de corpulence](niches/corps-humain/episodes/008-estomac-sature/)

## Au démarrage

1. Ouvrir un nouveau dossier dans `niches/corps-humain/episodes/<numero>-<sujet>/`. Le [modèle d’épisode](niches/corps-humain/production/modele-episode/) donne le format de base. Les dossiers 006 et 007 montrent comment ajouter une mise en scène précise en Python.
   Consulter la [bibliothèque de la série](niches/corps-humain/BIBLIOTHEQUE.yaml) et les épisodes existants avant toute génération. Vérifier les silhouettes et les calques à l’écran. Réutiliser les actifs disponibles et décliner leurs couleurs ou accessoires selon le plan. Réserver Recraft aux éléments qui manquent réellement.
2. Vérifier le profil. Si un fichier du socle a dérivé, identifier le changement et la version approuvée avant le rendu. Réserver `--figer` aux changements de charte validés par Marc.
3. Préserver les fichiers et archives des autres épisodes. Garder une nouvelle version du master à chaque révision livrée.

```sh
cd '/Users/marc./Documents/ChatGPT/postly/toon-studio'
.venv/bin/python -m toonstudio.production style corps-humain
```

Sur un autre poste, utiliser Python 3.12, FFmpeg et FFprobe, puis installer `requirements.txt` dans un environnement virtuel. Le moteur se trouve dans `toonstudio/`. Recraft sert aux nouvelles illustrations et ElevenLabs aux voix récurrentes. Utiliser le cache et le registre privé des voix configuré sur le poste. Le chemin du registre est configurable avec `TOON_VOICES_CONFIG`. Pour rouvrir un ZIP, utiliser `TOON_PRISES_INDEX` et les prises archivées. Garder les clés et les caches hors des livraisons et du dépôt.

## Les deux façons de partir

| Entrée donnée par Marc | Travail à faire |
|---|---|
| **Vidéo de référence** | Regarder le début, les pivots et la fin. Relever les plans et les temps, l’intention des répliques, les expressions, les gestes, les accessoires, le contact, la réaction et le bruitage. Utiliser si nécessaire les images extraites du fichier local dans `audits/dr-healthcare/corpus/`. Produire un équivalent français avec nos visuels, nos répliques et notre musique. Documenter ce qui vient de la référence et ce qui a été créé dans le studio. |
| **Script ou scénario de Marc** | Respecter ses répliques, ses vannes et l’ordre prévu. Corriger les fautes et vérifier les faits. Signaler une correction médicale ou une modification de fond qui changerait le sens. Ajouter les indications de jeu et les mouvements autour du texte. Si Marc demande une validation du script ou une ébauche, livrer d’abord cette étape. |

Pour un sujet médical, vérifier les faits avec une source primaire ou institutionnelle pertinente. Conserver le lien dans `provenance.md`. Réserver les exagérations aux gags visuels et faire formuler le conseil de façon claire et exacte par la docteure.

## Les éléments fixes de la série

- **Structure.** Ouvrir dans le corps dès la première image, avec un geste ou une vanne dans les trois premières secondes. Faire avancer le sketch par l’action et les réactions. Terminer au cabinet avec Léa, la docteure, l’explication et un appel à s’abonner à l’oral et à l’image. La durée habituelle est 65 à 72 secondes. Adapter la durée au récit et aux indications de Marc.
- **Couleur.** Remplir le fond anatomique en corail vif `#E75261` jusque dans les coins et pendant les coupes. Utiliser les roses de tissu et le bordeaux pour le relief. Réserver le noir au trait. Garder le cabinet gris-bleu approuvé. Vérifier le décor source puis les bords du MP4.
- **Casting.** Réutiliser exactement les rigs `docteure-aplats` et `lea-aplats` et les alias vocaux `mere` et `patiente`. Si Marc demande une corpulence ou un costume particulier, créer une variante dans le dossier de l’épisode, en conservant la tête, la coiffure, les couleurs et la voix du personnage. Pour un nouveau personnage, créer une silhouette simple et immédiatement lisible, avec aplats, contour net et expressions distinctes. Partir des éléments existants quand ils conviennent. Sinon utiliser Recraft avec la palette du studio ou créer un accessoire en calques dans le moteur.
- **Animation.** Donner du jeu aux yeux, aux mains et aux accessoires. Sur une action rapide, animer l’anticipation, le contact, la réaction et le retour au calme. Faire suivre la main et l’objet sur une trajectoire commune. Mettre le bruitage sur le contact et garder une respiration pour la chute comique.
- **Son.** Français familier, débit naturel et personnages immédiatement reconnaissables. Réutiliser les alias validés et garder les alignements originaux pour les lèvres et les mots. Utiliser **« Petites combines » à 125 BPM**, avec la voix au premier plan et une baisse musicale sur les impacts et les répliques.
- **Habillage.** Vertical `1080×1920`, 30 images/s. Badge d’organe en haut à gauche. Mini-badges accrochés aux nouveaux personnages, au plus deux à la fois. Sous-titres blancs en capitales, un mot à la fois, avec ombre sombre et SRT en phrases à côté. Filigrane blanc translucide **Le Corps Parle.fr** qui glisse entre ses positions, dans une zone libre.
- **Cabinet.** Garder le premier cadre manuscrit « Abonne-toi ». Ajouter dans le second un conseil différent à chaque épisode, court, juste et écrit dans le ton de la chaîne. Adapter une copie du décor dans le dossier de l’épisode. Garder le bouton final « ABONNE-TOI ».

## De la fabrication à la livraison

1. **Préparer.** Garder les dessins d’origine, les calques, les accessoires, le script français, `episode.yaml`, les commandes de rendu, `provenance.md` et `preuves.yaml`. Dans ce dernier, nommer trois calques réellement utilisés, trois instants du master et résumer honnêtement la fabrication.
2. **Animer et sonoriser.** Faire un aperçu aux temps importants. Examiner les plans aux dimensions d’un téléphone. Rendre une version image, voix et bruitages, puis mixer la signature musicale. Le [007](niches/corps-humain/episodes/007-alcool-grossesse/README.md) donne les commandes complètes.
3. **Contrôler.** Lire le MP4 de bout en bout ou vérifier les plans et les passages d’action au plus près, avec un décodage intégral. Vérifier le format, le cadrage TikTok, les aplats corail, les badges, la synchro, la lisibilité des deux cadres, le bouton final et l’intelligibilité des voix. Refaire le rendu si nécessaire.
4. **Archiver.** Livrer le MP4, le SRT, le ZIP vérifié et le dossier court de contestation. Garder le MP4 exact dans l’archive. Pour des calques d’un autre épisode, ajouter un `--dependance <dossier>` par dossier utilisé.

```sh
.venv/bin/python -m toonstudio.production archiver niches/corps-humain/episodes/<dossier> \
  --master <mp4-final> --sec <mp4-voix-et-bruitages>
.venv/bin/python -m toonstudio.production verifier <zip-produit>
```

Le dossier `-contestation` est généré à côté du ZIP dans `archives-production/corps-humain/`. Il contient **01-calques-et-rendu.jpg**, **02-reperes-de-montage.jpg** et **texte-contestation.txt**. Les images viennent des vrais calques et du MP4 livré. Garder le dossier qui correspond à la version publiée. En cas de demande TikTok, adapter le texte au motif exact et suivre les champs affichés dans le formulaire. Voir le [guide de contestation](docs/PRODUCTION.md#si-une-vidéo-est-contestée).

Le dépôt reçoit le code, les réglages, les éléments du studio et les reçus. Garder les masters, les ZIP, les voix brutes et le corpus de référence dans le stockage local ou privé. Livrer les liens aux fichiers exacts. Publier sur TikTok uniquement si Marc le demande.

## Message à donner à l’assistant suivant

> Tu travailles dans `/Users/marc./Documents/ChatGPT/postly/toon-studio`. Lis `README-PASSATION.md` et vérifie le profil de Le Corps Parle.fr. Voici ma référence ou mon script. Produis l’épisode en suivant la charte et livre le MP4, le SRT, le ZIP vérifié et les pièces de contestation. Indique les décisions prises et les vérifications effectuées.
