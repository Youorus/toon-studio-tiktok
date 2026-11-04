# La sortie est bloquée — épisode 010

Adaptation de la référence du **23 septembre 2025** avec le profil `lcp-1.2.0` et la signature `@lecorps.parle.fr`. Durée sur les prises : **46,3 secondes**. Le gardien et la selle sont réemployés ; aucun appel Recraft. Conclusion avec Léa et notre docteure.

- [Dialogues et directions de jeu](dialogues.py)
- [Provenance et examen de la référence](provenance.md)
- [Fiche éditoriale](fiche-editoriale.md)
- [Inventaire du réemploi](inventaire-reemploi.json)
- [Description et hashtags](publication-tiktok.txt)
- [MP4](out/La-sortie-est-bloquee-Le-Corps-Parle.mp4)
- [Sous-titres SRT](out/sous-titres.srt)
- [Guide commun des workflows et skills](../../../../docs/WORKFLOWS-ET-SKILLS.md)
- [Planning éditorial de la chaîne](../../../../docs/PLANNING-EDITORIAL.md)

Depuis Toon Studio, les prises sont mises en cache. Dans le ZIP, configurer `TOON_PRISES_INDEX` vers `prises/index.json` pour les réutiliser sans nouvel appel.

```sh
p=niches/corps-humain/episodes/010-sortie-bloquee
PYTHONPATH=. python "$p/preparer.py"
PYTHONPATH=. python "$p/produire.py" --apercu
PYTHONPATH=. python "$p/produire.py"
PYTHONPATH=. python -m toonstudio.musique_cartoon --image "$p/out/image-et-voix.mp4" \
  --son "$p/out/image-et-voix.mp4" --sous-titres "$p/out/sous-titres.json" \
  --montage "$p/out/montage.json" --sortie "$p/out/La-sortie-est-bloquee-Le-Corps-Parle.mp4"
```

Pour l’archive, déclarer les dépendances `005-caca-demission`, `006-antibioresistance` et `006-antibioresistance-v3`. Le ZIP conserve les actifs et le code de cette livraison ; le fichier d’inspiration reste dans sa bibliothèque séparée. Le transfert dans Studio n’est pas une publication TikTok.
