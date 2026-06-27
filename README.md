<div align="center">

# 📚 Library Analytics — Data Warehouse & Power BI

**An academic FR/BE library network — a 6-page Power BI dashboard on a fact-constellation star schema, from reproducible synthetic data to a prescriptive stock-reallocation engine.**

[![Power BI](https://img.shields.io/badge/Power_BI-Desktop-F2C811?logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![pandas](https://img.shields.io/badge/pandas-data-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-rng-013243?logo=numpy&logoColor=white)](https://numpy.org/)
[![Model](https://img.shields.io/badge/Model-Constellation_(3_facts_·_5_dims)-2ea44f)](#-architecture--star-constellation-schema)
[![Reproducible](https://img.shields.io/badge/Data-Reproducible_(seed_42)-blue)](#-data-generator)
[![Language](https://img.shields.io/badge/Language-English-informational)]()
[![Status](https://img.shields.io/badge/Status-Work_in_progress-orange)](#-project-status)

</div>

---

## 📖 Overview

A network of academic libraries across France and Belgium. The project models loans,
reservations and monthly stock snapshots in a **fact-constellation** warehouse and
delivers a **6-page Power BI report** answering 12 business questions — culminating in
a **prescriptive reallocation engine** that shows how much unmet demand could be
covered just by redistributing idle stock, with **no new purchases**.

The data is **100 % synthetic and reproducible** (fixed seed), with **deliberately
injected, correlated trends** so every page tells a piece of one coherent story:
*the network is imbalanced, and we know how to rebalance it.*

> **Team (EFREI):** Mathieu ALASSOEUR · Samuel DA SILVA · Raphaël THEBAULT
> **Work split:** pages 1–2 (Raphaël) · 3–4 (Samuel) · 5–6 (Mathieu).

---

## 🗂️ Repository structure

```
library-analytics-data-warehouse/
├── README.md                         ← you are here (single source of truth)
├── 0_COMMON_MODEL/
│   ├── library_analytics.pbix        ← THE master report (model + 6 pages)
│   ├── 00_base_measures_EN.dax       shared base measures
│   └── data_csv/                     the 8 CSVs (English, loaded by the .pbix)
├── 1_RAPHAEL_pages_1_2/01_raphael_pages_1_2_EN.dax
├── 2_SAMUEL_pages_3_4/02_samuel_pages_3_4_EN.dax  (+ INSTRUCTIONS.md)
├── 3_MATHIEU_pages_5_6/03_mathieu_pages_5_6_EN.dax
└── 4_generator/
    ├── generate_data.py              reproducible generator (writes English CSVs)
    └── source_dimensions/            hand-authored dimension sources
```

All measures live in a dedicated `_Mesures` table, organised into per-page display
folders. The whole model — columns, measures, data values — is in **English**.

---

## 🌌 Architecture — star (constellation) schema

Three fact tables share five conformed dimensions (a *fact constellation*):

| Fact table | Grain | Key business columns |
|---|---|---|
| `FACT_LOAN` | one loan | durations, overdue days, penalties |
| `FACT_RESERVATION` | one reservation | status (`fulfilled`/`pending`/`cancelled`), wait days |
| `FACT_INVENTORY_SNAPSHOT` | book × branch × month | copies, utilization, stock-outs, unmet demand, reallocation priority |

**Shared dimensions:** `DIM_DATE`, `DIM_BOOK`, `DIM_BRANCH`, `DIM_CATEGORY`, `DIM_USER`.

`DIM_BOOK` holds **book attributes only** — the old inventory columns (`total_copies`,
`available_copies`, `utilization_rate`, …) are **facts** and live in
`FACT_INVENTORY_SNAPSHOT` at the right grain (book × branch × month). Only
`base_total_copies` is kept on the book as a catalogue allocation attribute.

```text
                 ┌───────────┐
                 │ DIM_DATE  │
                 └─────┬─────┘
        ┌──────────────┼──────────────┐
        │              │              │
  ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼──────────────────┐
  │ FACT_LOAN │  │FACT_RESERV│  │FACT_INVENTORY_SNAPSHOT │
  └─┬───┬───┬─┘  └─┬───┬───┬─┘  └────┬────────┬─────┬─────┘
    │   │   │      │   │   │         │        │     │
 DIM_USER DIM_BOOK DIM_BRANCH   DIM_CATEGORY  …   (shared dims)
```

---

## 🔗 Relationships (14)

Import the 5 dimensions first, then the 3 facts. All CSVs are **UTF-8, comma-separated**.

| Dimension (1) | Fact (\*) | Key |
|---|---|---|
| DIM_DATE | FACT_LOAN | date_id |
| DIM_USER | FACT_LOAN | user_id |
| DIM_BOOK | FACT_LOAN | book_id |
| DIM_BRANCH | FACT_LOAN | branch_id |
| DIM_CATEGORY | FACT_LOAN | category_id |
| DIM_DATE | FACT_RESERVATION | date_id |
| DIM_USER | FACT_RESERVATION | user_id |
| DIM_BOOK | FACT_RESERVATION | book_id |
| DIM_BRANCH | FACT_RESERVATION | branch_id |
| DIM_CATEGORY | FACT_RESERVATION | category_id |
| DIM_DATE | FACT_INVENTORY_SNAPSHOT | date_id |
| DIM_BOOK | FACT_INVENTORY_SNAPSHOT | book_id |
| DIM_BRANCH | FACT_INVENTORY_SNAPSHOT | branch_id |
| DIM_CATEGORY | FACT_INVENTORY_SNAPSHOT | category_id |

Each relationship: **one-to-many (1:\*)**, cross-filter **Single** (dimension filters fact).

> ⚠️ **Pitfalls (must respect):**
> - **Do NOT create** a `DIM_BOOK → DIM_CATEGORY` relationship. Category joins the facts
>   directly via `category_id`. Adding a book→category edge creates an ambiguous
>   (snowflake) path and Power BI silently **deactivates** the three direct
>   fact→category relationships — category visuals then stop filtering.
> - **Mark `DIM_DATE` as a date table** on `full_date` (enables time intelligence:
>   YoY, MoM, YTD). Turn off **Auto date/time** to avoid hidden auto date tables.
> - **`return_date` blank** in `FACT_LOAN` = loan still open. Normal, not an error.
> - **Snapshot ≠ sum:** never sum `FACT_INVENTORY_SNAPSHOT` columns across time. Aggregate
>   within a month, and pin the latest snapshot for "current state" KPIs.
> - **Decimal columns** (`utilization_rate`, `availability_rate`, `penalty_amount`,
>   `popularity_score`) must be typed **Decimal** with **English (US)** locale (the CSVs
>   use a dot). If imported as text, `AVERAGE`/`SUM` break.

---

## 📚 Data dictionary

### `FACT_LOAN` — grain: one loan
| Column | Type | Description |
|---|---|---|
| `loan_id` | text | Technical loan key. |
| `date_id` | int | Date key (→ DIM_DATE). |
| `event_date` | date | Loan date (readable). |
| `user_id` | int | User key (→ DIM_USER). |
| `book_id` | int | Book key (→ DIM_BOOK). |
| `branch_id` | int | Branch key (→ DIM_BRANCH). |
| `category_id` | int | Category key (→ DIM_CATEGORY) = the book's category. |
| `loan_date` / `due_date` / `return_date` | date | Borrowed / due / actual return. `return_date` blank = open loan. |
| `loan_duration_days` | int | Effective loan duration (days). |
| `days_overdue` | int | Overdue days (0 if on time). |
| `penalty_amount` | decimal | Simulated penalty (€0.30 / overdue day). |
| `quantity` | int | Quantity loaned (1). |

### `FACT_RESERVATION` — grain: one reservation
| Column | Type | Description |
|---|---|---|
| `reservation_id` | text | Technical reservation key. |
| `date_id`, `event_date`, `user_id`, `book_id`, `branch_id`, `category_id` | int/date | Keys + readable date. |
| `reservation_status` | text | `fulfilled`, `pending` or `cancelled`. |
| `wait_days` | int | Wait before fulfilment / abandonment. |
| `quantity` | int | Quantity reserved (1). |

### `FACT_INVENTORY_SNAPSHOT` — grain: book × branch × month
| Column | Type | Description |
|---|---|---|
| `snapshot_id` | text | Technical snapshot key. |
| `date_id`, `snapshot_date` | int/date | Month-end snapshot date (→ DIM_DATE). |
| `book_id`, `branch_id`, `category_id` | int | Keys. |
| `total_copies` | int | Copies allocated to this book in this branch. |
| `available_copies` | int | Copies available at snapshot time. |
| `active_loans` | int | Copies currently on loan. |
| `utilization_rate` | decimal | `active_loans / total_copies` (0–1). |
| `availability_rate` | decimal | `available_copies / total_copies` (0–1). |
| `out_of_stock` | bool | `True` if `available_copies = 0`. |
| `loan_count_total` | int | Cumulative loans for this book × branch. |
| `loan_count_120d` | int | Loans in the 120 days before the snapshot. |
| `unsatisfied_reservations` | int | Estimated unmet demand (missing copies). |
| `reallocation_priority` | text | `Critical`, `High`, `Normal`, `Low`. |

### Dimensions
- **`DIM_DATE`** — academic calendar (month, quarter, year, exam flag, `academic_period` ∈ {`Back-to-School`, `Exams`, `Off-Exam`, `Summer Break`}). Mark as date table on `full_date`.
- **`DIM_BOOK`** — title, author, category, academic level, language, `demand_tier` (`top`/`high`/`medium`/`low`), `base_total_copies`, `popularity_score`.
- **`DIM_CATEGORY`** — category (e.g. `Law`, `Health`, `Data Science & AI`…), subcategory, discipline cluster.
- **`DIM_BRANCH`** — library, city, country, type (`University`/`School`/`IUT`/`BUT`), coordinates, profile (6 cities: Paris, Lyon, Lille, Marseille, Brussels, Liège).
- **`DIM_USER`** — user, type (`Student`/`Researcher`/`Faculty`), faculty, level, country, preferred branch.

---

## 📈 Analytical patterns (what the data deliberately contains)

Trends are injected on purpose and **correlated** (measured on seed 42):

1. **Book Pareto (80/20).** The top 20 % of books capture **~44 %** of loans; the long
   tail of `low` books stays cold. → targeted-acquisition story.
2. **Exam × category interaction.** Loans spike during exams, **but not for everyone**:
   Law ×2.8, Data Science & AI ×2.9, Health ×2.7; Literature ×1.8, Humanities ×1.6.
   An *interaction effect*, more telling than a flat average.
3. **Branch load asymmetry.** Paris-Centre ~4,350 · Lyon ~3,500 · Brussels ~3,100 ·
   Lille ~2,170 · Marseille ~1,600 · Liège ~1,260.
4. **Annual growth + an emerging hub.** Network grows **22.8 → 24.4 → 28.6 loans/day**
   (2024→2026). **Brussels** rises fastest (share **17.9 % → 21.7 %**). September peak,
   summer trough.
5. **User segmentation.** Overdue rate by type: **Student 24.8 %**, Researcher 15.3 %,
   Faculty 14.5 %. Researchers/faculty borrow more and longer (28 d vs 14 d).
6. **Stock reallocation — the differentiator.** Tense branches (Paris, Brussels,
   Marseille) are **under-allocated** vs demand; calm ones (Lille, Liège) hold **idle
   stock**. Headline (last month): **124 critical pairs**, **353 units of unmet demand**,
   and **~32 % of that gap is coverable by redistributing idle stock alone**.
7. **Reservation dynamics.** Wait time and cancel rate track branch tension (Paris/Brussels
   ~7.6 d wait, ~17–18 % cancel; Liège ~0.7 d, ~3 %).

> Example (Marketing Analytics, Mar 2025): Paris/Lyon/Brussels/Marseille at full
> utilization with unmet demand, while **Lille and Liège** hold spare copies → a direct
> **transfer order**: move copies from Lille/Liège to Paris/Brussels.

---

## ❓ The 12 questions → 6 pages

| Pages | Owner | Questions |
|---|---|---|
| 1–2 | Raphaël | Q1 volume/growth · Q2 emerging hub · Q3 seasonality · Q4 exams × category |
| 3–4 | Samuel | Q5 branch load · Q6 overdue by profile · Q7 cost of overdue |
| 5–6 | Mathieu | Q8 books to prioritise · Q9 backlogged demand · Q10 stock tension · Q11/Q12 reallocation |

---

## 🛠️ Data generator

Reproducible (fixed seed). Generates French internally (trend logic), writes **English**
CSVs directly to the model folder. One file — no separate translation step.

```powershell
cd 4_generator
pip install pandas numpy
python generate_data.py                       # -> ../0_COMMON_MODEL/data_csv/ (English)
python generate_data.py --seed 42 --out ../0_COMMON_MODEL/data_csv
python generate_data.py --keep-french         # raw FR (debug only)
```

The script prints sanity checks (16,000 loans · 3,600 reservations · 124 critical pairs ·
353 unmet · ~32.29 % coverage). Trend dictionaries (demand weights, branch tension,
exam sensitivity, faculty→category affinity, loan policy) sit at the top of `build()` —
tweak and rerun.

---

## 🔁 Reproduce the report

1. Open `0_COMMON_MODEL/library_analytics.pbix` in Power BI Desktop.
2. If you regenerate data, **Refresh** (column names are stable → relationships, types
   and measures survive).
3. Verify the sanity figures: `Total Loans` = 16,000 · `Total Reservations` = 3,600 ·
   `Critical Pairs (Last Month)` = 124 · `Reallocation Coverage Rate %` ≈ 32.29 %.

> **Portability:** the CSV source path is a Power Query parameter `DataFolder`. Set it to
> your local `0_COMMON_MODEL/data_csv` path after cloning.

---

## 🚦 Project status

| Page | Owner | Status |
|---|---|---|
| 1 — Overview | Raphaël | ✅ built (EN) |
| 2 — Time & exams | Raphaël | ✅ built (EN) |
| 3 — Network & branches | Samuel | ⏳ to build (measures ready) |
| 4 — Users & overdue | Samuel | ⏳ to build (measures ready) |
| 5 — Catalogue & demand | Mathieu | ✅ built (EN) |
| 6 — Stock & reallocation | Mathieu | ✅ built (EN) |

**Remaining:** Samuel's pages 3–4 · final theme/title harmonisation · cross-QA of the 6
pages against the 12 questions.

---

<div align="center">
<sub>Academic project · EFREI Paris — Panthéon-Assas · Business Intelligence & Analytics</sub>
</div>
