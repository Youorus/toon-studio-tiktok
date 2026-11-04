# Workflows et outils — consignes communes à toutes les IA

Demande de Marc du 4 novembre 2026 : agrandir le kit sans multiplier les appels Recraft, conserver l’identité et rendre la production transmissible à Codex, Claude et Gemini. Ce document accompagne `README-PASSATION.md`, `REFERENCES.md`, `PRODUCTION.md` et la charte. Le choix de l’agent ne modifie pas la direction artistique.

## Le moteur de production fait foi

Toon Studio est un pipeline Python reproductible. Il ne dépend pas de la présence d’un plugin HeyGen dans l’agent. Les skills servent de guides de travail ; ils ne remplacent ni les actifs approuvés, ni le profil, ni les contrôles du dépôt. Ne pas substituer un avatar HeyGen, un nouveau générateur vidéo ou une autre voix au casting existant.

| Étape | Implémentation utilisée | Guide utile si installé | Équivalent pour un autre agent |
|---|---|---|---|
| Retrouver une inspiration | `toonstudio.references`, catalogue, bibliothèque privée | `docs/REFERENCES.md` | Même CLI, original et SHA-256 ; aucun plugin requis |
| Examiner images et audio | FFmpeg/FFprobe, images natives, planches et journal ; Gemini multimodal en complément | Guide vidéo du fournisseur utilisé | Extraire toutes les images, examiner la chronologie et les gestes, transcrire l’audio avec un outil disponible et noter les limites réelles |
| Écrire le français et vérifier les faits | `dialogues.py`, `provenance.md`, master prompt et fiche éditoriale | `heygen:script-writer` si utilisé pour une réécriture | Appliquer `SCENARIOS-RETENTION.md`, préserver les demandes validées, vérifier les sources médicales |
| Illustrations manquantes seulement | `toonstudio.recraft`, cache et garde de budget | `docs/RECRAFT.md` | Réemployer d’abord les actifs ; Recraft uniquement pour une forme ou un décor réellement manquant |
| Prises expressives | `toonstudio.voice`, alias privés ElevenLabs, cache et alignements | Documentation ElevenLabs | Conserver les mêmes alias, enregistrer le jeu par réplique, ne pas cloner les voix de la référence |
| Animation et composition | PIL, NumPy, SciPy, `rig`, `episode`, `arms`, `limbs`, pistes temporelles | `heygen:motion-graphics` en guide facultatif | Mêmes calques et coordonnées, arcs, anticipation, contact, réaction, contrôles aux images clés |
| Sous-titres et badges | `toonstudio.sous_titres`, `cards`, alignements des prises | `heygen:captions` en guide facultatif | Garder le moteur existant et la police de la série ; produire aussi le SRT |
| Montage et contrôle | Python, FFmpeg, MP4 réel, synchronisation et revue audiovisuelle | `heygen:video-editing` utilisé comme guide de finition | Suivre la procédure ci-dessous avec les outils locaux, sans dépendance à HeyGen |
| Musique et bruitages | `musique_cartoon`, « Petites combines » 125 BPM et sons de la bibliothèque | Guide de mixage du dépôt et FFmpeg | Même composition, musique sous les voix, sons au contact, pas de reprise de la bande-son du tiers |
| Livraison et sauvegarde | `production archiver/verifier`, `preuves.yaml`, `postly --envoyer` | `docs/PRODUCTION.md` | Même MP4, empreintes, ZIP, captures réelles, texte de publication et reçu serveur |

Sur ce Mac, le guide de finition installé est [heygen:video-editing](/Users/marc./.codex/plugins/cache/openai-curated-remote/heygen/4.4.0/skills/video-editing/SKILL.md). Ce chemin dépend de la machine et de la version. Un autre agent n’a pas besoin de télécharger ce plugin pour utiliser le pipeline. Les autres skills du tableau sont des aides facultatives, et ne sont pas tous invoqués à chaque épisode. Ne pas annoncer avoir utilisé un skill ou un outil simplement parce qu’il est listé ici.

Pour l’épisode 010 : moteur local Toon Studio, guide `heygen:video-editing`, Gemini pour l’analyse audiovisuelle de la référence, ElevenLabs pour les prises, PIL/SciPy pour les mouvements et FFmpeg pour l’export. La V1 sans génération Recraft a été rejetée visuellement par Marc : économie d’API ne veut pas dire réemploi d’une maquette inadaptée. La V2 corrige les actifs manquants avec six appels Recraft ciblés, dont trois images retenues dans le montage (environ 0,225 $ selon le journal du studio), et des calques articulés locaux. Le casting principal reste réemployé ; zéro génération vidéo HeyGen. Gemini accepte au maximum 24 images/s pour cet appel d’analyse ; les 939 images natives à 30 images/s restent disponibles. Ne pas transformer cette limite en affirmation « tout analysé à 30 images/s ».

Le contrôle du MP4 inédit est resté local : décodage FFmpeg, mesures de mix, revue des images et transcription `faster-whisper` avec un modèle déjà présent sur le poste. L’envoi externe de ce livrable à Gemini a été refusé par la revue automatique et n’a pas eu lieu. Ne pas présenter une analyse externe du livrable comme réalisée. Whisper est une aide locale facultative, distincte de la synthèse ElevenLabs ; il n’est pas requis pour refaire le rendu avec les prises archivées.

## Réemploi obligatoire et enrichissement du kit

1. Lire `BIBLIOTHEQUE.yaml`, puis ouvrir les PNG et leur rig. Une entrée trouvée par son nom ne suffit pas : vérifier silhouette, teintes, yeux, échelle et points d’attache.
   Vérifier aussi le statut d’approbation. Un actif de pilote ou d’une révision rejetée ne doit pas redevenir un étalon. Pour le 010, le badge est « CACA » ; conserver les actions et les gros plans de la référence, dont la cuvette et la réaction du patient. Un personnage assis ne devient pas debout en le posant sur un autre décor.
2. Utiliser l’actif exact si sa fonction convient. Les changements de thème se font dans le scénario, les accessoires et les poses, sans recréer le casting.
3. Pour une variante, dupliquer seulement ce qui change dans le nouvel épisode : costume, bouche, bras, accessoire ou masque. Préserver les originaux. Retirer un bras de repos si un bras animé le remplace.
4. Préférer un montage de calques, une adaptation de palette contrôlée ou un rig articulé pour une variante simple. Réserver Recraft aux illustrations qui manquent réellement ; ne pas produire un personnage complet pour obtenir une main ou un marqueur.
5. Utiliser le cache et le garde de budget de `toonstudio.recraft`. Ne pas contourner le plafond. Conserver le coût réel et le nombre de nouvelles générations dans `inventaire-reemploi.json` de l’épisode. Une estimation n’est pas une facture.
6. Ajouter chaque actif réutilisable, sa provenance, son dossier et sa fonction à `BIBLIOTHEQUE.yaml`. Conserver les sources, pivots, couches et poses ; éviter un seul PNG aplati si l’objet doit être animé.
7. Promouvoir un nouvel élément au socle seulement après validation de Marc. Jusqu’alors, il reste un actif d’épisode réutilisable. Ne pas remplacer le profil verrouillé à chaque production.

## Contrôles minimaux avant livraison

- Vérifier le profil avant et après le travail. Réutiliser les prises déjà valides ; une nouvelle exportation ne doit pas relancer la génération vocale.
- Composer chaque mouvement sur le temps absolu : l’image calculée à un instant doit être identique en accès direct et en lecture séquentielle.
- Contrôler anticipation, contact, recul et sortie ; les mains et objets suivent leurs points d’attache. Conserver la synchronisation avec la bouche et les bruitages.
- Vérifier l’encodage réel, le décodage complet, la durée, les transitions, les textes à taille téléphone et les marges TikTok. Une planche ne prouve pas à elle seule la fluidité ou la qualité audio.
- Conserver le mix, la musique, les alignements et le montage. Indiquer honnêtement les passages regardés/écoutés et les outils d’analyse utilisés.
- Livrer le MP4, SRT, description et hashtags, ZIP et pièces de fabrication. Vérifier les téléchargements du studio. Une sauvegarde n’est pas une publication.

Prérequis du moteur : Python 3.12+, FFmpeg/FFprobe, `requirements.txt`, accès au registre privé des voix et aux fournisseurs seulement si des prises ou images manquent. Les clés restent hors des sources et des livraisons.
