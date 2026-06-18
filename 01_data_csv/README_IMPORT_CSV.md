# Import des CSV dans Power BI

Fichiers (UTF-8 sans BOM, séparateur `,`) :

Dimensions : `DIM_DATE`, `DIM_CATEGORY`, `DIM_BOOK`, `DIM_BRANCH`, `DIM_USER`.
Faits : `FACT_LOAN`, `FACT_RESERVATION`, `FACT_INVENTORY_SNAPSHOT`.

1. Importer les 5 dimensions puis les 3 faits.
2. Vérifier les types : les `*_id`, durées, compteurs en **Nombre entier** ;
   `utilization_rate` / `availability_rate` / `penalty_amount` en **Décimal** ;
   `out_of_stock` en **Booléen** ; les dates en **Date**.
3. Créer les relations (voir `05_documentation/RELATIONS_POWERBI.md`).
4. Marquer `DIM_DATE` comme table de dates sur `full_date`.

Ces CSV sont régénérables via `generator/generate_data.py`.
