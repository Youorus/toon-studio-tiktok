# Toon Studio

Studio de production de vidéos TikTok en **animation 2D à couches** : des personnages et des organes attachants qui
vivent une situation drôle, puis un personnage expert qui explique. Une **niche** = un univers (personnages, décors,
couleurs, ton). Première niche **Le Corps Parle.fr** (`niches/corps-humain`).

| Brique | Rôle |
|---|---|
| **Recraft** (API) | Dessine les personnages, organes, objets et décors dans un **style maison** constant (budget plafonné) |
| **Gemini Image** | Décors et images de test (marquage IA SynthID) |
| **Moteur maison** (`toonstudio/`) | Anime : visages (13 émotions, regard, clignements, bouche qui parle), bras articulés dessinés, tête qui penche, squash & stretch, effets, caméra, cartes de motion design, sous-titres, bruitages |
| **Écriture** | Scripts, sources, intentions des répliques et plans de montage versionnés par épisode |
| **ElevenLabs** | Prises récurrentes et alignements pour les visèmes et sous-titres |

## Démarrer

```bash
git clone https://github.com/Youorus/toon-studio-tiktok.git
cd toon-studio-tiktok
uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python -r requirements.txt
cp .env.example .env            # puis y mettre RECRAFT_API_TOKEN=...
.venv/bin/python -m toonstudio rendu niches/corps-humain/episodes/001-hoquet
```

La vidéo sort dans `niches/corps-humain/episodes/001-hoquet/out/`. Les rendus utilisent FFmpeg et FFprobe. Pour de nouvelles prises, fournir la clé ElevenLabs et le registre des voix. Pour rejouer un épisode archivé, fournir `TOON_PRISES_INDEX` depuis son ZIP privé.

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

- [Passation à Codex, Claude ou Gemini](README-PASSATION.md)
- [Produire, verrouiller et archiver un épisode](docs/PRODUCTION.md)
- [Architecture et rendu](docs/ARCHITECTURE.md)
- [Direction artistique et couleurs](docs/DIRECTION-ARTISTIQUE.md)
- [Recraft : budget et procédure](docs/RECRAFT.md)
- [Personnages : format personnage.yaml](docs/PERSONNAGES.md)
- [Épisodes : format episode.yaml](docs/EPISODES.md)
- [Ajouter une nouvelle niche](docs/NOUVELLE-NICHE.md)

## Le Corps Parle.fr

- [Profil visuel et sonore lcp-1.1.0](niches/corps-humain/profil-verrou.json)
- [Épisode étalon 006 · La bactérie qui n’a pas bougé](niches/corps-humain/episodes/006-antibioresistance-v3/)
- [Épisode 007 · Le colis surprise du placenta](niches/corps-humain/episodes/007-alcool-grossesse/)
- [Épisode 008 · Estomac en surcharge](niches/corps-humain/episodes/008-estomac-sature/)
- [Épisode 009 · Le buffet de la langue](niches/corps-humain/episodes/009-buffet-de-la-langue/)
- [Bibliothèque d’éléments réutilisables](niches/corps-humain/BIBLIOTHEQUE.yaml)
- [Exemple de scénario original · Le tympan a quitté le groupe](niches/corps-humain/scenarios/exemple-le-tympan-a-quitte-le-groupe.md)

Le code et les actifs studio sont versionnés. Les masters, les prises enregistrées et les archives de production sont conservés à part, avec leurs empreintes. Une nouvelle niche peut partir du même moteur avec son propre casting, ses décors et ses réglages.
