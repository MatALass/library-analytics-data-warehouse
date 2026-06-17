# Import des CSV dans Power BI — version une seule table de faits

## Tables à importer

Dimensions :

- `DIM_DATE.csv`
- `DIM_CATEGORY.csv`
- `DIM_BOOK.csv`
- `DIM_BRANCH.csv`
- `DIM_USER.csv`

Table de faits unique :

- `FACT_LIBRARY.csv`

## Relations recommandées

Toutes les relations vont des dimensions vers `FACT_LIBRARY` :

- `DIM_DATE[date_id]` → `FACT_LIBRARY[date_id]`
- `DIM_CATEGORY[category_id]` → `FACT_LIBRARY[category_id]`
- `DIM_BOOK[book_id]` → `FACT_LIBRARY[book_id]`
- `DIM_BRANCH[branch_id]` → `FACT_LIBRARY[branch_id]`
- `DIM_USER[user_id]` → `FACT_LIBRARY[user_id]`

Cardinalité : `1:*`.
Sens du filtre : `Single`, de la dimension vers la fact.

## Point important sur la fact unique

`FACT_LIBRARY.csv` contient trois types de lignes dans la colonne `event_type` :

- `loan` : une ligne = un emprunt.
- `reservation` : une ligne = une réservation.
- `inventory_snapshot` : une ligne = un état de stock pour un couple livre × branche.

Comme la table mélange plusieurs grains métiers, les mesures DAX doivent toujours filtrer `event_type`. C’est indispensable pour éviter les agrégations fausses.

Exemples :

- Total emprunts → filtrer `event_type = "loan"`.
- Réservations non satisfaites → filtrer `event_type = "reservation"`.
- Total exemplaires / disponibilité → filtrer `event_type = "inventory_snapshot"`.

## Conseil Power BI

Créez une table vide `_Mesures` dans Power BI et rangez-y toutes les mesures validées. Les fichiers DAX du dossier `02_mesures_dax` sont prêts pour cette organisation.
