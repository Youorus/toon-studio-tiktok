# Produire et livrer un épisode Toon Studio

## Le Corps Parle.fr · lcp-1.0.0

Le [profil verrouillé](../niches/corps-humain/profil-verrou.json) identifie la charte, le casting, les décors récurrents, le moteur d’habillage, les mouvements de l’épisode étalon et le code de la musique. Il fixe le rendu approuvé de l’[épisode 006](../niches/corps-humain/episodes/006-antibioresistance-v3/). Un nouveau sujet vit dans son propre dossier et fournit ses personnages secondaires, ses accessoires, ses animations et son conseil du cabinet.

Depuis la racine du dépôt, contrôler la version avant de commencer et avant de livrer.

```sh
.venv/bin/python -m toonstudio.production style corps-humain
```

Une modification approuvée du socle doit recevoir un nouvel identifiant de version dans `niche.yaml`. La commande avec `--figer` enregistre les nouvelles empreintes, qui sont à relire avec le diff. Les anciennes archives gardent le profil dont elles sont issues.

## Boucle de production

1. Relever les actions, les réactions, les rôles des répliques et les transitions de la référence. Consigner le lien et les choix de réécriture dans `provenance.md`.
2. Écrire le texte français, vérifier l’idée médicale et le conseil mural. Réutiliser les voix, les calques récurrents et le décor du cabinet. Créer les actifs propres au sujet.
3. Enregistrer les prises, caler les gestes et les sons sur leurs attaques, puis rendre. Contrôler la version verticale à taille téléphone, l’intelligibilité, la présence des badges, les deux cadres et le filigrane. Exporter le MP4, le SRT, le plan de montage et les contrôles.
4. Archiver les sources, le MP4 exact et les pistes audio. Utiliser le nom du dossier de l’épisode et les chemins de sa livraison.

```sh
.venv/bin/python -m toonstudio.production archiver niches/corps-humain/episodes/<id> \
  --master <mp4-livre> --sec <mp4-voix-bruitages>
.venv/bin/python -m toonstudio.production verifier <zip-produit>
```

Répéter `--dependance <dossier-episode>` si le plan réutilise des actifs ou du code d’un autre épisode. Les archives sont dans `archives-production/<niche>/` et contiennent notamment les prises et leurs alignements, les calques, le code, la piste musicale, la version livrée et un manifeste SHA-256. Conserver le ZIP privé et une copie dans le stockage choisi par le compte. Un ZIP portant une nouvelle empreinte du master constitue une livraison distincte.

## Si une vidéo est contestée

Reprendre le motif exact dans la notification ou dans le tableau de bord TikTok. Préparer le lien de la publication, le master concerné, les repères de montage et deux ou trois pièces qui montrent la fabrication, par exemple une planche de calques, des prises séparées et le fichier du plan de montage. Indiquer honnêtement les références et les outils utilisés. Joindre seulement ce que le formulaire accepte. Les empreintes servent à vérifier l’intégrité des fichiers. L’appréciation de l’originalité et de l’éligibilité dépend du programme et de la décision de TikTok.

- [Violations du contenu et contestations](https://support.tiktok.com/en/safety-hc/account-and-user-safety/content-violations-and-bans)
- [Programme de récompenses pour les créateurs](https://support.tiktok.com/en/business-and-creator/creator-rewards-program/creator-rewards-program)

Les clés d’API, le cache général, les copies de référence et les ZIP de preuves restent dans le stockage local prévu. Le dépôt conserve le moteur, les actifs du studio, la charte, les scripts et les reçus de livraison.
