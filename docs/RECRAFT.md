# Recraft : budget et procédure

## Tarifs (relevés le 2/11/2026 — https://www.recraft.ai/docs/api-reference/pricing)

1 $ = 1 000 unités API, sans expiration. Image matricielle V4.1 : **0,035 $** ; vectorielle : 0,08 $ ;
création de style : 0,005 $ ; détourage / vectorisation : 0,01 $.

## Garde-fous du studio (`toonstudio/recraft.py`)

- **Plafond** : `RECRAFT_BUDGET_USD` dans `.env` (10 $ = le solde du compte de Marc le 2/11/2026). Tout appel qui le
  dépasserait est refusé.
- **Journal** : `data/recraft-depenses.jsonl`, une ligne par appel payé. `python -m toonstudio budget --compte` compare
  avec le solde réel.
- **Cache** : une demande identique n'est jamais payée deux fois (`data/cache/recraft`).
- **Délai dépassé** : Recraft facture même si la réponse n'arrive pas ; le studio note alors la dépense (« image perdue »).
- **Estimation d'abord** : `kit … ` sans `--lancer` affiche seulement la liste et le prix.

## Procédure

```bash
.venv/bin/python -m toonstudio kit corps-humain elements                     # estimation
.venv/bin/python -m toonstudio kit corps-humain elements --seulement foie --lancer
.venv/bin/python -m toonstudio choisir corps-humain niches/corps-humain/recraft/elements/foie.png foie --type organe
```

Pour un nouvel élément : l'ajouter à `kit.yaml` (`type` organe | humain | decor, `couleurs: tissus` pour les tissus),
le générer avec `--seulement`, puis `choisir`.

## Leçons du premier kit (2/11/2026, 7,59 $ au total)

- Un **style Recraft enregistré** à partir d'organes teinte tout ce qu'il touche : la peau des humains et les instruments
  devenaient rouges. Le kit v3 n'utilise donc **pas** de style enregistré : consigne `style` + palette imposée.
- Le filtre de Recraft **bloque comme références de style** les gros plans « chair » (intérieur de l'estomac).
- La **palette imposée** (`controls.colors`) change tout : c'est elle qui donne la vivacité voulue.
- Le vert des microbes, imposé à une bouche, peut couler sur les gencives : donner aux gros plans la palette `tissus`
  et générer les microbes à part.
- Diaphragme : Recraft dessine des lèvres ; l'image retenue est un bol **retourné** (`diaphragme-retourne.png`).
