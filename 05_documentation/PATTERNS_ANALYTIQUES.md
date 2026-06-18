# Patterns analytiques injectés

Les données ne sont pas uniformes : des tendances sont introduites volontairement
et de façon **corrélée**, pour que l'analyse révèle des signaux exploitables. Ce
document liste ce qui est dans les données et ce qu'on peut mettre en avant. Les
chiffres ci-dessous sont mesurés sur le jeu généré (seed 42).

## 1. Pareto sur les livres (effet 80/20)
Les 20 % de livres les plus demandés concentrent **~44 % des emprunts** ; la
longue traîne des livres `low` reste peu empruntée. → Visuel « top livres »,
courbe de concentration, discours sur les acquisitions ciblées.

## 2. Pic d'examens × catégorie (effet d'interaction)
Les emprunts montent fortement en période d'examens, **mais pas pour tout le monde** :

| Catégorie | Examens (empr./j) | Hors exam. (empr./j) | Ratio |
|---|---|---|---|
| Droit | 6,0 | 2,2 | ×2,8 |
| Data Science & IA | 5,1 | 1,8 | ×2,9 |
| Santé | 5,5 | 2,0 | ×2,7 |
| Littérature | 2,8 | 1,5 | ×1,8 |
| Sciences Humaines | 2,8 | 1,7 | ×1,6 |

→ STEM / Droit / Santé / Éco explosent ; Lettres / SHS restent plats. Croisement
`DIM_DATE[is_exam_period]` × `DIM_CATEGORY`. C'est un effet d'interaction, plus
parlant qu'une simple moyenne.

## 3. Asymétrie de charge entre branches
Volume d'emprunts très inégal : Paris-Centre ~4 350, Lyon ~3 500, Bruxelles ~3 100,
Lille ~2 170, Marseille ~1 600, Liège ~1 260. → Classement de branches, carte
(coordonnées dans `DIM_BRANCH`).

## 4. Tendance annuelle + croissance d'une branche
Le réseau croît : **22,8 → 24,4 → 28,6 emprunts/jour** de 2024 à 2026. Et la part
de Bruxelles passe de **17,9 % à 21,7 %** : c'est la branche qui monte le plus vite.
→ Courbe temporelle, analyse YoY, focus « hub émergent ».
Pic de rentrée chaque septembre, creux en été (juillet-août).

## 5. Segmentation des usagers
Taux de retard par type : **Student 24,8 %**, Researcher 15,3 %, Faculty 14,5 %.
Les chercheurs/enseignants ont aussi une durée de prêt autorisée plus longue (28 j
vs 14 j) et empruntent davantage. Affinité faculté → catégorie respectée (les
juristes empruntent du Droit, etc.). → Profils d'usagers, segmentation pénalités.

## 6. Réallocation de stock — LE point différenciant (moteur prescriptif)
`FACT_INVENTORY_SNAPSHOT` contient un déséquilibre volontaire : les branches
tendues (Paris, Bruxelles, Marseille) sont **sous-allouées** vs leur demande, les
branches calmes (Lille, Liège) ont du **stock dormant**.

Résultat mesuré : **50 paires (livre × mois)** où, le même mois, une branche est en
rupture avec demande non satisfaite **pendant qu'une autre a des exemplaires
inutilisés** du même livre. Au total **~140 exemplaires dormants** seraient
mobilisables face à de la demande non satisfaite.

Exemple lisible — *Marketing Analytics*, mars 2025 :

| Branche | total | dispo | utilisation | non satisf. | priorité |
|---|---|---|---|---|---|
| Paris-Centre | 5 | 0 | 1,00 | 3 | Critique |
| Lyon | 5 | 0 | 1,00 | 2 | Critique |
| Bruxelles | 4 | 0 | 1,00 | 2 | Critique |
| Marseille | 3 | 0 | 1,00 | 1 | Critique |
| **Lille** | 4 | **1** | 0,75 | 0 | **Faible** |
| **Liège** | 3 | **2** | 0,33 | 0 | **Faible** |

→ Recommandation prescriptive directe : déplacer des exemplaires de Lille/Liège
vers Paris/Bruxelles. C'est le cœur de la page « moteur de recommandation ».

## 7. Dynamique des réservations
Délai d'attente et taux d'annulation suivent la tension de la branche :

| Branche | Attente moy. (j) | Taux d'annulation |
|---|---|---|
| Paris-Centre | 7,6 | 18,2 % |
| Bruxelles | 7,6 | 17,0 % |
| Marseille | 6,8 | 13,9 % |
| Lyon | 5,4 | 11,6 % |
| Lille | 1,2 | 6,1 % |
| Liège | 0,7 | 2,9 % |

→ Là où ça coince, on attend plus longtemps et on annule davantage. Renforce
l'histoire de réallocation.

---

**À garder en tête pour la soutenance** : ces tendances sont cohérentes entre
elles (une branche tendue est tendue en volume, en réservations ET en stock). Ce
n'est pas du bruit : chaque page peut raconter un morceau d'une même histoire
« le réseau est déséquilibré et on sait comment le rééquilibrer ».
