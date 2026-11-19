# Model review

Review of the first version of the report, `legacy/library_analytics.pbix` (November 2026). The model was read with `tools/export_model.py` and every figure of the README was recomputed from the CSVs in `tests/test_kpis.py`.

## What is right

- **Schema.** 3 facts, 5 conformed dimensions, 14 relationships, all one-to-many with single cross-filter. No `DIM_BOOK → DIM_CATEGORY` edge, so the category filters stay active.
- **Date table.** `DIM_DATE` is marked as a date table and auto date/time is off (no hidden `LocalDateTable_*`).
- **Snapshots.** The "Last Month" measures pin the latest snapshot instead of summing stock over time.
- **Headline figures.** 16,000 loans, 3,600 reservations, 124 critical pairs, 353 units of unmet demand, 32.29 % coverage: all match the CSVs.
- **Reproducibility.** `python generate_data.py` rebuilds the 8 CSVs byte for byte.

## README figures that were wrong (fixed in this PR)

| Claim | README before | Report and CSVs | Why |
|---|---|---|---|
| Top 20 % of books, share of loans | ~44 % | 46.4 % | The measure takes ROUNDUP(72 × 0.2) = 15 books. |
| Overdue rate, Student / Researcher / Faculty | 24.8 / 15.3 / 14.5 % | 26.1 / 16.7 / 15.8 % | The README divided by all loans, the report divides by closed loans. Open loans always have 0 overdue days, so the report is the right one. |

## Fixes (applied in the PBIP report)

The report is now generated from `powerbi/build_report.py`, so these fixes are applied in code. `tests/test_powerbi.py` checks that they stay applied.

### 1. Utilization should be weighted by copies (page 6)

`Avg Utilization (Last Month)` averages `utilization_rate` row by row. A pair with 1 copy weighs as much as a pair with 30 copies. On the last month that gives 71.9 % instead of 77.7 % for the copy-weighted utilization, so the network looks less tense than it is.

```dax
Avg Utilization (Last Month) =
VAR d = [_Last Snapshot Date]
RETURN
    CALCULATE (
        DIVIDE (
            SUM ( FACT_INVENTORY_SNAPSHOT[active_loans] ),
            SUM ( FACT_INVENTORY_SNAPSHOT[total_copies] )
        ),
        FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d )
    )

Avg Utilization (Month) =
DIVIDE (
    SUM ( FACT_INVENTORY_SNAPSHOT[active_loans] ),
    SUM ( FACT_INVENTORY_SNAPSHOT[total_copies] )
)
```

The names stay the same, so the visuals keep working.

### 2. Year-to-date should follow the academic year (page 1)

`Loans YTD` resets on 1 January, in the middle of the academic year (September to August, as in `DIM_DATE[academic_year]`).

```dax
Loans YTD = TOTALYTD ( [Total Loans], DIM_DATE[full_date], "08-31" )
```

### 3. Model hygiene

- `Current Reallocation Priority` gets the `06 - Stock` display folder.
- Foreign keys and raw numbers of the three facts are hidden: visuals use dimension columns and measures.
- `DIM_USER[preferred_branch_id]` is hidden and no longer summarized.
- `DataFolder` defaults to `C:\pbip\library-analytics-data-warehouse\data\` instead of a local path from the course.

### 4. Also changed in the rebuild

- **Top 10 users** chart: the old report filtered the visual; the new measure `Total Loans (Top 10 Users)` returns blank outside the top 10, so the rule is in the model and visible in `docs/model.md`.
- **Map of cities** replaced by a bar chart: the Azure map needs a tenant setting and shows six cities poorly.
- **Filter panel** with bookmark buttons replaced by slicers in the header of each page.
- **Colour theme** (`powerbi/theme.json`): the old report used the default theme.

## Still to do

- [ ] Open the PBIP in Power BI Desktop, refresh, check the sanity figures, then delete `legacy/`.
- [ ] Export one screenshot per page to `docs/img/` and show them in the README: a recruiter will not open a Power BI file.
