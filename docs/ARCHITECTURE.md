# Architecture et rendu

```
episode.yaml ──► Episode (episode.py) ──► pour chaque image (30/s) :
                   minutage des répliques           décor du plan (+ caméra, transition)
                   état de chaque acteur  ──► rig.Character.render(pose, émotion, regard, clignement, bouche, effets)
                                                   couches + visage procédural (face.py) + bras (arms.py)
                   carte de la réplique   ──► cards.draw(...)
                   sous-titres, filigrane
                 ──► ffmpeg (images envoyées par tuyau, rien sur le disque) ──► mixage des bruitages ──► MP4
```

- **Tout est déterministe** : même fichier, même vidéo (clignements et phases dérivés du nom des acteurs).
- **Caches** : visages par état (`rig._FACE_CACHE`), images Recraft et Gemini (`data/cache/`).
- **Coût de rendu** : ~1 min de calcul pour 10 s de vidéo sur le Mac.
- **Pas de code tiers** : synctoon (GPL-3.0) a seulement inspiré le principe (choix d'assets par mot, visèmes) ;
  aucun code n'en est copié, le studio n'a donc pas de contrainte GPL.

## Ajouter un effet, une carte, une émotion

- Effet d'acteur : `effect()` dans `episode.py` (renvoie décalage, écrasement, inclinaison, échelle).
- Carte : une fonction dans `cards.py`, ajoutée à `TYPES`.
- Émotion : une entrée dans `EMOTIONS` (`face.py`) : paupières, sourcils, pupilles, bouche au repos.
