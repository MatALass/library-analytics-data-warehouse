# Note — Pourquoi une seule fact peut fonctionner ici

Le projet utilise une seule table de faits : `FACT_LIBRARY`.

Ce choix est acceptable pour un projet Power BI pédagogique à condition de respecter deux règles :

1. Toujours filtrer `event_type` dans les mesures.
2. Ne pas additionner directement des colonnes qui ne concernent pas le même type de ligne.

Exemples :

- `COUNTROWS(FACT_LIBRARY)` sans filtre est faux, car cela mélange emprunts, réservations et stock.
- `SUM(total_copies)` doit être calculé uniquement sur `event_type = "inventory_snapshot"`.
- `AVERAGE(loan_duration_days)` doit être calculé uniquement sur `event_type = "loan"`.

Dans un vrai projet d'entreprise, on séparerait probablement les facts. Mais si la consigne est d'avoir une seule fact, cette structure est le compromis le plus propre.
