# Semantic model

Generated from `powerbi/build_report.py` by `tools/export_model.py`. Do not edit by hand.
Review notes: [model_review.md](model_review.md).

## Tables

| Table | Role | Columns | Measures |
|---|---|---|---|
| `DIM_DATE` | date | 15 | 0 |
| `DIM_BOOK` | dimension | 13 | 0 |
| `DIM_BRANCH` | dimension | 9 | 0 |
| `DIM_CATEGORY` | dimension | 4 | 0 |
| `DIM_USER` | dimension | 12 | 0 |
| `FACT_LOAN` | fact | 14 | 37 |
| `FACT_RESERVATION` | fact | 10 | 8 |
| `FACT_INVENTORY_SNAPSHOT` | fact | 16 | 13 |

## Relationships (14)

| From (many) | To (one) |
|---|---|
| `FACT_LOAN[date_id]` | `DIM_DATE[date_id]` |
| `FACT_LOAN[user_id]` | `DIM_USER[user_id]` |
| `FACT_LOAN[book_id]` | `DIM_BOOK[book_id]` |
| `FACT_LOAN[branch_id]` | `DIM_BRANCH[branch_id]` |
| `FACT_LOAN[category_id]` | `DIM_CATEGORY[category_id]` |
| `FACT_RESERVATION[date_id]` | `DIM_DATE[date_id]` |
| `FACT_RESERVATION[user_id]` | `DIM_USER[user_id]` |
| `FACT_RESERVATION[book_id]` | `DIM_BOOK[book_id]` |
| `FACT_RESERVATION[branch_id]` | `DIM_BRANCH[branch_id]` |
| `FACT_RESERVATION[category_id]` | `DIM_CATEGORY[category_id]` |
| `FACT_INVENTORY_SNAPSHOT[date_id]` | `DIM_DATE[date_id]` |
| `FACT_INVENTORY_SNAPSHOT[book_id]` | `DIM_BOOK[book_id]` |
| `FACT_INVENTORY_SNAPSHOT[branch_id]` | `DIM_BRANCH[branch_id]` |
| `FACT_INVENTORY_SNAPSHOT[category_id]` | `DIM_CATEGORY[category_id]` |

## Measures (58)


### 00 - Common

**Active Branches** (`FACT_LOAN`, format `#,0`)

```dax
DISTINCTCOUNT ( FACT_LOAN[branch_id] )
```

**Active Days** (`FACT_LOAN`, format `#,0`)

```dax
DISTINCTCOUNT ( FACT_LOAN[date_id] )
```

**Active Users** (`FACT_LOAN`, format `#,0`)

```dax
DISTINCTCOUNT ( FACT_LOAN[user_id] )
```

**Cancelled Reservations** (`FACT_RESERVATION`, format `#,0`)

```dax
CALCULATE ( [Total Reservations], FACT_RESERVATION[reservation_status] = "cancelled" )
```

**Closed Loans** (`FACT_LOAN`, format `#,0`)

```dax
CALCULATE ( COUNTROWS ( FACT_LOAN ), NOT ISBLANK ( FACT_LOAN[return_date] ) )
```

**Distinct Books Loaned** (`FACT_LOAN`, format `#,0`)

```dax
DISTINCTCOUNT ( FACT_LOAN[book_id] )
```

**Fulfilled Reservations** (`FACT_RESERVATION`, format `#,0`)

```dax
CALCULATE ( [Total Reservations], FACT_RESERVATION[reservation_status] = "fulfilled" )
```

**Loaned Quantity** (`FACT_LOAN`, format `#,0`)

```dax
SUM ( FACT_LOAN[quantity] )
```

**Open Loans** (`FACT_LOAN`, format `#,0`)

```dax
CALCULATE ( COUNTROWS ( FACT_LOAN ), ISBLANK ( FACT_LOAN[return_date] ) )
```

**Pending Reservations** (`FACT_RESERVATION`, format `#,0`)

```dax
CALCULATE ( [Total Reservations], FACT_RESERVATION[reservation_status] = "pending" )
```

**Total Loans** (`FACT_LOAN`, format `#,0`)

```dax
COUNTROWS ( FACT_LOAN )
```

**Total Reservations** (`FACT_RESERVATION`, format `#,0`)

```dax
COUNTROWS ( FACT_RESERVATION )
```

**_Last Snapshot Date** (`FACT_INVENTORY_SNAPSHOT`, format `0`)

> date_id of the latest monthly snapshot in the selected period.

```dax
CALCULATE ( MAX ( FACT_INVENTORY_SNAPSHOT[date_id] ), ALL ( FACT_INVENTORY_SNAPSHOT ), ALLSELECTED ( DIM_DATE ) )
```


### 01 - Overview

**Avg Daily Loans** (`FACT_LOAN`, format `#,0.0`)

```dax
DIVIDE ( [Total Loans], COUNTROWS ( DIM_DATE ) )
```

**Loans LM** (`FACT_LOAN`, format `#,0`)

```dax
CALCULATE ( [Total Loans], DATEADD ( DIM_DATE[full_date], -1, MONTH ) )
```

**Loans LY** (`FACT_LOAN`, format `#,0`)

```dax
CALCULATE ( [Total Loans], SAMEPERIODLASTYEAR ( DIM_DATE[full_date] ) )
```

**Loans MoM %** (`FACT_LOAN`, format `+0.0%;-0.0%;0.0%`)

```dax
VAR Prev = [Loans LM]
RETURN DIVIDE ( [Total Loans] - Prev, Prev )
```

**Loans YTD** (`FACT_LOAN`, format `#,0`)

> Academic year to date (September to August).

```dax
TOTALYTD ( [Total Loans], DIM_DATE[full_date], "08-31" )
```

**Loans YoY %** (`FACT_LOAN`, format `+0.0%;-0.0%;0.0%`)

```dax
VAR Prev = [Loans LY]
RETURN DIVIDE ( [Total Loans] - Prev, Prev )
```

**Running Total Loans** (`FACT_LOAN`, format `#,0`)

```dax
CALCULATE ( [Total Loans], FILTER ( ALL ( DIM_DATE ), DIM_DATE[full_date] <= MAX ( DIM_DATE[full_date] ) ) )
```

**Total Loans (Top 10 Users)** (`FACT_LOAN`, format `#,0`)

> Blank outside the top 10, so the bar chart keeps 10 bars without a visual filter.

```dax
IF (
    RANKX ( ALLSELECTED ( DIM_USER[full_name] ), [Total Loans],, DESC, DENSE ) <= 10,
    [Total Loans]
)
```


### 02 - Time & Exams

**Daily Loans (Exam Period)** (`FACT_LOAN`, format `#,0.0`)

```dax
DIVIDE ( [Loans (Exam Period)], [_Exam Days] )
```

**Daily Loans (Off-Exam)** (`FACT_LOAN`, format `#,0.0`)

```dax
DIVIDE ( [Loans (Off-Exam)], [_Off-Exam Days] )
```

**Exam Overload Index** (`FACT_LOAN`, format `#,0.00`)

```dax
DIVIDE ( [Daily Loans (Exam Period)], [Daily Loans (Off-Exam)] )
```

**Exam-Period Loans %** (`FACT_LOAN`, format `0.0%`)

```dax
DIVIDE ( [Loans (Exam Period)], [Total Loans] )
```

**Loans (Exam Period)** (`FACT_LOAN`, format `#,0`)

```dax
CALCULATE ( [Total Loans], DIM_DATE[is_exam_period] = TRUE () )
```

**Loans (Off-Exam)** (`FACT_LOAN`, format `#,0`)

```dax
CALCULATE ( [Total Loans], DIM_DATE[is_exam_period] = FALSE () )
```

**Weekend Loans %** (`FACT_LOAN`, format `0.0%`)

```dax
DIVIDE ( CALCULATE ( [Total Loans], DIM_DATE[is_weekend] = TRUE () ), [Total Loans] )
```

**_Exam Days** (`FACT_LOAN`, format `#,0`)

```dax
CALCULATE ( COUNTROWS ( DIM_DATE ), DIM_DATE[is_exam_period] = TRUE () )
```

**_Off-Exam Days** (`FACT_LOAN`, format `#,0`)

```dax
CALCULATE ( COUNTROWS ( DIM_DATE ), DIM_DATE[is_exam_period] = FALSE () )
```


### 03 - Network

**Avg Branch Daily Load** (`FACT_LOAN`, format `#,0.0`)

```dax
VAR _TotalDays = CALCULATE ( COUNTROWS ( DIM_DATE ), DIM_DATE[full_date] <= MAX ( DIM_DATE[full_date] ) )
RETURN DIVIDE ( [Total Loans], _TotalDays )
```

**Branch Loan Share %** (`FACT_LOAN`, format `0.0%`)

```dax
DIVIDE ( [Total Loans], CALCULATE ( [Total Loans], ALL ( DIM_BRANCH ) ) )
```


### 04 - Users

**Avg Loan Duration (days)** (`FACT_LOAN`, format `#,0.0`)

```dax
AVERAGE ( FACT_LOAN[loan_duration_days] )
```

**Avg Overdue Days (overdue only)** (`FACT_LOAN`, format `#,0.0`)

```dax
AVERAGEX ( FILTER ( FACT_LOAN, FACT_LOAN[days_overdue] > 0 ), FACT_LOAN[days_overdue] )
```

**Avg Penalty per User** (`FACT_LOAN`, format `#,0.00 €`)

```dax
DIVIDE ( [Total Penalties], [Active Users] )
```

**Loans per User** (`FACT_LOAN`, format `#,0.0`)

```dax
DIVIDE ( [Total Loans], [Active Users] )
```

**Overdue Loans** (`FACT_LOAN`, format `#,0`)

```dax
CALCULATE ( COUNTROWS ( FACT_LOAN ), FACT_LOAN[days_overdue] > 0 )
```

**Overdue Rate %** (`FACT_LOAN`, format `0.0%`)

> Overdue loans / closed loans: open loans always have 0 overdue days.

```dax
DIVIDE ( [Overdue Loans], [Closed Loans] )
```

**Total Penalties** (`FACT_LOAN`, format `#,0.00 €`)

```dax
SUM ( FACT_LOAN[penalty_amount] )
```


### 05 - Catalogue

**Avg Reservation Wait (days)** (`FACT_RESERVATION`, format `#,0.0`)

```dax
AVERAGE ( FACT_RESERVATION[wait_days] )
```

**Book Rank** (`FACT_LOAN`, format `0`)

```dax
IF ( HASONEVALUE ( DIM_BOOK[book_id] ), RANKX ( ALL ( DIM_BOOK[book_id] ), [Total Loans],, DESC, DENSE ) )
```

**Cumulative Loans % (Pareto)** (`FACT_LOAN`, format `0.0%`)

```dax
VAR CurLoans = [Total Loans]
VAR Books = ADDCOLUMNS ( ALLSELECTED ( DIM_BOOK[title] ), "@loans", [Total Loans] )
VAR Grand = SUMX ( Books, [@loans] )
VAR CumLoans = SUMX ( FILTER ( Books, [@loans] >= CurLoans ), [@loans] )
RETURN IF ( NOT ISBLANK ( CurLoans ), DIVIDE ( CumLoans, Grand ) )
```

**Demand Pressure (Resv per Loan)** (`FACT_RESERVATION`, format `#,0.00`)

```dax
DIVIDE ( [Total Reservations], [Total Loans] )
```

**Reservation Cancel Rate %** (`FACT_RESERVATION`, format `0.0%`)

```dax
DIVIDE ( [Cancelled Reservations], [Total Reservations] )
```

**Reservation Fulfillment Rate %** (`FACT_RESERVATION`, format `0.0%`)

```dax
DIVIDE ( [Fulfilled Reservations], [Total Reservations] )
```

**Top 20% Books Loan Share %** (`FACT_LOAN`, format `0.0%`)

```dax
VAR N = COUNTROWS ( ALL ( DIM_BOOK[book_id] ) )
VAR NbTop = ROUNDUP ( N * 0.2, 0 )
VAR T = ADDCOLUMNS ( ALL ( DIM_BOOK[book_id] ), "@l", [Total Loans] )
VAR TopBooks = TOPN ( NbTop, T, [@l], DESC )
RETURN DIVIDE ( SUMX ( TopBooks, [@l] ), SUMX ( T, [@l] ) )
```


### 06 - Stock

**Available Copies (Last Month)** (`FACT_INVENTORY_SNAPSHOT`, format `#,0`)

```dax
VAR d = [_Last Snapshot Date]
RETURN CALCULATE ( SUM ( FACT_INVENTORY_SNAPSHOT[available_copies] ), FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d ) )
```

**Avg Utilization (Last Month)** (`FACT_INVENTORY_SNAPSHOT`, format `0.0%`)

> Weighted by copies: a pair with 30 copies weighs more than a pair with 1.

```dax
VAR d = [_Last Snapshot Date]
RETURN
    CALCULATE (
        DIVIDE ( SUM ( FACT_INVENTORY_SNAPSHOT[active_loans] ), SUM ( FACT_INVENTORY_SNAPSHOT[total_copies] ) ),
        FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d )
    )
```

**Avg Utilization (Month)** (`FACT_INVENTORY_SNAPSHOT`, format `0.0%`)

> Weighted by copies.

```dax
DIVIDE ( SUM ( FACT_INVENTORY_SNAPSHOT[active_loans] ), SUM ( FACT_INVENTORY_SNAPSHOT[total_copies] ) )
```

**Critical Pairs (Last Month)** (`FACT_INVENTORY_SNAPSHOT`, format `#,0`)

```dax
VAR d = [_Last Snapshot Date]
RETURN CALCULATE ( COUNTROWS ( FACT_INVENTORY_SNAPSHOT ), FACT_INVENTORY_SNAPSHOT[reallocation_priority] = "Critical", FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d ) )
```

**Current Reallocation Priority** (`FACT_INVENTORY_SNAPSHOT`, format `default`)

```dax
VAR d = [_Last Snapshot Date]
RETURN
    CALCULATE (
        SELECTEDVALUE ( FACT_INVENTORY_SNAPSHOT[reallocation_priority] ),
        FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d ),
        ALL ( FACT_INVENTORY_SNAPSHOT[reallocation_priority] )
    )
```

**Idle Copies (Last Month)** (`FACT_INVENTORY_SNAPSHOT`, format `#,0`)

```dax
VAR d = [_Last Snapshot Date]
RETURN CALCULATE ( SUM ( FACT_INVENTORY_SNAPSHOT[available_copies] ), FACT_INVENTORY_SNAPSHOT[reallocation_priority] = "Low", FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d ) )
```

**Movable Idle Copies (Last Month)** (`FACT_INVENTORY_SNAPSHOT`, format `#,0`)

> Idle copies that can move while keeping one copy on site.

```dax
VAR d = [_Last Snapshot Date]
RETURN
    CALCULATE (
        SUMX ( FACT_INVENTORY_SNAPSHOT, MAX ( FACT_INVENTORY_SNAPSHOT[available_copies] - 1, 0 ) ),
        FACT_INVENTORY_SNAPSHOT[reallocation_priority] = "Low",
        FACT_INVENTORY_SNAPSHOT[available_copies] >= 2,
        FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d )
    )
```

**Out-of-Stock Rate % (Last Month)** (`FACT_INVENTORY_SNAPSHOT`, format `0.0%`)

```dax
VAR d = [_Last Snapshot Date]
RETURN
    CALCULATE (
        DIVIDE (
            CALCULATE ( COUNTROWS ( FACT_INVENTORY_SNAPSHOT ), FACT_INVENTORY_SNAPSHOT[out_of_stock] = TRUE () ),
            COUNTROWS ( FACT_INVENTORY_SNAPSHOT )
        ),
        FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d )
    )
```

**Reallocation Coverage Rate %** (`FACT_INVENTORY_SNAPSHOT`, format `0.0%`)

> Share of last month's unmet demand coverable by moving idle stock, with no new purchase.

```dax
DIVIDE ( [Movable Idle Copies (Last Month)], [Unsatisfied Demand (Last Month)] )
```

**Total Copies (Last Month)** (`FACT_INVENTORY_SNAPSHOT`, format `#,0`)

```dax
VAR d = [_Last Snapshot Date]
RETURN CALCULATE ( SUM ( FACT_INVENTORY_SNAPSHOT[total_copies] ), FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d ) )
```

**Unsatisfied Demand (Last Month)** (`FACT_INVENTORY_SNAPSHOT`, format `#,0`)

```dax
VAR d = [_Last Snapshot Date]
RETURN CALCULATE ( SUM ( FACT_INVENTORY_SNAPSHOT[unsatisfied_reservations] ), FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d ) )
```

**Unsatisfied Reservations (Month)** (`FACT_INVENTORY_SNAPSHOT`, format `#,0`)

```dax
SUM ( FACT_INVENTORY_SNAPSHOT[unsatisfied_reservations] )
```

## Pages

- **Overview**: Monthly Loans vs Last Year, Cumulative Loans, Loans by Category, Top 10 Users by Loans
- **Time & Exam Periods**: Daily Loans by Category: Exam vs Off-Exam, Loans by Academic Period, Weekly Loans: Exam vs Non-Exam Weeks, Weekend Loans Share
- **Network & Branches**: Loans by City, Branch Loan Share by City, Monthly Loans by City
- **Users & Overdue**: Overdue Rate by User Type, Loans by Faculty, Top Users by Loans & Penalties
- **Catalogue & Demand**: Loans by Category, Book Pareto: Loans & Cumulative Share, Book Demand & Reservations
- **Stock & Reallocation**: Branch Utilization (Last Month), Monthly Unmet Demand & Utilization, Reallocation Plan: Critical vs Idle Stock
