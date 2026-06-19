# FAIT — Mathieu (pages 5 et 6)

Ces 2 pages sont **construites** (elles sont dans `MODELE_pages_5_6.pbix`). Ce
dossier sert de **référence** : ouvrez le pbix pour voir à quoi ressemble une
page finie, et comment sont posées les mesures.

## Page 5 — Catalogue & demande
Répond à Q8 (quels livres prioriser → Pareto, 20 % des livres ≈ 46 % des emprunts)
et Q9 (où la demande coince → table des livres réservés avec attente/annulation).

## Page 6 — Stock & moteur de réallocation (différenciateur)
Répond à Q10 (état de tension du stock), Q11 (où réallouer, combien) et Q12
(peut-on couvrir le manque sans racheter).
Chiffres clés : **124 couples critiques**, **353 exemplaires de demande non
satisfaite**, et **32 % de ce manque couvrable par redistribution du stock dormant**.
La table prescriptive (filtrée sur un livre, dernier mois) montre la paire
Critique/Faible = ordre de transfert (ex. déplacer de Liège vers Paris).

## Mesures
Dans `mesures_mathieu.dax`. Déjà créées dans le pbix.

## Pour la soutenance
Mener avec Q11/Q12 : « le réseau est déséquilibré, mais un tiers du manque se
règle sans rien acheter, juste en redéployant le stock ». Préciser que la table
est filtrée sur un livre pour la démo, mais que le moteur s'applique à tout le catalogue.
