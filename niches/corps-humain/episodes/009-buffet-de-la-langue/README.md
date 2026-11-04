# Le buffet de la langue

Épisode 009 de Le Corps Parle.fr. Le cerveau rose de la bibliothèque se réveille, les bactéries profitent des résidus sur la langue, puis la réaction se joue au petit-déjeuner. La docteure termine avec l’explication du phénomène et le conseil. Dans le deuxième cadre, « Dents et langue, tout doux. Chaque jour. »

- [Texte français et intentions](dialogues.py)
- [Provenance et découpage de la référence](provenance.md)
- [Livraison MP4](out/Le-buffet-de-la-langue-Le-Corps-Parle-V3.mp4)
- [Description et hashtags prêts à publier](publication-tiktok.txt)
- [Inventaire de la série](../../BIBLIOTHEQUE.yaml)

## Refaire le rendu

Depuis Toon Studio ou depuis un ZIP décompressé. Pour le ZIP, définir `TOON_PRISES_INDEX="$PWD/prises/index.json"`.

```sh
p=niches/corps-humain/episodes/009-buffet-de-la-langue
o="$p/out"
PYTHONPATH=. python "$p/preparer.py"
PYTHONPATH=. python "$p/produire.py"
PYTHONPATH=. python -m toonstudio.musique_cartoon --image "$o/image-et-voix.mp4" \
  --son "$o/image-et-voix.mp4" --sous-titres "$o/sous-titres.json" \
  --montage "$o/montage.json" --sortie "$o/Le-buffet-de-la-langue-Le-Corps-Parle-V3.mp4"
```

Dépendances d’actifs et de sons dans les épisodes 006 et 006-v3. Le cerveau rose détaillé vient du rig commun personnages/cerveau. Consulter les actifs existants avant de lancer `illustrer.py`. Le décor de bouche et l’assiette sont conservés. `costumes.py` prépare le corps de Léa sans doublon de bras et harmonise la peau de l’ami. `geste_lea.py` anime un bras continu avec une main pleine devant le nez, composé derrière la table. Les mains de repos sont cachées par le plateau. Le tableau du petit-déjeuner porte « Le café réveille. Ton haleine aussi. »
