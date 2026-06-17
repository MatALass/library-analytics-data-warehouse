# Plan des pages Power BI

## Page 1 — Vue d'ensemble & Activité — Raphaël

Visuels :

- KPI : Total emprunts, Emprunteurs actifs, Durée moyenne de prêt, Taux de disponibilité global.
- Top 10 des livres les plus empruntés.
- Emprunts par catégorie.
- Évolution mensuelle des emprunts avec marqueur `is_exam_period`.
- Slicers : année, pays, type d'usager.

Mesures principales : `[Total Emprunts]`, `[Emprunteurs Actifs]`, `[Durée Moyenne de Prêt]`, `[Taux de Disponibilité Global]`.

## Page 2 — Analyse temporelle des prêts — Raphaël

Visuels :

- Emprunts par mois et trimestre.
- Matrice `DIM_DATE × DIM_CATEGORY`.
- Aires empilées par catégorie dans le temps.
- Hiérarchie Année > Trimestre > Mois.
- Comparaison examen vs hors examen.

Mesures principales : `[Total Emprunts]`, `[Emprunts Période Examen]`, `[Emprunts Hors Examen]`, `[Ratio Examen vs Hors Examen]`.

## Page 3 — Géographique & Branches — Samuel

Visuels :

- Carte des branches.
- Emprunts par branche.
- Emprunts par type d'établissement.
- Matrice branche × catégorie.
- Comparaison France vs Belgique.

Mesures principales : `[Total Emprunts]`, `[Emprunts France]`, `[Emprunts Belgique]`.

## Page 4 — Usagers & Comportement — Samuel

Visuels :

- Top 10 emprunteurs.
- Emprunts par type d'usager et faculté.
- Distribution de la durée des prêts.
- Taux de retard par profil.
- Croisement `academic_level × user_type`.

Mesures principales : `[Total Emprunts]`, `[Taux de Retard]`, `[Pénalités Totales]`, `[Durée Moyenne de Prêt]`.

## Page 5 — Catalogue & Livres — Mathieu

Visuels :

- Top 10 livres.
- Top auteurs.
- Répartition par catégorie/genre.
- Taux de disponibilité par catégorie.
- Table détaillée des livres avec mise en forme conditionnelle.

Mesures principales : `[Total Emprunts]`, `[Availability Rate]`, `[Total Exemplaires]`, `[Exemplaires Disponibles]`.

## Page 6 — Disponibilité & Gestion du stock — Mathieu

Visuels :

- KPI : Total exemplaires, Disponibles, Taux d'occupation, Titres en rupture.
- Top livres en tension.
- Disponibilité par catégorie.
- Réservations pending/cancelled par livre.
- Délai d'attente moyen par catégorie ou branche.
- Matrice livre × branche avec disponibilité.
- Drill-through livre ou branche.

Mesures principales : `[Utilization Rate]`, `[Titres en Rupture]`, `[Réservations Non Satisfaites]`, `[Délai d’Attente Moyen]`, `[Score Tension Stock]`.
