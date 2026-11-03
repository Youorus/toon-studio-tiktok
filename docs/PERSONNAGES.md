# Personnages : format `personnage.yaml`

Chaque personnage est un dossier `niches/<niche>/personnages/<nom>/` : images PNG transparentes + `personnage.yaml`
+ `apercu.jpg` (planche des 13 émotions, régénérée par `python -m toonstudio apercu <dossier>`).

`choisir … --type organe|humain` crée tout automatiquement (détourage, repères, aperçu). Vérifier l'aperçu, puis ajuster.

```yaml
nom: Docteure
type: humain                 # humain | organe
echelle: 1.0                 # taille par défaut à l'écran (multipliée par celle de l'épisode)
couches:                     # ordre de dessin ; la première est la racine
  - id: corps
    images: {defaut: corps.png}      # plusieurs variantes possibles : {defaut: a.png, assis: b.png}
    pivot: [309, 1100]               # point au sol (bas-centre), en pixels de l'image
  # - id: chapeau, parent: corps, attache: [x, y], pivot: [x, y], images: {...}, z: 2
decoupe_tete: {y: 259, cou: [287, 257]}   # humain : la tête est découpée au cou pour pencher
visage:
  couche: tete               # la couche où dessiner le visage (corps pour un organe)
  yeux: [287, 177]           # milieu entre les deux yeux
  rayon_oeil: 19
  ecart: 2.15                # écart des yeux, en rayons (2 = ils se touchent)
  bouche: [287, 210]
  largeur_bouche: 40
  peau: '#F1C7A6'            # couleur des paupières = couleur de la peau autour
  forme_oeil: 1.15           # hauteur / largeur de l'œil
  paupiere: .2               # paupière toujours un peu tombante (regard blasé des organes)
  pupille: .85               # taille des pupilles
  lunettes: '#1F7A80'        # optionnel : lunettes rondes dessinées
  cils: true                 # optionnel
  sourcils: true
mouvement: {souplesse: .15, respiration: .008}   # organes : souplesse 1 (squash & stretch marqué)
# bras: optionnel, bras dessinés par le moteur (épaule, coude, 6 mains) — non utilisés dans cette niche
poses: {defaut: {}}
```

## Émotions disponibles

neutre, content, rire, choque, triste, inquiet, fache, fatigue, gene, degoute, douleur, malicieux, amoureux.
Bouches de parole (visèmes) : A, E, O, M, F, repos — choisies automatiquement depuis le texte.

## Flagelle animé

Un personnage à flagelle peut déclarer un point d’attache en pixels sur son calque racine. Le moteur l’anime derrière le corps et suit la rotation du personnage. La longueur et l’amplitude sont en pixels, la fréquence en cycles par seconde et l’angle en degrés dans le repère image.

```yaml
flagelle: {attache: [25, 80], longueur: 220, amplitude: 40, angle: 160, frequence: 3, couleur: '#91D3DF', epaisseur: 14}
```
