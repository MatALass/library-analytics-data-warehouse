# Schéma en étoile — version une seule table de faits

## Table de faits centrale

### `FACT_LIBRARY`

Cette table contient toutes les observations métier du projet. La colonne structurante est :

- `event_type`

Valeurs possibles :

- `loan` : emprunt d'un livre par un usager.
- `reservation` : demande de réservation.
- `inventory_snapshot` : état de stock pour un couple livre × branche.

## Dimensions

- `DIM_DATE`
- `DIM_CATEGORY`
- `DIM_BOOK`
- `DIM_BRANCH`
- `DIM_USER`

## Relations Power BI

```text
DIM_DATE[date_id]         1 ─── * FACT_LIBRARY[date_id]
DIM_CATEGORY[category_id] 1 ─── * FACT_LIBRARY[category_id]
DIM_BOOK[book_id]         1 ─── * FACT_LIBRARY[book_id]
DIM_BRANCH[branch_id]     1 ─── * FACT_LIBRARY[branch_id]
DIM_USER[user_id]         1 ─── * FACT_LIBRARY[user_id]
```

Paramètres recommandés :

- Cardinalité : `One-to-many`.
- Direction de filtre : `Single`.
- Les dimensions filtrent la table de faits.

## Remarque de modélisation importante

Dans un entrepôt de données strict, les emprunts/réservations et les snapshots de stock seraient souvent séparés en deux facts, car leur grain n'est pas le même. Ici, comme le projet impose une seule fact, on utilise une table de faits unique avec un discriminant `event_type`.

La conséquence est simple : les mesures DAX doivent être rigoureuses. Une mesure d'emprunt filtre `event_type = "loan"`. Une mesure de stock filtre `event_type = "inventory_snapshot"`. Une mesure de réservation filtre `event_type = "reservation"`.
