# Conclusions attendues avec le dataset

Les données sont volontairement déséquilibrées pour rendre les visualisations interprétables.

## Activité globale

- Les emprunts augmentent fortement pendant les périodes d'examen.
- Les catégories Data Science, Business Intelligence et Data Engineering concentrent la demande.
- Quelques livres dominent très nettement les emprunts, ce qui rend le Top 10 utile.

## Temporalité

- Les pics mensuels doivent apparaître autour des périodes d'évaluation.
- La matrice `date × catégorie` montre que toutes les catégories ne réagissent pas pareil aux examens.
- Les visualisations de drill-down Année > Trimestre > Mois doivent montrer une vraie variation.

## Géographie

- Paris-Centre et Bruxelles Campus ressortent comme branches très actives.
- Les branches universitaires et écoles techniques ont une demande plus forte en numérique.
- La comparaison France vs Belgique doit montrer une différence visible, pas un 50/50 artificiel.

## Usagers

- Les étudiants empruntent davantage et ont plus de retards.
- Les chercheurs ont moins d'emprunts mais des durées de prêt plus longues.
- Les profils Informatique/Data sont surreprésentés dans les catégories techniques.

## Catalogue et stock

- Certains titres sont en rupture ou quasi-rupture.
- Data Science, BI et Data Engineering ont une disponibilité faible.
- Littérature et Sciences Humaines sont relativement moins tendues.
- La page stock doit permettre de recommander une réallocation ou un rachat d'exemplaires.
