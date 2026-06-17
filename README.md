# Library-Analytics-Data-Warehouse

Projet Power BI basé sur un modèle en étoile pour analyser l'activité d'un réseau de bibliothèques académiques.

## Structure

```text
library-analytics-data-warehouse/
├── 00_modele_commun/
├── 01_data_csv/
├── 02_mesures_dax/
├── 03_rapports_individuels/
├── 04_livrable_final/
└── 05_documentation/
```

## Tables CSV

Dimensions :

- `DIM_DATE.csv`
- `DIM_CATEGORY.csv`
- `DIM_BOOK.csv`
- `DIM_BRANCH.csv`
- `DIM_USER.csv`

Fact unique :

- `FACT_LIBRARY.csv`

## Répartition des pages

- Raphaël : pages 1 et 2.
- Samuel : pages 3 et 4.
- Mathieu : pages 5 et 6.

## Fichiers DAX

- `raphael_pages_1_2.dax`
- `samuel_pages_3_4.dax`
- `mathieu_pages_5_6.dax`
- `mesures_validees_modele_commun.dax`

Le fichier central à intégrer dans le modèle commun est :

```text
02_mesures_dax/mesures_validees_modele_commun.dax
```

## Point de vigilance

La fact unique contient trois types de lignes :

- `loan`
- `reservation`
- `inventory_snapshot`

Les mesures DAX doivent donc filtrer `FACT_LIBRARY[event_type]`. Ne faites pas de `COUNTROWS(FACT_LIBRARY)` brut dans vos visuels.
