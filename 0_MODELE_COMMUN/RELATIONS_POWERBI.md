# Relations Power BI — checklist d'import

## Ordre d'import
Importer d'abord les 5 dimensions, puis les 3 facts. Tous les CSV sont en
**UTF-8 sans BOM**, séparateur virgule.

## Relations à créer (12)

| Dimension (1) | Fait (*) | Clé |
|---|---|---|
| DIM_DATE | FACT_LOAN | date_id |
| DIM_USER | FACT_LOAN | user_id |
| DIM_BOOK | FACT_LOAN | book_id |
| DIM_BRANCH | FACT_LOAN | branch_id |
| DIM_CATEGORY | FACT_LOAN | category_id |
| DIM_DATE | FACT_RESERVATION | date_id |
| DIM_USER | FACT_RESERVATION | user_id |
| DIM_BOOK | FACT_RESERVATION | book_id |
| DIM_BRANCH | FACT_RESERVATION | branch_id |
| DIM_CATEGORY | FACT_RESERVATION | category_id |
| DIM_DATE | FACT_INVENTORY_SNAPSHOT | date_id |
| DIM_BOOK | FACT_INVENTORY_SNAPSHOT | book_id |
| DIM_BRANCH | FACT_INVENTORY_SNAPSHOT | branch_id |
| DIM_CATEGORY | FACT_INVENTORY_SNAPSHOT | category_id |

Pour chaque relation : cardinalité **One-to-many (1:*)**, direction de filtre
croisé **Single** (la dimension filtre le fait).

## Pièges à éviter

- **Ne PAS créer** de relation DIM_BOOK → DIM_CATEGORY. La catégorie est reliée
  directement aux facts via `category_id`. Créer en plus un lien livre→catégorie
  ferait un chemin ambigu (snowflake) ; Power BI désactiverait une relation.
- **DIM_DATE** : la marquer comme table de dates (Marquer comme table de dates →
  `full_date`) pour activer la time intelligence.
- **`return_date` vide** dans FACT_LOAN = emprunt en cours. Normal, ne pas le
  traiter comme une erreur. Une mesure « emprunts en cours » =
  `CALCULATE(COUNTROWS(FACT_LOAN), ISBLANK(FACT_LOAN[return_date]))`.
- **Snapshot ≠ somme** : ne jamais sommer `available_copies` dans le temps. Sur
  une fact de snapshot périodique, on agrège un état avec
  `AVERAGE`/`LASTNONBLANK`, jamais `SUM` sur l'axe temps.
