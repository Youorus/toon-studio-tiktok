# Le colis surprise du placenta

Épisode 007 de Le Corps Parle.fr. L’utérus ouvre l’action, le placenta et le fœtus jouent le passage de l’alcool, puis la docteure répond à Léa. Le deuxième cadre du cabinet indique « Un doute ? Parles-en sans filtre. »

- [Script et direction des voix](dialogues.py)
- [Provenance et relevé de la référence](provenance.md)
- [Livraison révisée](out/Le-colis-surprise-du-placenta-Le-Corps-Parle-V2.mp4)
- [Description et hashtags prêts à publier](publication-tiktok.txt)

## Reproduire depuis les sources

```sh
# Pour une archive hors ligne, depuis le dossier extrait
export TOON_PRISES_INDEX="$PWD/prises/index.json"
p=niches/corps-humain/episodes/007-alcool-grossesse
o="$p/out"
PYTHONPATH=. python "$p/preparer.py"
PYTHONPATH=. python "$p/produire.py"
PYTHONPATH=. python -m toonstudio.musique_cartoon --image "$o/image-et-voix.mp4" \
  --son "$o/image-et-voix.mp4" --sous-titres "$o/sous-titres.json" \
  --montage "$o/montage.json" --sortie "$o/Le-colis-surprise-du-placenta-Le-Corps-Parle-V2.mp4"
```
