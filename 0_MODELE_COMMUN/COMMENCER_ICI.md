# COMMENCER ICI — à lire avant tout

Ce dossier contient **le point de départ commun**. Ne reconstruis pas le modèle :
il est déjà fait, testé et fonctionnel dans le fichier `.pbix`.

## Étape 1 — Ouvre le bon fichier

Ouvre **`MODELE_pages_5_6.pbix`** dans Power BI Desktop, puis **enregistre-le
sous ton nom** (ex. `pages_1_2_raphael.pbix`) dans ton dossier perso. Tu travailles
sur ta copie, pas sur l'original.

Ce fichier contient déjà :
- le modèle en **constellation** (3 facts + 5 dimensions) avec les 14 relations ;
- les **types corrigés** (le piège des booléens / décimaux est déjà réglé) ;
- les **mesures de base** (`Total Emprunts`, `Total Réservations`, etc.) dans la table `_Mesures` ;
- les **pages 5 et 6** de Mathieu (exemples de ce qu'on attend).

Donc tu démarres avec un modèle qui marche. Tu n'as qu'à **ajouter tes 2 pages**.

## Étape 2 — Vérifie que tout va bien (test des valeurs)

Crée une page de test, pose ces mesures sur des cartes, compare :

| Mesure | Doit afficher |
|---|---|
| `Total Emprunts` | 16 000 |
| `Total Réservations` | 3 600 |
| `Couples Critiques (dernier mois)` | 124 |
| `Taux de Couverture Réallocation %` | 32,29 % |

Si les chiffres tombent, le modèle est bon. Supprime la page de test.

## Étape 3 — Crée tes mesures

Ouvre le fichier `mesures_*.dax` de TON dossier, et crée chaque mesure dans la
table **`_Mesures`** (copier-coller). Les mesures de base existent déjà, ne les
recrée pas. Pense à **formater** : `%` pour les taux, `€` pour les pénalités,
nombre entier + séparateur de milliers pour les compteurs.

## Étape 4 — Construis tes pages

Suis les maquettes de ton `INSTRUCTIONS.md`. Chaque page répond à des questions
métier précises, avec la réponse attendue déjà indiquée.

---

## ⚠️ Les 3 pièges (déjà réglés dans le pbix, mais à connaître)

Si tu repars d'un import CSV brut un jour, tu retomberas dessus :

1. **Types texte au lieu de décimal.** `utilization_rate`, `availability_rate`,
   `penalty_amount`, `popularity_score` peuvent s'importer en TEXTE → les mesures
   `AVERAGE`/`SUM` plantent (« ne peut pas fonctionner avec des valeurs de type
   String »). Fix : Power Query → *Modifier le type → Utilisation des paramètres
   régionaux* → Décimal, anglais (US), car les CSV utilisent le point décimal.

2. **Booléens en texte.** `is_exam_period`, `is_weekend`, `out_of_stock` doivent
   être en **Booléen**. Sinon `= TRUE()` ne matche rien (cartes vides). Soit
   retyper la colonne, soit remplacer `= TRUE()` par `= "True"` dans les mesures.

3. **Hiérarchie de dates parasite.** Quand tu mets `year_month` en axe, Power BI
   le transforme en hiérarchie (Année/Trimestre/Mois/Jour) et n'affiche que
   l'Année. Fix : dans le puits, flèche déroulante du champ → choisis `year_month`
   tout court (pas « Hiérarchie de dates »).

## ⚠️ La règle du snapshot (pour qui touche au stock)

`FACT_INVENTORY_SNAPSHOT` est un snapshot mensuel : **ne jamais sommer ses
colonnes à travers le temps**. Mesures `(dernier mois)` = cartes KPI ;
mesures `(mois)` = courbes avec le mois en axe. Pour figer un tableau au dernier
mois, filtre `snapshot_date` en **Filtrage de base** sur la dernière date
(pas « N premiers »).
