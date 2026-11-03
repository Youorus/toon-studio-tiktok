# La bactérie qui n’a pas bougé

Épisode 006 · Ton corps, expliqué · 3 novembre 2026

Adaptation française du déroulé de [What Actually Causes Antibiotic Resistance?](https://www.tiktok.com/@dr..healthcare1/video/7561844938804186390). L’ouverture suit une gélule prise pour un mal de tête. Après une éraflure, des bactéries entrent, un globule blanc tente de les contenir et un antibiotique est prescrit. Le dessin permet de voir la bactérie résistante avant le traitement, puis les cellules sensibles disparaître et les survivantes se multiplier. Le dernier plan revient au cabinet pour l’explication et l’abonnement.

Les dialogues et les dessins sont propres à Toon Studio. La docteure et Léa utilisent les silhouettes en aplats validées par Marc, les voix récurrentes et le même cabinet que dans l’épisode du spermogramme. Les bouches, les regards et les clignements sont animés sur les calques tirés des modèles approuvés.

Cette version sert de référence à la [direction artistique définitive](../../../../docs/DIRECTION-ARTISTIQUE.md). L’estomac et la peau ont des fonds accordés à leur palette et un badge anatomique. Le cabinet intègre un petit mot manuscrit « Abonne-toi » dans le cadre mural. Le placement des textes a été vérifié avec une simulation du fil vertical inspirée du [guide de cadrage TikTok](https://ads.tiktok.com/business/library/Creative_Codes_One_Pager.pdf).

## Sources médicales

- L’usage inutile d’antibiotiques favorise la sélection de bactéries résistantes. Les bactéries, et non la personne, résistent au médicament. L’épisode illustre le mécanisme par une bactérie résistante déjà présente, qui survit et se multiplie. [Organisation mondiale de la santé](https://www.who.int/news-room/fact-sheets/detail/antimicrobial-resistance)
- L’Assurance Maladie recommande l’usage sur prescription, selon la dose, le rythme et la durée prescrits, et le retour des restes en pharmacie. L’indication et le choix d’un traitement adapté dépendent de l’évaluation médicale. [Assurance Maladie](https://www.ameli.fr/medecin/sante-prevention/medicaments/antibiotiques/limiter-prescription-antibiotiques) · [OMS Europe](https://www.who.int/europe/news-room/fact-sheets/item/antimicrobial-resistance)

## Fichiers de production

- [Version TikTok courte](out/La-bacterie-qui-na-pas-bouge-TikTok.mp4) · [Sous-titres de la version courte](out/La-bacterie-qui-na-pas-bouge-TikTok.srt) · [Contrôle du rendu court](out/controle-tiktok-corail.json)
- [Épisode et texte français](episode.yaml)
- [Plan de jeu et rendu](produire.py)
- [MP4](out/La-bacterie-qui-na-pas-bouge.mp4) · [Planche du MP4](out/planche.jpg) · [Sous-titres SRT](out/sous-titres.srt) · [Contrôle final](out/controle-final.json) · [Simulation TikTok](out/controle-tiktok.jpg)

Le dossier art/ conserve les illustrations Recraft et la variante de peau. Le journal du studio attribue **0,245 $** à ces sept illustrations. Les 24 prises françaises sont en cache. Les accents sonores sont locaux.

La version TikTok applique le corail aux fonds de l’estomac et de la peau. Elle remonte les prises existantes, recale les sous-titres sur la nouvelle durée et retourne au cabinet vers 45 secondes. Son [plan de montage](out/La-bacterie-qui-na-pas-bouge-TikTok.json) conserve la correspondance entre les temps source et l’export.

Depuis la racine de Toon Studio, les commandes de préparation et de rendu sont les suivantes.

```sh
projet=niches/corps-humain/episodes/006-antibioresistance
.venv/bin/python niches/corps-humain/maquettes/casting-aplats/preparer_rigs.py
.venv/bin/python "$projet/ecrire_episode.py"
PYTHONPATH=. .venv/bin/python "$projet/preparer_art.py"
PYTHONPATH=. .venv/bin/python "$projet/produire.py"
PYTHONPATH=. .venv/bin/python "$projet/produire_tiktok.py"
```
