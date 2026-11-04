# Produire et livrer un épisode Toon Studio

## Le Corps Parle.fr · lcp-1.2.0

Le [profil verrouillé](../niches/corps-humain/profil-verrou.json) identifie la charte, le casting, les décors récurrents, le moteur d’habillage, les mouvements de l’épisode étalon et le code de la musique. Il fixe le rendu approuvé de l’[épisode 006](../niches/corps-humain/episodes/006-antibioresistance-v3/). Un nouveau sujet vit dans son propre dossier et fournit ses personnages secondaires, ses accessoires, ses animations et son conseil du cabinet.

Depuis la racine du dépôt, contrôler la version avant de commencer et avant de livrer.

```sh
.venv/bin/python -m toonstudio.production style corps-humain
```

Une modification approuvée du socle doit recevoir un nouvel identifiant de version dans `niche.yaml`. La commande avec `--figer` enregistre les nouvelles empreintes, qui sont à relire avec le diff. Les anciennes archives gardent le profil dont elles sont issues.

## Boucle de production

1. Résoudre le dossier daté dans le catalogue et suivre [le parcours des références](REFERENCES.md). Examiner la chronologie, les images successives et l’audio. Relever les actions, les réactions, les répliques et les transitions. Consigner la date, l’ID, le SHA-256, les repères source et les choix de réécriture dans `provenance.md`. Renseigner ensuite `preuves.yaml` avec les calques du projet, trois temps du master et le résumé de fabrication.
2. Écrire le texte français, vérifier l’idée médicale et le conseil mural. Réutiliser les voix, les calques récurrents et le décor du cabinet. Créer les actifs propres au sujet.
3. Enregistrer les prises, caler les gestes et les sons sur leurs attaques, puis rendre. Contrôler la version verticale à taille téléphone, l’intelligibilité, la présence des badges, les deux cadres et le filigrane. Exporter le MP4, le SRT, le plan de montage et les contrôles.
4. Écrire `publication-tiktok.txt` dans le dossier de l’épisode : description courte prête à copier, avec une question et des hashtags pertinents. Voir [les consignes de publication](PUBLICATION-TIKTOK.md). Le contrôle d’archivage exige ce fichier pour Le Corps Parle.fr.
5. Archiver les sources, le MP4 exact, le texte de publication et les pistes audio. Utiliser le nom du dossier de l’épisode et les chemins de sa livraison.

```sh
.venv/bin/python -m toonstudio.production archiver niches/corps-humain/episodes/<id> \
  --master <mp4-livre> --sec <mp4-voix-bruitages>
.venv/bin/python -m toonstudio.production verifier <zip-produit>
```

Répéter `--dependance <dossier-episode>` si le plan réutilise des actifs ou du code d’un autre épisode. Les archives sont dans `archives-production/<niche>/` et contiennent notamment les prises et leurs alignements, les calques, le code, la piste musicale, la version livrée et un manifeste SHA-256. Conserver le ZIP privé et une copie dans le stockage choisi par le compte. Un ZIP portant une nouvelle empreinte du master constitue une livraison distincte. L’archivage contrôle aussi les décors des plans anatomiques pour repérer les fonds noirs et les zones transparentes.

## Si une vidéo est contestée

Pour une inéligibilité au fil Pour toi, ouvrir la vidéo, puis ses statistiques, la notification et **Contester**. Pour le Programme de récompenses, ouvrir la décision d’éligibilité dans le tableau de bord du programme. Ces aides publiques décrivent le parcours et la possibilité de faire appel. Le formulaire affiché avec la décision indique les pièces qu’il accepte. Garder aussi une capture de la notification si le support demande le motif exact.

Chaque livraison génère un dossier `-contestation` à côté du ZIP. Il contient `01-calques-et-rendu.jpg`, `02-reperes-de-montage.jpg` et `texte-contestation.txt`. Compléter le texte avec le lien de la publication et le motif affiché. Si le formulaire accepte une image, joindre d’abord la première planche, qui réunit les calques et un extrait du master. La deuxième montre les repères des prises et trois captures du MP4. Utiliser le dossier correspondant exactement à la vidéo publiée. Le ZIP complet reste disponible si le support demande plus de détails.

Pour générer les trois fichiers d’une livraison existante, utiliser `python -m toonstudio.production preuves <dossier-épisode> --master <mp4-publié>`.

- [Contester une inéligibilité au fil Pour toi](https://support.tiktok.com/en/safety-hc/account-and-user-safety/content-violations-and-bans?invalid_lang=de)
- [Éligibilité et contestation dans le Programme de récompenses](https://support.tiktok.com/en/business-and-creator/creator-rewards-program/how-is-the-creator-rewards-program-different-from-the-tiktok-creator-fund?invalid_lang=ko)

Les clés d’API, le cache général, les copies de référence et les ZIP de preuves restent dans le stockage local prévu. Le dépôt conserve le moteur, les actifs du studio, la charte, les scripts et les reçus de livraison.
