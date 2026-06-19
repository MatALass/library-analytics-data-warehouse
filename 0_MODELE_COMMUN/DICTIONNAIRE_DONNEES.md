# Dictionnaire des données

## `FACT_LOAN` (grain : un emprunt)

| Colonne | Type | Description |
|---|---|---|
| `loan_id` | texte | Clé technique de l'emprunt. |
| `date_id` | entier | Clé de date (→ `DIM_DATE`). |
| `event_date` | date | Date de l'emprunt (lisible). |
| `user_id` | entier | Clé usager (→ `DIM_USER`). |
| `book_id` | entier | Clé livre (→ `DIM_BOOK`). |
| `branch_id` | entier | Clé branche (→ `DIM_BRANCH`). |
| `category_id` | entier | Clé catégorie (→ `DIM_CATEGORY`), = catégorie du livre. |
| `loan_date` | date | Date d'emprunt. |
| `due_date` | date | Date prévue de retour. |
| `return_date` | date | Date réelle de retour. Vide si emprunt encore en cours. |
| `loan_duration_days` | entier | Durée effective du prêt (jours). |
| `days_overdue` | entier | Jours de retard (0 si à l'heure). |
| `penalty_amount` | décimal | Pénalité simulée (0,30 €/jour de retard). |
| `quantity` | entier | Quantité empruntée (1). |

## `FACT_RESERVATION` (grain : une réservation)

| Colonne | Type | Description |
|---|---|---|
| `reservation_id` | texte | Clé technique de la réservation. |
| `date_id` | entier | Clé de date (→ `DIM_DATE`). |
| `event_date` | date | Date de la réservation. |
| `user_id` | entier | Clé usager (→ `DIM_USER`). |
| `book_id` | entier | Clé livre (→ `DIM_BOOK`). |
| `branch_id` | entier | Clé branche (→ `DIM_BRANCH`). |
| `category_id` | entier | Clé catégorie (→ `DIM_CATEGORY`). |
| `reservation_status` | texte | `fulfilled`, `pending` ou `cancelled`. |
| `wait_days` | entier | Délai d'attente avant satisfaction / abandon. |
| `quantity` | entier | Quantité réservée (1). |

## `FACT_INVENTORY_SNAPSHOT` (grain : livre × branche × mois)

| Colonne | Type | Description |
|---|---|---|
| `snapshot_id` | texte | Clé technique du snapshot. |
| `date_id` | entier | Date du snapshot (fin de mois, → `DIM_DATE`). |
| `snapshot_date` | date | Date du snapshot (lisible). |
| `book_id` | entier | Clé livre (→ `DIM_BOOK`). |
| `branch_id` | entier | Clé branche (→ `DIM_BRANCH`). |
| `category_id` | entier | Clé catégorie (→ `DIM_CATEGORY`). |
| `total_copies` | entier | Exemplaires alloués à ce livre dans cette branche. |
| `available_copies` | entier | Exemplaires disponibles au moment du snapshot. |
| `active_loans` | entier | Exemplaires actuellement empruntés. |
| `utilization_rate` | décimal | `active_loans / total_copies` (0 à 1). |
| `availability_rate` | décimal | `available_copies / total_copies` (0 à 1). |
| `out_of_stock` | booléen | `True` si `available_copies = 0`. |
| `loan_count_total` | entier | Emprunts cumulés sur ce couple livre × branche. |
| `loan_count_120d` | entier | Emprunts sur les 120 jours précédant le snapshot. |
| `unsatisfied_reservations` | entier | Demande non satisfaite estimée (copies manquantes). |
| `reallocation_priority` | texte | `Critique`, `Élevée`, `Normale`, `Faible`. |

## Dimensions

- `DIM_DATE` : calendrier académique (mois, trimestre, année, période d'examen, période académique).
- `DIM_BOOK` : livre, auteur, catégorie, niveau académique, langue, `demand_tier`, `base_total_copies`, `popularity_score`. **Plus de colonnes d'inventaire.**
- `DIM_CATEGORY` : catégorie, sous-catégorie, cluster disciplinaire.
- `DIM_BRANCH` : bibliothèque, ville, pays, type, coordonnées, profil.
- `DIM_USER` : usager, type (`Student`/`Researcher`/`Faculty`), faculté, niveau, pays, branche préférée.
