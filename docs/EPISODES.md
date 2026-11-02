# Épisodes : format `episode.yaml`

Un épisode = `niches/<niche>/episodes/<id>/episode.yaml`. Rendu : `python -m toonstudio rendu <dossier>` →
`out/<id>.mp4` (1080×1920, 30 i/s, H.264 CRF 16, AAC).

```yaml
titre: Pourquoi on a le hoquet ?
niche: corps-humain
duree_cible: 62                 # optionnel : étire/resserre le minutage (monétisation TikTok : 61-65 s)
plans:
  - id: dans-le-thorax
    decor: decors/gros-plan-thorax.png
    zoom: [1.0, 1.05]           # travelling avant sur le plan
    acteurs:
      diaphragme: {perso: personnages/diaphragme, x: 540, y: 1540, echelle: 1.05}   # x, y = point au sol
    repliques:
      - qui: diaphragme
        dit: "HIC !"
        emotion: choque
        reactions: {poumons: choque}       # émotion des autres pendant la réplique
        effets: {diaphragme: hic}          # hic | saut | tremble | gonfle | apparait | rot
        effet_delai: 0.5                   # optionnel
        carte: {type: choc, texte: "HIC !"}
        sfx: [boing]                       # optionnel (sinon bruitages automatiques)
        duree: 1.4                         # optionnel (sinon temps de lecture)
```

## Cartes de motion design

| type | champs |
|---|---|
| `choc` | `texte`, `fond` |
| `chiffre` | `valeur` (nombre qui compte ou texte), `unite`, `legende`, `couleur` |
| `liste` | `titre`, `lignes: [[texte, ok\|non\|attention], …]` |
| `alerte` | `texte` (`\n` pour aller à la ligne) |
| `image` | `fichier`, `legende` |
| `bouton` | `texte`, `couleur` |
| `vote` | `question`, `oui`, `non` |

Options communes : `position: haut|centre|bas`, `garde: true` (reste affichée aux répliques suivantes).

## Voix (prochaine étape)

Sans voix, chaque réplique dure le temps de la lire et la bouche suit les lettres. Quand la voix ElevenLabs sera
branchée, le minutage mot à mot remplacera ce calcul (même principe que `scripts/blender-voices.ts` du studio Dr Mia).

## Règles éditoriales

- Faits vérifiés sur des sources médicales (MSD Manuals, sante.fr, Ameli, NHS), sources notées en tête du fichier.
- Jamais de conseil dangereux ; « consulte si… » quand c'est utile.
