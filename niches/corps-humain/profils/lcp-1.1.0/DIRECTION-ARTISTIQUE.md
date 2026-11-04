# Direction artistique — Le Corps Parle.fr

## Style définitif validé par Marc le 3 novembre 2026

**Le Corps Parle.fr** · **@lecorps.parle.fr**

L’[épisode 006 révisé](../niches/corps-humain/episodes/006-antibioresistance-v3/) fixe le casting, l’action et l’habillage de la série. Le [comparatif de l’estomac](../niches/corps-humain/identite/comparatif-fond-corail.jpg) fixe la couleur de fond des scènes dans le corps. Le [fichier de niche](../niches/corps-humain/niche.yaml) fixe les modèles, les voix, le décor du cabinet, les coordonnées des badges et des sous-titres ainsi que le bouton de fin. Le profil `lcp-1.1.0` est vérifié avant livraison. Toute évolution de ce socle requiert une nouvelle validation de Marc et une nouvelle version.

Les sujets, les organes, les gags, les cadrages et les poses utiles au récit varient d’un épisode à l’autre. Le fond corail des plans anatomiques, le duo, le traitement des yeux, le cabinet, l’habillage et la structure ouverture dans le corps puis consultation font partie de la signature de la série.

## Rythme, jeu et son des prochains épisodes

- **Durée.** Viser environ 70 secondes, abonnement compris. Partir d’environ 175 à 185 mots, puis chronométrer les prises avec leurs respirations et les temps de lecture. Raccourcir les répétitions au stade du script. Laisser retomber la vanne avant de repartir.
- **Sketch.** Montrer une action dans le corps dès la première image et placer une réaction ou une vanne dans les trois premières secondes. Deux ou trois temps comiques suffisent. L’organe qui subit râle, l’autre le chambre ou se défend. Une conséquence visible relance la scène. Le comique vient du comportement, de la mauvaise foi et du décalage entre les personnages.
- **Voix.** Garder les timbres récurrents et diriger la prise par réplique. Enchaîner les réactions courtes, varier le débit à l’intérieur de l’échange et marquer une courte suspension avant la chute. La docteure ralentit légèrement sur le terme à retenir et explique une idée principale au cabinet, vers 45 secondes.
- **Bruitages.** Accrocher chaque effet au mouvement ou à la réaction qui le motive. Un petit « ploc » au contact, un « toc » sur un arrêt ou un souffle de transition suffisent souvent. Laisser de l’espace avant une vanne et contrôler au volume d’un téléphone que chaque réplique reste intelligible.

## Priorité du 3 novembre — silhouettes reconnaissables et casting original

La référence donne le niveau de finition, de lisibilité et de contraste. Les personnages de Toon Studio ont leurs propres silhouettes, proportions, visages, coiffures et accessoires. Pour un organe, on conserve les repères anatomiques nécessaires à la scène et on différencie le dessin, le cadrage et le jeu du personnage. Pour un humain, contrôler la silhouette en petit format puis la combinaison coiffure, vêtements, accessoires et mimiques en plan rapproché.

- **Forme avant visage.** À largeur téléphone, masquer les yeux et l’étiquette. L’estomac doit se lire grâce à l’arrivée du conduit, à la courbe de sa poche et à sa sortie. Dans une coupe, vérifier aussi l’emplacement de l’organe et le trajet que l’action doit montrer.
- **Couleur par rôle.** Garder de grands aplats distincts, des ombres courtes et des reflets ponctuels. Vérifier les teintes sur l’image composée à la taille finale. Le test du hoquet montre comment des hachures et de grands reflets clairs peuvent brouiller les volumes même si la palette est proche.
- **Fonds anatomiques.** Poser le corail vif `#E75261` en plein cadre, jusque dans les coins et pendant les coupes. Les creux utilisent les couleurs de tissus. Le noir sert au trait. Vérifier les coins, les bords et les grands aplats dans le décor source puis dans le MP4 pour écarter tout fond noir, zone transparente ou bande noire.
- **Création avec Recraft.** Réutiliser le casting existant quand il passe ces contrôles. Pour une forme ou une pose à reprendre, générer un modèle avec Recraft en décrivant deux ou trois repères anatomiques et les traits propres au personnage, puis préparer son animation dans Toon Studio.

## Le rendu : dessin animé rétro, lissé

- Aspect **cellulo d'un studio d'animation classique** : trait d'encre sombre net et assuré, peinture lisse en aplats,
  ombrage simple, **reflets ponctuels** aux endroits où la matière capte la lumière.
- **Pas** d'effet crayon : ni hachures, ni traits esquissés, ni aquarelle qui coule (version « crayon » écartée par Marc).
- La consigne exacte est la clé `style` de `niches/corps-humain/kit.yaml` ; elle est ajoutée à chaque demande Recraft.

## Les couleurs

Palette relevée par Marc sur Dr Healthcare (intérieur de la bouche), imposée à Recraft pour les tissus et les gros plans :

| Rôle | Couleur |
|---|---|
| Fond des plans dans le corps | `#E75261` |
| Profondeurs, intérieur de la bouche | `#6D383B` |
| Tissus rose-rouge (langue, organes) | `#B65F63` |
| Gencives, tissus clairs | `#C77779` |
| Ombres anatomiques | `#8F474B` |
| Dents, reflets crème | `#FFF9ED` |
| Contours | `#181313` |
| Microbes verts / ombres vertes | `#5BDD79` / `#31B958` |
| Microbes rouges | `#D45C58` |
| Salive, liquides | `#91D3DF` |

Le cabinet reste **gris-bleu éteint** (`#B3C2CC`, `#E5E6E6`, sol `#6D5F5A`) : un fond calme fait ressortir les personnages,
comme chez Dr Healthcare.

### Le rouge dans les plans anatomiques

Le corail vif `#E75261` occupe l’arrière-plan. Le bordeaux `#6D383B` sert aux creux, les tons roses plus clairs aux reliefs et le trait sombre `#181313` aux silhouettes. Contrôler la séparation de l’organe, des yeux et de l’action dès la première image à taille téléphone. Le rouge vif peut orienter le regard selon la scène. L’effet sur la durée de visionnage se mesure sur les épisodes. [Étude expérimentale sur le rouge et l’attention](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2015.00212/full)

- **Le contraste chaud / froid** : tissus chauds + touches froides (salive bleue, microbes verts, cabinet gris-bleu).
  Des couleurs opposées sur le cercle chromatique se renforcent l'une l'autre.
- **Le vert des microbes** est la couleur complémentaire du rouge des tissus : les « méchants » sautent aux yeux.
- **Le crème** (dents, reflets) donne de la lumière sans blanc pur, ce qui garde le côté rétro.
- Les **cartes** (rouge `#D45C58`) et le **mot en cours** des sous-titres (jaune `#FFD84D`) sont les seules couleurs
  « graphiques » : elles signalent l'information importante.

## Les personnages

- **Casting récurrent, validé par Marc le 3 novembre.** La [planche validée](../niches/corps-humain/maquettes/casting-aplats/casting.jpg) fixe les deux modèles visuels. La [docteure](../niches/corps-humain/maquettes/casting-aplats/docteure.png) garde son chignon bouclé auburn, sa blouse crème et son haut bleu pétrole. [Léa](../niches/corps-humain/maquettes/casting-aplats/lea.png) garde son carré bouclé, son pull terracotta et son pantalon prune. Réutiliser les rigs [docteure-aplats](../niches/corps-humain/personnages/docteure-aplats/personnage.yaml) et [lea-aplats](../niches/corps-humain/personnages/lea-aplats/personnage.yaml). Pour les nouvelles poses et expressions, partir de ces modèles et conserver leurs proportions et couleurs.
- **Voix et cabinet.** Réutiliser les voix récurrentes et le [cabinet avec le petit « Abonne-toi » dans le cadre mural](../niches/corps-humain/decors/cabinet-abonne-toi.png), dérivé du décor de l’épisode 004. Réserver les nouveaux décors et accessoires aux besoins du sujet.
- **Humains minimalistes.** Une silhouette lisible, un trait sombre régulier, des aplats, une ombre simple. Jouer les regards, les paupières et les pauses avec peu de détails. Préparer quelques mains et postures utiles au sketch.
- **Organes et objets** : visage du moteur, yeux ovales à paupière un peu tombante (`paupiere: .2`), petites pupilles.
  Les objets gardent leurs couleurs naturelles (métal, blanc, bleu pâle).

## Mise en scène (reprise de la recette Dr Healthcare)

1. **Première image dans le corps.** Un organe joue ou réagit dès l’ouverture et prend la parole en premier. La situation du quotidien peut s’entendre depuis l’intérieur avant d’être montrée. Prévoir un gag visible, lisible son coupé.
2. **Dernière scène au cabinet.** La docteure explique ce que les organes ont vécu et ce qui se passe ensuite. Le patient peut relancer ou jouer la chute dans le même plan. La docteure conclut et porte l’invitation à s’abonner, à l’oral et à l’écran.
3. **Repères de lecture.** Renseigner `organe` sur les plans anatomiques rendus par `CaptionedEpisode` pour afficher le cartouche en haut à gauche, en retrait des bords. Vérifier le cartouche, les sous-titres et le bouton final à taille téléphone avec les marges de l’interface TikTok.
4. **Signature de la chaîne.** Afficher « Le Corps Parle.fr » en petits caractères blancs semi-transparents, directement sur l’image. Le filigrane change de zone en glissant doucement entre les côtés et les hauteurs du cadre. Privilégier les zones dégagées des visages, de l’action, des badges et des sous-titres. Garder `@lecorps.parle.fr` dans la description.
5. **Identification.** Donner aux nouveaux personnages un mini-badge mobile lié à leur silhouette, le temps d’une lecture. Garder au plus deux mini-badges visibles en plus du badge d’organe. Conserver le même code couleur lors d’un changement d’intitulé.
6. **Sous-titres.** Le mode `mot_capitales` affiche un mot à la fois, sur les repères de la prise, en Luckiest Guy blanc cassé avec une ombre noire courte. Le texte est centré bas dans l’image. Garder un SRT en phrases pour la relecture et l’accessibilité.
7. **Clin d’œil du cabinet.** Le premier cadre mural porte le petit « Abonne-toi ». Mettre dans le deuxième cadre un conseil manuscrit court, exact et lié au sujet, avec le ton de la chaîne. Le placer dans une copie du décor propre à l’épisode et vérifier sa lecture à taille téléphone.
8. **Travail à partir d’une référence.** Relever la fonction de chaque réplique, l’ordre des actions, les réactions, les accélérations et les respirations. Recréer ces fonctions dans notre univers, avec des dialogues français et des gags écrits pour l’épisode, nos calques et nos pistes sonores. Conserver les repères et la provenance des éléments utilisés.
9. **Musique.** Utiliser la version à 125 BPM de « Petites combines » comme signature musicale de la série. La même composition originale accompagne chaque épisode, avec des creux sur les répliques et les impacts. Archiver la composition et le mix.

## Modèle des scripts

1. **Ouverture dans l’organe.** Action dès la première image, identité de l’élément entrant et première réaction en trois secondes.
2. **Conflit.** Un second élément débarque, l’organe râle et l’autre le chambre. Faire avancer la situation en quelques répliques.
3. **Relance.** Retour d’un élément déjà identifié ou arrivée d’une nouvelle contrainte.
4. **Conséquence.** La montrer dans le corps, puis laisser une réplique ou un bruitage ponctuer la chute.
5. **Consultation.** Une question courte, une explication vérifiée, la suite et l’abonnement face caméra.

La [fiche à dupliquer](../niches/corps-humain/production/fiche-episode.md) sépare les paroles, le jeu, les badges et les bruitages. Le [mode d’emploi](../niches/corps-humain/production/LISEZ-MOI.md) accompagne le modèle de rendu.
