# Toon Studio

Studio de production de vidéos TikTok en **animation 2D à couches** : des personnages et des organes attachants qui
vivent une situation drôle, puis un personnage expert qui explique. Une **niche** = un univers (personnages, décors,
couleurs, ton). Première niche : **« Ton corps, expliqué »** (`niches/corps-humain`).

| Brique | Rôle |
|---|---|
| **Recraft** (API) | Dessine les personnages, organes, objets et décors dans un **style maison** constant (budget plafonné) |
| **Gemini Image** | Décors et images de test (marquage IA SynthID) |
| **Moteur maison** (`toonstudio/`) | Anime : visages (13 émotions, regard, clignements, bouche qui parle), bras articulés dessinés, tête qui penche, squash & stretch, effets, caméra, cartes de motion design, sous-titres, bruitages |
| **Claude** | Écrit les épisodes (`episode.yaml`) et vérifie les faits |
| ElevenLabs (plus tard) | Voix ; le moteur synchronisera les bouches sur l'audio |

## Démarrer

```bash
cd ~/Documents/ChatGPT/postly/toon-studio
uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python -r requirements.txt
cp .env.example .env            # puis y mettre RECRAFT_API_TOKEN=...
.venv/bin/python -m toonstudio rendu niches/corps-humain/episodes/001-hoquet
```

La vidéo sort dans `niches/corps-humain/episodes/001-hoquet/out/`.

## Commandes

| Commande | Effet |
|---|---|
| `budget [--compte]` | Dépenses Recraft (journal `data/recraft-depenses.jsonl`) |
| `kit <niche> references [--lancer]` | Essais de style Recraft (prix affiché d'abord, rien n'est payé sans `--lancer`) |
| `style <niche> <images…>` | Enregistre le style maison et l'écrit dans `niche.yaml` |
| `kit <niche> elements [--seulement nom…] [--lancer]` | Génère personnages, organes, objets, gros plans dans le style maison |
| `choisir <niche> <candidat.png> <nom> --type organe\|humain\|decor` | Installe un candidat : détourage, `personnage.yaml`, planche d'aperçu |
| `organe <niche> <nom> "<description>" [--source gemini]` | Crée directement un organe animable |
| `decor <niche> <nom> "<description>"` | Décor par Gemini |
| `apercu <dossier personnage>` | Planche des 13 émotions pour vérifier le placement du visage |
| `rendu <dossier épisode>` | Rend l'épisode en MP4 1080×1920 |

## Organisation

```
toonstudio/          le moteur (Python)
  config.py            chemins, format, lecture des clés
  recraft.py           client Recraft : cache, plafond de budget, journal des dépenses
  gemini.py            décors Gemini (cache)
  face.py              visage procédural : yeux, paupières, sourcils, lunettes, bouches, visèmes
  arms.py              bras dessinés : épaule, coude, 6 formes de main
  rig.py               personnage en couches (personnage.yaml) et son rendu image par image
  cards.py             cartes de motion design (choc, chiffre, liste, alerte, image, bouton, vote)
  episode.py           minutage, acteurs, effets, caméra, transitions, sous-titres, mixage
  __main__.py          ligne de commande
niches/<niche>/
  niche.yaml           ton, format, palette, style des prompts, style_id Recraft
  kit.yaml             la commande Recraft de l'identité visuelle
  personnages/<nom>/   personnage.yaml + images (+ apercu.jpg)
  decors/              décors 1080×1920
  episodes/<id>/       episode.yaml (+ out/ : vidéos rendues, non versionnées)
shared/fonts, shared/sfx   polices et bruitages communs
docs/                guides détaillés (voir ci-dessous)
data/                journal des dépenses ; cache/ (non versionné)
```

## Guides

- [Architecture et rendu](docs/ARCHITECTURE.md)
- [Direction artistique et couleurs](docs/DIRECTION-ARTISTIQUE.md)
- [Recraft : budget et procédure](docs/RECRAFT.md)
- [Personnages : format personnage.yaml](docs/PERSONNAGES.md)
- [Épisodes : format episode.yaml](docs/EPISODES.md)
- [Ajouter une nouvelle niche](docs/NOUVELLE-NICHE.md)

## État au 2 novembre 2026

- **Kit visuel v3 validé par Marc** (rendu rétro « cellulo » lissé, palette vive) : 4 humains, 24 organes / objets /
  microbes, 6 décors, installés et animables. Coût Recraft total : 7,59 $ (journal `data/recraft-depenses.jsonl`).
- Épisode test `001-hoquet` (62 s, sans voix) rendu avec ce kit.
- Voix : pas encore branchée (aucun crédit ElevenLabs dépensé).
