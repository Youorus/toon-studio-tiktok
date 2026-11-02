# Direction artistique — « Ton corps, expliqué »

Validée par Marc le 2 novembre 2026, à partir de l'analyse de Dr Healthcare (@dr..healthcare1) et de ses propres retours.

## Le rendu : dessin animé rétro, lissé

- Aspect **cellulo d'un studio d'animation classique** : trait d'encre sombre net et assuré, peinture lisse en aplats,
  ombrage simple, **reflets brillants** sur les organes, très léger grain de papier.
- **Pas** d'effet crayon : ni hachures, ni traits esquissés, ni aquarelle qui coule (version « crayon » écartée par Marc).
- La consigne exacte est la clé `style` de `niches/corps-humain/kit.yaml` ; elle est ajoutée à chaque demande Recraft.

## Les couleurs

Palette relevée par Marc sur Dr Healthcare (intérieur de la bouche), imposée à Recraft pour les tissus et les gros plans :

| Rôle | Couleur |
|---|---|
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

### Pourquoi ces couleurs retiennent le pouce

- **Le rouge-rose chaud et saturé** du corps attire l'œil en premier dans un fil TikTok dominé par des vidéos filmées
  plus ternes ; c'est aussi la couleur qu'on associe à « l'intérieur du corps », donc on comprend la scène en une image.
- **Le contraste chaud / froid** : tissus chauds + touches froides (salive bleue, microbes verts, cabinet gris-bleu).
  Des couleurs opposées sur le cercle chromatique se renforcent l'une l'autre.
- **Le vert des microbes** est la couleur complémentaire du rouge des tissus : les « méchants » sautent aux yeux.
- **Le crème** (dents, reflets) donne de la lumière sans blanc pur, ce qui garde le côté rétro.
- Les **cartes** (rouge `#D45C58`) et le **mot en cours** des sous-titres (jaune `#FFD84D`) sont les seules couleurs
  « graphiques » : elles signalent l'information importante.

## Les personnages

- **Humains blancs et matures**, proportions adultes, bras dessinés dans l'image (mains dans les poches ou le long du corps).
  **Seul le visage est animé** (yeux, sourcils, bouche, tête qui penche) : c'est là qu'est l'émotion.
- **Docteure** (~55 ans, chignon châtain, chemisier marine, lunettes rondes bleu canard dessinées par le moteur) et
  **docteur** (~55 ans, barbe poivre et sel, nœud papillon moutarde). Différents de la docteure de Dr Healthcare
  (cheveux gris, chemise bordeaux) : ne pas s'en rapprocher.
- **Organes et objets** : visage du moteur, yeux ovales à paupière un peu tombante (`paupiere: .2`), petites pupilles.
  Les objets gardent leurs couleurs naturelles (métal, blanc, bleu pâle).

## Mise en scène (reprise de la recette Dr Healthcare)

1. **Dans le corps** : gros plan plein écran, les organes se disputent et vivent le problème (humour, un peu crade assumé).
2. **Au cabinet** : la docteure explique au patient, cartes de motion design pour les faits.
3. **Chute** et question pour faire commenter.
