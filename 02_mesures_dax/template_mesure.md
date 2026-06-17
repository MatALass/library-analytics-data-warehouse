# Template de mesure DAX

## Nom de la mesure
`[Nom Mesure]`

## Auteur
Raphaël / Samuel / Mathieu

## Pages concernées
Page X — description courte

## Objectif métier
Décrire ce que la mesure permet d'analyser.

## Table recommandée
`_Mesures`

## DAX
```DAX
Nom Mesure =
CALCULATE (
    <expression>,
    'FACT_LIBRARY'[event_type] = "loan" -- ou reservation / inventory_snapshot selon le besoin
)
```

## Validation attendue
- Le résultat est cohérent avec un total manuel.
- La mesure respecte le filtre `event_type` quand nécessaire.
- La mesure fonctionne avec les slicers prévus.
