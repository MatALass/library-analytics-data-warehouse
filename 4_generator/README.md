# Générateur de données

`generate_data.py` produit les 8 CSV de `../01_data_csv/` de façon reproductible
(seed fixe = 42).

## Utilisation
```powershell
pip install pandas numpy
python generate_data.py
```

## Principe
- Les 5 dimensions sources sont dans `source_dimensions/` (hand-authored).
  Le script les recopie dans `01_data_csv/` (et nettoie `DIM_BOOK` de ses
  anciennes colonnes d'inventaire).
- Les 3 facts sont générées avec des **tendances injectées volontairement**
  (Pareto livres, pic d'examens par catégorie, asymétrie de charge entre
  branches, croissance annuelle, segmentation usagers, déséquilibre de stock
  pour la réallocation). Détail : `../05_documentation/PATTERNS_ANALYTIQUES.md`.

## Paramètres de tendance
Tout est regroupé en haut du script (section 1) : poids de demande par livre,
charge et tension par branche, sensibilité aux examens par catégorie, affinité
faculté→catégorie, politique de prêt. Modifier ces dictionnaires pour ajuster
l'intensité des signaux, puis relancer.
