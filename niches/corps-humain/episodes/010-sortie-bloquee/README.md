# La sortie est bloquée — épisode 010, V2

Révision demandée par Marc : badge **CACA**, silhouettes et couleurs reprises, marche et contacts, glissement dans une coupe courbe, vrai gros plan du CACA et du sang dans la cuvette, puis Léa debout. La tête de Léa, le policier comique, la docteure et le cabinet approuvés sont conservés. Profil `lcp-1.2.0`, signature `@lecorps.parle.fr`, environ **48,26 secondes**.

La V1 a été rejetée visuellement. Son MP4 et son archive restent historiques ; ne pas la prendre pour étalon. Le nouveau master est le fichier **V2** ci-dessous. L’approbation du socle ne vaut pas validation automatique de tous les dessins d’un épisode.

- [MP4 V2](out/La-sortie-est-bloquee-Le-Corps-Parle-V2.mp4)
- [Sous-titres SRT](out/sous-titres.srt)
- [Scénario français](SCRIPT.md)
- [Dialogues et directions de jeu](dialogues.py)
- [Provenance et choix de la révision](provenance.md)
- [Inventaire, réemploi et dépenses estimées](inventaire-reemploi.json)
- [Description et hashtags](publication-tiktok.txt)
- [Guide des workflows et skills](../../../../docs/WORKFLOWS-ET-SKILLS.md)

## Refaire la V2

Depuis Toon Studio, les dessins sont déjà présents et les voix en cache. Dans le ZIP, définir `TOON_PRISES_INDEX` vers `prises/index.json`. Aucune nouvelle génération d’image n’est nécessaire pour refaire cette livraison.

```sh
p=niches/corps-humain/episodes/010-sortie-bloquee
PYTHONPATH=. python "$p/preparer.py"
PYTHONPATH=. python "$p/produire.py" --apercu
PYTHONPATH=. python "$p/produire.py"
PYTHONPATH=. python -m toonstudio.musique_cartoon --image "$p/out/image-et-voix-V2.mp4" \
  --son "$p/out/image-et-voix-V2.mp4" --sous-titres "$p/out/sous-titres.json" \
  --montage "$p/out/montage.json" --sortie "$p/out/La-sortie-est-bloquee-Le-Corps-Parle-V2.mp4"
PYTHONPATH=. python "$p/controler.py"
```

`preparer.py` et `produire.py` sont les entrées courantes et appellent la V2. `--remixer-audio` réutilise les images déjà encodées lorsque seuls les sons ont changé. Ne pas lancer les copies historiques de `revisions/v1/` hors de leur archive d’origine.

Les six appels Recraft de la révision ont coûté environ 0,225 $ selon le journal du client ; trois illustrations ont été retenues, les autres essais écartés. Les nouveaux calques, la pose debout, la coupe, le trajet et le gros plan restent réutilisables. La glissade sonore prolonge un son de notre bibliothèque sans appel fournisseur.

Pour l’archive, déclarer `006-antibioresistance` et `006-antibioresistance-v3` comme dépendances. Les preuves doivent correspondre au master V2 exact. Le transfert dans Studio n’est pas une publication TikTok.
