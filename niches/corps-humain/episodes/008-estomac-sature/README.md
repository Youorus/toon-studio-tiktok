# Estomac en surcharge

Épisode 008 de Le Corps Parle.fr. L’estomac attaque son burger, les arrivages et le soda le débordent, puis il appelle le cerveau. Léa finit au cabinet avec le sac de repas. Sa corpulence a été adaptée à la demande de Marc dans un rig propre à cet épisode. Le deuxième cadre affiche « Pose tes couverts. Écoute ton ventre. »

- [Répliques françaises et direction des voix](dialogues.py)
- [Provenance et relevé des scènes](provenance.md)
- [MP4 livré](out/Estomac-en-surcharge-Le-Corps-Parle.mp4)
- [Description et hashtags prêts à publier](publication-tiktok.txt)

## Refaire le rendu

Exécuter depuis Toon Studio. Depuis un ZIP décompressé, définir `TOON_PRISES_INDEX="$PWD/prises/index.json"` pour reprendre les prises sans synthèse.

```sh
p=niches/corps-humain/episodes/008-estomac-sature
o="$p/out"
PYTHONPATH=. python "$p/preparer.py"
PYTHONPATH=. python "$p/produire.py"
PYTHONPATH=. python -m toonstudio.musique_cartoon --image "$o/image-et-voix.mp4" \
  --son "$o/image-et-voix.mp4" --sous-titres "$o/sous-titres.json" \
  --montage "$o/montage.json" --sortie "$o/Estomac-en-surcharge-Le-Corps-Parle.mp4"
```

Réutilise les calques et bruitages des dossiers 006, 006-v2 et 006-v3. Les dessins supplémentaires sont sous `art/`. Les prises et leurs alignements sont dans l’archive privée.
