# Dictionnaire des données

## `FACT_LIBRARY`

| Colonne | Description |
|---|---|
| `fact_id` | Identifiant technique de la ligne de fact. |
| `source_id` | Identifiant dans l'ancienne source logique. |
| `fact_source` | `event` ou `inventory`. |
| `event_type` | `loan`, `reservation` ou `inventory_snapshot`. |
| `date_id` | Clé de date reliée à `DIM_DATE`. |
| `event_date` | Date lisible de l'événement ou du snapshot. |
| `is_exam_period_event` | Indique si la date est en période d'examen. |
| `user_id` | Clé usager. Vide pour les lignes de stock. |
| `book_id` | Clé livre. |
| `branch_id` | Clé branche. |
| `category_id` | Clé catégorie. |
| `reservation_status` | Statut de réservation : `fulfilled`, `pending`, `cancelled`. |
| `loan_date` | Date d'emprunt. |
| `due_date` | Date prévue de retour. |
| `return_date` | Date réelle de retour. |
| `loan_duration_days` | Durée effective du prêt. |
| `days_overdue` | Nombre de jours de retard. |
| `penalty_amount` | Montant de pénalité simulé. |
| `wait_days` | Délai d'attente pour une réservation. |
| `quantity` | Quantité transactionnelle, principalement 1 pour les emprunts. |
| `total_copies` | Nombre total d'exemplaires pour une ligne `inventory_snapshot`. |
| `available_copies` | Exemplaires disponibles pour une ligne `inventory_snapshot`. |
| `active_loans` | Exemplaires actuellement occupés pour une ligne `inventory_snapshot`. |
| `utilization_rate` | Taux d'occupation stocké au niveau livre × branche. |
| `availability_rate` | Taux de disponibilité stocké au niveau livre × branche. |
| `out_of_stock` | Indique une rupture locale livre × branche. |
| `loan_count_total` | Historique total d'emprunts pour le couple livre × branche. |
| `loan_count_120d` | Emprunts sur la période récente simulée. |
| `unsatisfied_reservations` | Réservations non satisfaites simulées au niveau stock. |
| `reallocation_priority` | Priorité de réallocation : `Critique`, `Haute`, `Normale`, etc. |

## Dimensions principales

- `DIM_DATE` : calendrier académique, mois, trimestre, année, période d'examen.
- `DIM_BOOK` : livre, auteur, catégorie, niveau académique, popularité simulée.
- `DIM_CATEGORY` : catégories et sous-catégories.
- `DIM_BRANCH` : bibliothèques, villes, pays, type d'établissement.
- `DIM_USER` : usagers, type, faculté, niveau académique, pays.
