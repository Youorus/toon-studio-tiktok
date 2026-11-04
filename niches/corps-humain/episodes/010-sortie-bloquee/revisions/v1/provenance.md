# Provenance — La sortie est bloquée

## Référence fournie par Marc

- Dossier : `2025-09-23`.
- Identifiant de catalogue : `r-1145439917a7702636986ce2`.
- ID de vidéo : `7553267300753870102`.
- Original : `2025-09-23_7553267300753870102_This Is What Happens If You Don’t Poop for Days .mp4`.
- SHA-256 : `dc7d7df9cf3dcc8c5dcf70f9d8b127baeaaa1c94f2530ad6e0524bad28c15fa2`.
- Source technique : 31,3 s, 1072×1920, 30 images/s, 939 images. Copie conservée dans la bibliothèque privée des inspirations ; pas dans les pièces présentées comme nos propres dessins.
- Analyse locale : `niches/corps-humain/references/analyses/r-1145439917a7702636986ce2/`.

## Examen réellement effectué

Extraction des 939 images natives et des horodatages, de l’audio WAV et des deux planches d’ensemble, examinées sur toute la chronologie. Revue supplémentaire des images successives à 0,1 s d’intervalle autour de la poussée (6,7–7,6 s), de la sortie du marqueur et de son contact (17,4–18,9 s), puis de la libération (20,6–22,3 s). Gemini 2.5 Flash a reçu la vidéo entière et son audio avec un échantillonnage demandé à 24 images/s, limite de cet appel. Sa transcription et son analyse sont conservées dans `reference-analyse.json`. Elles complètent la revue des images ; elles ne constituent pas une affirmation de lecture humaine de chacune des 939 images ou d’écoute directe par l’agent principal.

| Temps source | Construction conservée | Mise en scène dans notre univers |
|---|---|---|
| 0–4 s | La selle demande à sortir, ouverture de la porte | Corps issu du 005, gardien issu du 006-v3, porte articulée et cartouche « Rectum » |
| 4–7 s | La selle se coince et appelle à l’aide | Approche, contact avec arrêt et recul ; mains liées aux acteurs, bruit sur le contact |
| 7–13 s | Poussée infructueuse et constat de dureté | Gardien qui se penche et pousse ; « dur comme du béton », puis « séché sur place » |
| 14–20 s | Marqueur rouge et signe d’alerte | Marqueur animé au poignet ; traces courtes fixées à la selle. Métaphore comique, aucun mécanisme médical intentionnel attribué au corps |
| 20–22 s | Dernière poussée et passage | Anticipation, contact, trajectoire commune et sortie dans la porte |
| 22–24 s | Coupe anatomique puis chute dans la cuvette | Coupe simplifiée corail, descente et son de chute raccordé à la sortie |
| 25–31,3 s | Le patient voit les traces et décide de consulter | Léa, notre personnage récurrent, réagit dans les toilettes |
| Ajout propre à la série | Consultation et abonnement | Notre docteure explique la possibilité d’irritation et l’importance de consulter en cas de sang, puis termine avec le CTA |

Les paroles françaises sont adaptées de la fonction des échanges de la référence, avec des formulations et une réplique comique propres au studio. La scène de consultation est ajoutée selon notre format récurrent. Ce n’est pas une création sans inspiration extérieure : les dossiers de fabrication doivent conserver cette provenance.

## Fabrication et réemploi

Profil `lcp-1.2.0`, casting, visages, voix et cabinet récurrents. Le côlon et le corps « caca-b » existaient dans l’épisode 005. Le policier comique et ses bottes viennent du 006-v3. Les variantes retirent son panneau et ses mains de repos pendant la pose de travail. Les calques, pivots et noms sont indexés dans la bibliothèque. Aucun appel Recraft pour cet épisode.

Porte, marqueur, bras liés aux contacts, coupe anatomique et accessoires de toilettes sont composés dans notre moteur Python/PIL, avec interpolation PCHIP des mouvements à 60 échantillons/s puis rendu à 30 images/s. Les sons courts réutilisent les bibliothèques du 006 et du 006-v3. Les douze prises françaises utilisent les alias ElevenLabs habituels. La musique est notre composition « Petites combines », 125 BPM ; la bande-son du tiers n’est pas réutilisée.

Le second cadre du cabinet porte « Envie d’y aller ? N’attends pas. Ton corps a parlé. ». Le filigrane est exactement `@lecorps.parle.fr`.

## Vérification médicale — 4 novembre 2026

- Le côlon absorbe de l’eau ; un séjour prolongé peut durcir les selles. Se retenir est un facteur possible, pas la seule cause de constipation. [Assurance Maladie : définition et causes](https://www.ameli.fr/assure/sante/themes/constipation-adulte/definition-symptomes-facteurs-favorisants).
- Fibres, hydratation et activité physique peuvent aider ; éviter de forcer. En cas de sang dans les selles, consulter pour en déterminer la cause ; le film ne pose aucun diagnostic. [Assurance Maladie : gestes et consultation](https://www.ameli.fr/assure/sante/themes/constipation-adulte/que-faire-quand-consulter).
- Le marqueur est un gag visuel et les traces rouges symbolisent une alerte. Le sang n’est pas fabriqué volontairement par un gardien pour envoyer un message, et n’est pas une conséquence systématique de quelques jours sans selle.

Format court de croissance, durée mesurée environ 46,3 s. Il n’est pas présenté comme éligible à une récompense exigeant plus d’une minute.
