# Modèle commun Power BI

Le fichier `Projet_EDW_original.pbix` est conservé comme base de départ.

Pour la version adaptée, importez les CSV du dossier `01_data_csv` et utilisez uniquement une table de faits :

- `FACT_LIBRARY.csv`

Ne réimportez pas les anciennes facts séparées. Elles ont été supprimées de cette version pour éviter les confusions.

Relations à créer : voir `05_documentation/SCHEMA_ETOILE.md`.
Mesures DAX à ajouter : voir `02_mesures_dax/mesures_validees_modele_commun.dax`.
