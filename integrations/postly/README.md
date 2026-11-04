# Le Corps Parle.fr dans CAlabs Studio

GitHub conserve le code et les actifs ; le stockage privé Postly conserve aussi les vidéos, sources ZIP, SRT, descriptions, captures et textes de contestation. Accès : `https://studio.seyalabs.com`, carte **Le Corps Parle.fr**, **Voir les vidéos**.

La destination est dans `config.json`, sans secret. La clé SSH reste sur le poste. Le module serveur `scripts/import_local_studio.py` est versionné dans le backend Postly. Il ne publie pas de vidéo et ne lance pas Art Echo.

Après production, contrôle et archivage :

```sh
PYTHONPATH=. .venv/bin/python -m toonstudio.postly niches/corps-humain/episodes/<episode> --envoyer
```

Sans `--envoyer`, préparer seulement le lot local. Sans dossier, prendre les épisodes possédant `recu-livraison.json`. Le script vérifie les empreintes du master et du ZIP, le manifeste, les captures, le SRT et la description. Inclure `#Santé`, le tag de série et des mots-clés pertinents, pour cinq hashtags au maximum selon notre convention éditoriale.

Le serveur vérifie chaque fichier, sonde et décode le MP4 et relit les copies du bucket avant de valider les fiches. Le master reste identique. Un réimport ne crée pas de doublon. Le dossier de transit de cet envoi est supprimé seulement après le reçu vérifié ; en cas d’échec il reste disponible pour une reprise.

Chaque dossier d’épisode reçoit `recu-postly.json` : lien, UUID, SHA-256 et nombre de fichiers relus. L’inventaire et le reçu du lot sont dans `integrations/postly/out/`, ignoré par Git. Ne pas déclarer la livraison en ligne avant vérification du reçu et des téléchargements authentifiés.

Cette bibliothèque est exclue de la purge automatique après publication. Le compte est créé pour le téléchargement et la publication manuelle. Relier Buffer ou activer une programmation relève d’une demande distincte. Les autres comptes restent inchangés.
