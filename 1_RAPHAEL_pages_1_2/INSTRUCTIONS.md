# INSTRUCTIONS — Raphaël (pages 1 et 2)

> Avant de commencer : lis `0_MODELE_COMMUN/COMMENCER_ICI.md`, ouvre
> `MODELE_pages_5_6.pbix`, enregistre-le sous ton nom. Le modèle est déjà fait.

Tu construis **2 pages** : une vue d'ensemble, et une analyse temporelle/examens.
Pour chaque question, la **réponse attendue** est indiquée — c'est ce que les
données contiennent, donc ce que tes visuels doivent faire ressortir et ce que tu
diras en soutenance.

---

## PAGE 1 — Synthèse & vue d'ensemble

### Questions auxquelles cette page répond

**Q1 — Quel est le volume d'activité du réseau et comment évolue-t-il ?**
Réponse attendue : **16 000 emprunts** sur la période (sept. 2024 → mai 2026),
avec une activité en **croissance** (≈ 22,8 → 28,6 emprunts/jour de 2024 à 2026).

**Q2 — La croissance est-elle portée par une branche en particulier ?**
Réponse attendue : oui, **Bruxelles** monte le plus vite (part qui passe de
~18 % à ~22 %). À détailler sur ta page mais aussi sur la page 3 de Samuel.

### Maquette (page 1280 × 720)

```
┌──────────────── Titre : "Synthèse du réseau" ────────────────┐
│  ▼ Année   ▼ Pays                                            │
├──────────┬──────────┬──────────┬───────────────────────────┤
│ [Total   │ [Usagers │ [Croiss. │ [Taux de Retard %]        │
│ Emprunts]│ Actifs]  │ YoY %]   │                           │
├──────────┴──────────┴──────────┴───────────────────────────┤
│ ┌─────────────────────────┐ ┌────────────────────────────┐ │
│ │ Emprunts par mois       │ │ Top 6 branches (barres)    │ │
│ │ (courbe, year_month)    │ │ Total Emprunts/branch_name │ │
│ └─────────────────────────┘ └────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

- **Cartes** : `Total Emprunts`, `Usagers Actifs`, `Croissance Emprunts YoY %`,
  `Taux de Retard %`.
- **Courbe** : `Total Emprunts` par `DIM_DATE[year_month]` (pic rentrée + creux été visibles).
- **Barres** : `Total Emprunts` par `DIM_BRANCH[branch_name]`, trié décroissant.

---

## PAGE 2 — Dynamique temporelle & examens

### Questions auxquelles cette page répond

**Q3 — Quand la demande explose-t-elle dans l'année ?**
Réponse attendue : pendant les **périodes d'examens** (≈ ×2,4 le volume quotidien
normal), avec un **pic de rentrée** en septembre et un **creux marqué l'été**
(juillet-août).

**Q4 — Les examens font-ils monter toutes les disciplines, ou certaines seulement ?**
Réponse attendue (le point fort de la page) : **certaines seulement**.
Droit ≈ ×2,8, Santé ≈ ×2,7, Data Science ≈ ×2,9 ; mais Littérature ≈ ×1,8 et
Sciences Humaines ≈ ×1,6. C'est un **effet d'interaction** (examens × catégorie),
plus parlant qu'une simple moyenne.

### Maquette

```
┌──────────── Titre : "Saisonnalité & examens" ────────────────┐
│  ▼ Année   ▼ Catégorie                                       │
├──────────────┬──────────────┬────────────────────────────────┤
│ [Empr/j      │ [Empr/j      │ [Indice Surintensité Examens]  │
│  Examens]    │  Hors exam.] │  (≈ ×2,4)                      │
├──────────────┴──────────────┴────────────────────────────────┤
│ ┌────────────────────────────────────────────────────────┐   │
│ │ Emprunts par mois, COULEUR = academic_period           │   │
│ │ (Rentrée / Examens / Hors examens / Vacances été)      │   │
│ └────────────────────────────────────────────────────────┘   │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ Indice Surintensité Examens PAR CATÉGORIE (barres)     │   │
│ │ axe : DIM_CATEGORY[category], trié décroissant         │   │
│ └────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

- **Cartes** : `Emprunts par Jour (Examens)`, `Emprunts par Jour (Hors Examens)`,
  `Indice Surintensité Examens`.
- **Courbe** : `Total Emprunts` par `year_month`, légende `academic_period`.
- **Barres (le punch)** : `Indice Surintensité Examens` par `category`, trié.

---

## Tes mesures à créer

Toutes dans `mesures_raphael.dax` (table `_Mesures`). Les mesures de base
(`Total Emprunts`, `Usagers Actifs`, `Taux de Retard %`…) **existent déjà** dans
le pbix, tu ne les recrées pas.

À créer : `Emprunts Moyens par Jour`, `Emprunts YTD`, `Croissance Emprunts YoY %`,
`Variation Emprunts MoM %`, `Emprunts Période Examens`, `Emprunts Hors Examens`,
`Emprunts par Jour (Examens)`, `Emprunts par Jour (Hors Examens)`,
`Indice Surintensité Examens`, `Part Emprunts en Examens %`, `Emprunts Week-end %`.

## Rappels

- `year_month` en axe → choisir le champ simple, pas la hiérarchie de dates.
- Formate : `%` sur les taux, séparateur de milliers sur les compteurs.
- Garde le même style de titre/slicers que les autres pages (on harmonisera à la fin).
