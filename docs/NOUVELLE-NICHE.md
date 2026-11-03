# Ajouter une nouvelle niche (ex. « Ton cerveau te ment »)

1. Copier la structure : `niches/<nouvelle-niche>/{niche.yaml,kit.yaml,personnages/,decors/,episodes/}`.
2. `niche.yaml` : nom, public, ton, format, filigrane, palette (`accent`, `legende`), `style_personnage`, `style_decor`.
3. `kit.yaml` : la consigne `style`, les `palettes` et la liste des éléments à dessiner (personnages récurrents,
   objets, décors). Faire d'abord quelques essais (`--seulement`, n=1), valider le rendu, puis tout le kit.
4. `choisir` chaque élément retenu ; vérifier les `apercu.jpg`.
5. Écrire un premier épisode court et le rendre.

Le moteur ne change pas : seules les données de la niche changent. Une niche peut réutiliser les personnages d'une autre
(chemin `perso: ../../autre-niche/personnages/docteure` relatif à la niche).

Les nouveaux comptes possèdent chacun un dossier et un épisode étalon. Conserver les fonctions partagées (calques, animation, sous-titres, rendu et archives) dans le moteur. Placer les couleurs, le casting, le ton et l’habillage dans le dossier de la niche. Le verrou actuel concerne Le Corps Parle.fr. Pour introduire un verrou sur une autre niche, définir d’abord ses propres actifs invariants et son épisode étalon. Voir la [boucle de livraison](PRODUCTION.md).
