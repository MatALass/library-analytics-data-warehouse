# Library-Analytics-Data-Warehouse

Projet Power BI d'analyse d'un réseau de bibliothèques académiques (France + Belgique).
Modèle en **constellation** : 3 tables de faits partageant 5 dimensions communes.

## Modèle

```
                          DIM_DATE
                             │
   DIM_USER ── FACT_LOAN ────┼──── FACT_RESERVATION ── DIM_USER
        │          │         │            │
   DIM_BOOK ───────┼─────────┼────────────┼──── DIM_BOOK
        │          │         │            │
  DIM_BRANCH ──────┘         │            └──── DIM_BRANCH
        │                    │
  DIM_CATEGORY ──────────────┴──── FACT_INVENTORY_SNAPSHOT ── DIM_BOOK / DIM_BRANCH / DIM_CATEGORY / DIM_DATE
```

| Table de faits | Grain | Clé technique |
|---|---|---|
| `FACT_LOAN` | 1 emprunt | `loan_id` |
| `FACT_RESERVATION` | 1 réservation | `reservation_id` |
| `FACT_INVENTORY_SNAPSHOT` | 1 état de stock livre × branche × mois | `snapshot_id` |

Dimensions partagées : `DIM_DATE`, `DIM_BOOK`, `DIM_BRANCH`, `DIM_CATEGORY`, `DIM_USER`.

## Pourquoi 3 facts (et plus une seule)

`loan` et `reservation` sont des événements transactionnels ; `inventory_snapshot`
est un état périodique (grain livre × branche × mois, sans usager). Mélanger les
deux natures dans une fact unique imposait une moitié de colonnes vides par ligne
et des colonnes « fuyantes » entre types. Le découpage en facts transactionnelles
+ fact de snapshot périodique est le pattern Kimball standard et supprime ces
défauts. Voir `05_documentation/SCHEMA_ETOILE.md`.

## Structure

```
library-analytics-data-warehouse/
├── 00_modele_commun/              # .pbix commun (à reconstruire sur le modèle 3-facts)
├── 01_data_csv/                   # CSV à importer dans Power BI (UTF-8, sans BOM)
├── 02_mesures_dax/                # mesures DAX
├── 03_rapports_individuels/       # pages par contributeur
├── 04_livrable_final/
├── 05_documentation/              # schéma, dictionnaire, patterns, relations
└── generator/                     # générateur reproductible des données
```

## Données

Les CSV de `01_data_csv/` sont **générés** par `generator/generate_data.py`
(seed fixe, reproductible). Des tendances analytiques sont injectées
volontairement — voir `05_documentation/PATTERNS_ANALYTIQUES.md` pour la liste
de ce qu'on peut mettre en avant dans l'analyse.

Pour régénérer :

```powershell
cd generator
pip install pandas numpy
python generate_data.py
```

## Répartition des pages

- Raphaël : pages 1 et 2.
- Samuel : pages 3 et 4.
- Mathieu : pages 5 et 6.
