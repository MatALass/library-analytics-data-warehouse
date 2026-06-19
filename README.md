# Library Analytics — Projet Power BI (équipe)

Réseau de bibliothèques académiques FR/BE. Dashboard Power BI à 6 pages, modèle en
**constellation** (3 facts + 5 dimensions). Organisation **par personne** pour que
chacun avance sans dépendre des autres.

## Structure

```
library-analytics-projet/
├── 0_MODELE_COMMUN/          ← TOUT LE MONDE COMMENCE ICI
│   ├── COMMENCER_ICI.md          guide de démarrage + pièges
│   ├── MODELE_pages_5_6.pbix     fichier de départ (modèle + mesures + pages 5-6)
│   ├── mesures_base.dax          mesures partagées (déjà dans le pbix)
│   ├── data_csv/                 les 8 CSV (déjà importés dans le pbix)
│   ├── SCHEMA_constellation.md   le modèle expliqué
│   ├── RELATIONS_POWERBI.md      les 14 relations
│   └── DICTIONNAIRE_DONNEES.md   description des colonnes
│
├── RAPHAEL_pages_1_2/        ← Raphaël : INSTRUCTIONS.md + mesures_raphael.dax
├── SAMUEL_pages_3_4/         ← Samuel  : INSTRUCTIONS.md + mesures_samuel.dax
├── MATHIEU_pages_5_6/        ← Mathieu : FAIT (référence)
│
├── PATTERNS_ANALYTIQUES.md   ce que les données contiennent (tendances + chiffres)
└── generator/                générateur reproductible des données (seed fixe)
```

## Comment ça marche (workflow)

1. **Chacun ouvre `0_MODELE_COMMUN/MODELE_pages_5_6.pbix`** et l'enregistre sous
   son nom dans son dossier. Le modèle, les relations, les types et les mesures de
   base sont **déjà faits** — personne ne refait le modèle.
2. **Chacun lit son `INSTRUCTIONS.md`** : ses pages, les questions à traiter, la
   réponse attendue, la maquette, ses mesures à créer.
3. **Chacun construit ses 2 pages** dans sa copie.
4. **Intégration finale** (voir ci-dessous).

## Les 12 questions, réparties

| Pages | Qui | Questions |
|---|---|---|
| 1–2 | Raphaël | Q1 volume/croissance, Q2 hub émergent, Q3 saisonnalité, Q4 examens × catégorie |
| 3–4 | Samuel | Q5 charge des branches, Q6 retards par profil, Q7 coût des retards |
| 5–6 | Mathieu | Q8 livres à prioriser, Q9 demande refoulée, Q10 tension stock, Q11/Q12 réallocation |

Détail et réponses attendues dans chaque `INSTRUCTIONS.md`.

## Intégration finale (important : Power BI ne se fusionne pas comme du code)

On ne « merge » pas trois `.pbix`. La méthode :
1. On part de **MODELE_pages_5_6.pbix** comme fichier **maître** (il a déjà les
   pages 5-6).
2. Raphaël et Samuel ouvrent leur fichier ET le maître côte à côte. Sur chaque
   page, ils **sélectionnent tous les visuels** (Ctrl+A), **copient** (Ctrl+C),
   puis **collent** dans une nouvelle page du maître (Ctrl+V).
3. Si une mesure manque après collage, on la récrée depuis le fichier
   `mesures_*.dax` correspondant (toutes les mesures vivent dans la table `_Mesures`).
4. Une fois les 6 pages dans le maître : passe d'harmonisation (thème, titres,
   formats, slicers) et **QA croisée** (chacun relit les pages des autres contre
   les questions).

Décider **dès maintenant** qui détient le fichier maître pour éviter les
divergences.

## Régénérer les données (optionnel)

```
cd generator
pip install pandas numpy
python generate_data.py
```
Seed fixe → mêmes données. Les tendances injectées sont documentées dans
`PATTERNS_ANALYTIQUES.md`.
