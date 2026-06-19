# INSTRUCTIONS — Samuel (pages 3 et 4)

> Avant de commencer : lis `0_MODELE_COMMUN/COMMENCER_ICI.md`, ouvre
> `MODELE_pages_5_6.pbix`, enregistre-le sous ton nom. Le modèle est déjà fait.

Tu construis **2 pages** : une sur le réseau (branches), une sur les usagers et
les retards. Pour chaque question, la **réponse attendue** est indiquée.

---

## PAGE 3 — Réseau & branches

### Questions auxquelles cette page répond

**Q5 — Quelles branches sont surchargées, lesquelles sous-utilisées ?**
Réponse attendue : forte asymétrie. **Paris-Centre** (~4 350 emprunts) et
**Bruxelles** en tête ; **Lille** (~2 170), **Marseille** (~1 600) et surtout
**Liège** (~1 260) loin derrière. C'est le déséquilibre de charge du réseau.

**Q2 (volet branche) — La croissance est-elle portée par une branche ?**
Réponse attendue : **Bruxelles** est le hub émergent — sa part passe de ~18 %
(2024) à ~22 % (2026). À montrer avec une courbe multi-lignes par branche.

### Maquette (page 1280 × 720)

```
┌──────────────── Titre : "Analyse du réseau" ─────────────────┐
│  ▼ Année   ▼ Type de branche                                │
├──────────────┬──────────────┬────────────────────────────────┤
│ [Branches    │ [Charge moy. │ [Croissance Branche YoY %]     │
│  Actives]    │  empr/j]     │                                │
├──────────────┴──────────────┴────────────────────────────────┤
│ ┌─────────────────────────┐ ┌──────────────────────────────┐ │
│ │ CARTE (map)             │ │ Classement branches (barres) │ │
│ │ latitude/longitude      │ │ Total Emprunts + Part %      │ │
│ │ taille = Total Emprunts │ │                              │ │
│ └─────────────────────────┘ └──────────────────────────────┘ │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ Emprunts par year_month, une ligne PAR branche         │   │
│ │ → Bruxelles décolle                                    │   │
│ └────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

- **Cartes** : `Branches Actives`, `Charge Moyenne Branche (empr/j)`,
  `Croissance Branche YoY %`.
- **Carte géo** : bulles sur `DIM_BRANCH[latitude]`/`[longitude]`, taille =
  `Total Emprunts` (6 villes FR + BE).
- **Barres** : `Total Emprunts` + `Part Emprunts Branche %` par `branch_name`.
- **Courbe multi-lignes** : `Total Emprunts` par `year_month`, légende `branch_name`.

---

## PAGE 4 — Usagers & comportement

### Questions auxquelles cette page répond

**Q6 — Quels profils d'usagers génèrent les emprunts… et les retards ?**
Réponse attendue (le contraste fort de la page) : les **étudiants** rendent en
retard ~**24,8 %** du temps, contre ~**14,5 %** pour les enseignants (Faculty) et
~15 % pour les chercheurs. Les chercheurs/enseignants empruntent plus et plus
longtemps (durée de prêt autorisée 28 j vs 14 j).

**Q7 — Combien coûtent les retards et qui les concentre ?**
Réponse attendue : à lire via `Pénalités Totales` (0,30 €/jour de retard) croisé
avec le type d'usager et la faculté. Les facultés à forte activité (Droit,
Médecine) concentrent les emprunts.

### Maquette

```
┌──────────────── Titre : "Usagers & retards" ─────────────────┐
│  ▼ Faculté   ▼ Type d'usager                                │
├──────────┬──────────┬──────────┬───────────────────────────┤
│ [Empr.   │ [Taux de │ [Retard  │ [Pénalités Totales €]     │
│ /Usager] │ Retard %]│ Moyen j] │                           │
├──────────┴──────────┴──────────┴───────────────────────────┤
│ ┌─────────────────────────┐ ┌────────────────────────────┐ │
│ │ Taux de Retard % PAR     │ │ Emprunts par faculté       │ │
│ │ user_type (barres)       │ │ (barres, faculty)          │ │
│ └─────────────────────────┘ └────────────────────────────┘ │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Table : top usagers — full_name, Total Emprunts,       │ │
│ │ Taux de Retard %, Pénalités Totales (tri décroissant)  │ │
│ └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

- **Cartes** : `Emprunts par Usager`, `Taux de Retard %`,
  `Retard Moyen (jours, retards seuls)`, `Pénalités Totales`.
- **Barres 1** : `Taux de Retard %` par `DIM_USER[user_type]` (le contraste).
- **Barres 2** : `Total Emprunts` par `DIM_USER[faculty]`.
- **Table** : `full_name` + `Total Emprunts` + `Taux de Retard %` + `Pénalités Totales`.

---

## Tes mesures à créer

Toutes dans `mesures_samuel.dax` (table `_Mesures`). Les mesures de base
existent déjà dans le pbix, ne les recrée pas.

À créer : `Part Emprunts Branche %`, `Rang Branche`, `Charge Moyenne Branche (empr/j)`,
`Croissance Branche YoY %`, `Taux Annulation Réservations Branche %`,
`Attente Moyenne Branche (j)`, `Emprunts par Usager`, `Emprunts En Retard`,
`Taux de Retard %`, `Retard Moyen (jours, retards seuls)`, `Jours de Retard Cumulés`,
`Pénalités Totales`, `Pénalité Moyenne par Usager`, `Durée Moyenne de Prêt (j)`,
`Taux d'Activité Usagers %`.

## Rappels

- `Pénalités Totales` → formate en **€**. `Taux de Retard %` → en **%**.
- `Taux de Retard %` se rapporte aux emprunts **clôturés** (un emprunt en cours
  n'est pas « en retard »). C'est volontaire.
- `year_month` en axe → champ simple, pas la hiérarchie de dates.
