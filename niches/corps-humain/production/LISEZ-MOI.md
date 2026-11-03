# Kit de production · Le Corps Parle.fr

**Signature** — `@lecorps.parle.fr`

Ce kit est conçu pour le studio local Toon Studio. Il réunit la charte, le modèle de script, les réglages de la niche, les calques des personnages, les décors, les badges, la photo de profil et les sons courts. Les prises de voix s’enregistrent avec les profils récurrents configurés sur le Mac.

## D’un sujet au MP4

1. Dupliquer la fiche, choisir le sujet et vérifier l’idée médicale.
2. Écrire environ 175 à 185 mots et faire relire les répliques avant l’enregistrement. Viser environ 70 secondes au total.
3. Copier le dossier du modèle sous `niches/corps-humain/episodes/<id>`. Adapter les cinq plans au sujet et remplacer chaque texte d’exemple. Le champ `dit` contient les mots prononcés. Si une direction vocale est utile, renseigner `jeu` avec l’indication entre crochets suivie de la réplique complète, comme `[vexée] Calme-toi !`. Dans `sous_titres`, une barre verticale sépare les groupes affichés.
4. Choisir les décors et les calques, puis régler les entrées, les badges et les bruitages sur les prises. Les alias `mere` et `patiente` reprennent la docteure et Léa.
5. Depuis la racine de Toon Studio, lancer la commande ci-dessous. Le moteur produit le MP4 vertical et les sous-titres SRT dans `out/`. Relire la planche de contrôle avant de publier.

```sh
.venv/bin/python -m toonstudio rendu --captionne niches/corps-humain/episodes/<id>
```

Le rendu sous-titré est disponible dans le moteur du workspace. Pour une maquette locale sans synthèse, retirer la clé `voix` du modèle. Le ZIP fournit le moteur et ses dépendances déclarées dans `requirements.txt`. Le rendu avec les voix récurrentes utilise le registre de voix et les accès ElevenLabs configurés dans l’environnement local.

## Mini-badges

Chaque entrée de `mini_badges` se rattache à un `acteur` présent dans le plan. `replique` commence à zéro. `delai` et `duree` sont en secondes. Le badge suit le point d’ancrage du personnage pendant le mouvement et le zoom. Le `decalage` sert à dégager le visage ou à séparer deux étiquettes. Sur la révélation, afficher un nouveau mini-badge du même acteur, avec la même couleur et un nouvel intitulé.

## Repères visuels

- Le fond des plans anatomiques est corail `#E75261`.
- Le badge d’organe identifie le lieu. Le mini-badge identifie un acteur à son entrée ou à sa révélation.
- le filigrane blanc glisse entre les zones dégagées. Le petit mot dans le cabinet et le bouton final gardent leur place.
- Les décors Estomac et Peau fournis vont avec leurs calques de visages dédiés. Pour un nouveau sujet, choisir un rig de la bibliothèque ou préparer un nouveau modèle Recraft dans la même charte.
