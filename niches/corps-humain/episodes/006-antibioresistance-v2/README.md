# La bactérie qui n’a pas bougé · Le Corps Parle.fr

Épisode 006, seconde production. Le [script court](../006-antibioresistance/relecture/script-006-tiktok-court-proposition.md) donne les répliques. Le rendu utilise les décors corail, le casting récurrent et la signature mobile `@lecorps.parle.fr`.

Les 19 prises françaises sont dirigées séparément et gardent leur débit d’enregistrement. Le montage réduit des silences de bord pour atteindre environ 70 secondes. Les badges suivent les personnages. Leurs apparitions et les bruitages sont calés sur les mouvements ou les mots mesurés des prises.

## Export

- [Version avec musique de fond](out/La-bacterie-qui-na-pas-bouge-Le-Corps-Parle-Avec-Musique.mp4)
- [Master vertical MP4](out/La-bacterie-qui-na-pas-bouge-Le-Corps-Parle.mp4)
- [Sous-titres SRT](out/sous-titres.srt)
- [Plan du montage](out/montage.json) et [contrôle du fichier](out/controle.json)

Depuis la racine de Toon Studio, reproduire l’export à partir du cache avec les commandes ci-dessous. Le drapeau `--voix` de `preparer.py` demande les prises manquantes au service de voix configuré.

```sh
projet=niches/corps-humain/episodes/006-antibioresistance-v2
PYTHONPATH=. .venv/bin/python "$projet/preparer.py"
PYTHONPATH=. .venv/bin/python "$projet/produire.py"
.venv/bin/python "$projet/mixer_musique.py"
```

Le mix musical ajoute une composition instrumentale originale continue. Le niveau du fond baisse pendant les répliques et le PLOUF. Le MP4 conserve le flux vidéo du master. [Contrôle du mix](out/controle-mix-musical.json)

Le propos sur la résistance, la sélection et l’usage des antibiotiques repose sur les sources de l’épisode de référence. [Assurance Maladie](https://www.ameli.fr/assure/sante/medicaments/utiliser-recycler-medicaments/bien-utiliser-les-antibiotiques/antibiotiques-et-antibioresistance) · [OMS](https://www.who.int/news-room/fact-sheets/detail/antimicrobial-resistance)
