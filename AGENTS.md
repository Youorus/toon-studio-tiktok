# Toon Studio

Lire `README-PASSATION.md`, `docs/PRODUCTION.md` et la charte du compte avant de produire. Pour Le Corps Parle.fr, vérifier `lcp-1.2.0` avec `python -m toonstudio.production style corps-humain`. Le casting, les fonds de série, la palette corail, les yeux, le filigrane, les badges et le format des sous-titres viennent du profil approuvé. Les changements de socle requièrent une validation et une nouvelle version.

Pour chaque nouvelle référence, consigner les actions, les intentions, les repères et les sources dans `provenance.md`. Le cadre mural secondaire porte un conseil court et propre au sujet. Le corail couvre le fond des plans anatomiques d’un bord à l’autre. Livrer un export vérifié, le SRT, le ZIP de production et le dossier de contestation généré à partir de `preuves.yaml`. Écarter les références vidéo, les secrets, les caches et les pistes privées des commits.

Avant toute génération Recraft, lire `niches/corps-humain/BIBLIOTHEQUE.yaml` et examiner les actifs qui conviennent au plan. Réutiliser les silhouettes, rigs, décors et accessoires déjà disponibles. Ajouter à l’inventaire les nouveaux éléments réalisés pour l’épisode.

Lire `docs/WORKFLOWS-ET-SKILLS.md` pour les outils, les guides facultatifs et leurs équivalents pour tout agent. Agrandir le kit par réemploi et variantes de calques avant tout appel Recraft. Livrer `inventaire-reemploi.json` pour distinguer les actifs repris, les variantes et les générations payantes réelles ; ne pas changer le socle approuvé pour changer de sujet.

Pour chaque épisode terminé de Le Corps Parle.fr, livrer `publication-tiktok.txt` dans le dossier de l’épisode, prêt à copier : accroche courte, question engageante et hashtags pertinents. Lire `docs/PUBLICATION-TIKTOK.md`. Vérifier les occultations : les mains au repos restent derrière la table ; une main levée ne traverse pas les assiettes et utilise une silhouette lisible.

Après archivage, sauvegarder chaque livraison dans le bucket CAlabs Studio avec `python -m toonstudio.postly <dossier> --envoyer`. Lire `integrations/postly/README.md`, vérifier le reçu et les téléchargements. Garder `#Santé` parmi les hashtags du compte. Le transfert des médias n’est pas une publication TikTok ou Buffer.

Avant chaque scénario de Le Corps Parle.fr, lire `docs/MASTER-PROMPT-TIKTOK.md` et `docs/SCENARIOS-RETENTION.md`. Priorité : progression vers 10 000 abonnés authentiques, rétention, humour naturel et faits médicaux justes. Les objectifs chiffrés sont expérimentaux. Joindre la fiche éditoriale du modèle au nouvel épisode et distinguer format court de croissance et récit de plus d’une minute destiné au programme de récompenses.

Une date donnée par Marc désigne un dossier de `niches/corps-humain/downloads/`. Lire `docs/REFERENCES.md` et le catalogue de la niche ; préparer la vidéo avec `python -m toonstudio.references preparer <date>`, analyser ses images et son audio puis consigner l’ID, le SHA-256 et les repères dans la provenance. Si la date contient plusieurs vidéos, préciser laquelle. Sauvegarder les nouveaux ajouts avec `python -m toonstudio.references sauvegarder`. Le filigrane canonique des nouveaux rendus est exactement **@lecorps.parle.fr**.
