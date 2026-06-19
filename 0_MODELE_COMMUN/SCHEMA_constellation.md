# Schéma en constellation — 3 tables de faits

Le projet utilise trois tables de faits qui partagent les mêmes dimensions
conformes (schéma dit « en constellation » ou *fact constellation*).

## Tables de faits

### `FACT_LOAN` — grain : un emprunt
Un événement transactionnel : un usager emprunte un livre dans une branche à une date.
Colonnes métier : durées, retards, pénalités. Aucune colonne vide.

### `FACT_RESERVATION` — grain : une réservation
Un événement transactionnel : un usager réserve un livre. Colonnes métier :
statut (`fulfilled` / `pending` / `cancelled`) et délai d'attente.

### `FACT_INVENTORY_SNAPSHOT` — grain : livre × branche × mois
Un *snapshot périodique* (fin de mois) de l'état de stock d'un livre dans une
branche. Pas d'usager. Colonnes métier : exemplaires, taux d'occupation /
disponibilité, ruptures, réservations non satisfaites, priorité de réallocation.
C'est la table qui alimente le moteur de recommandation prescriptif.

## Dimensions partagées

`DIM_DATE`, `DIM_BOOK`, `DIM_BRANCH`, `DIM_CATEGORY`, `DIM_USER`.

`DIM_BOOK` ne contient plus que des **attributs de livre**. Les anciennes colonnes
d'inventaire (`total_copies`, `available_copies`, `active_loans`,
`utilization_rate`, `availability_rate`, `out_of_stock_global`, `book_count`) ont
été retirées : ce sont des faits, ils vivent dans `FACT_INVENTORY_SNAPSHOT` au bon
grain (livre × branche × mois). On garde `base_total_copies` comme attribut de
dotation catalogue.

## Relations Power BI

```text
DIM_DATE[date_id]          1 ─── *  FACT_LOAN[date_id]
DIM_USER[user_id]          1 ─── *  FACT_LOAN[user_id]
DIM_BOOK[book_id]          1 ─── *  FACT_LOAN[book_id]
DIM_BRANCH[branch_id]      1 ─── *  FACT_LOAN[branch_id]
DIM_CATEGORY[category_id]  1 ─── *  FACT_LOAN[category_id]

DIM_DATE[date_id]          1 ─── *  FACT_RESERVATION[date_id]
DIM_USER[user_id]          1 ─── *  FACT_RESERVATION[user_id]
DIM_BOOK[book_id]          1 ─── *  FACT_RESERVATION[book_id]
DIM_BRANCH[branch_id]      1 ─── *  FACT_RESERVATION[branch_id]
DIM_CATEGORY[category_id]  1 ─── *  FACT_RESERVATION[category_id]

DIM_DATE[date_id]          1 ─── *  FACT_INVENTORY_SNAPSHOT[date_id]
DIM_BOOK[book_id]          1 ─── *  FACT_INVENTORY_SNAPSHOT[book_id]
DIM_BRANCH[branch_id]      1 ─── *  FACT_INVENTORY_SNAPSHOT[branch_id]
DIM_CATEGORY[category_id]  1 ─── *  FACT_INVENTORY_SNAPSHOT[category_id]
```

Paramètres : cardinalité `One-to-many`, direction de filtre `Single`
(les dimensions filtrent les faits). Détails et pièges dans
`RELATIONS_POWERBI.md`.

## Conséquence sur les mesures DAX

Plus besoin de filtrer un discriminant `event_type` partout : chaque mesure
s'écrit sur sa propre fact. `COUNTROWS(FACT_LOAN)` = nombre d'emprunts, point.
`SUM(FACT_INVENTORY_SNAPSHOT[total_copies])` répond correctement au filtre branche.
C'est le bénéfice principal du découpage.
