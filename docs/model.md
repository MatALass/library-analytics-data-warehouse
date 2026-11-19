# Semantic model

Generated from `library_analytics.pbix` by `tools/export_model.py`. Do not edit by hand.
Review notes and fixes to apply in Power BI Desktop: [model_review.md](model_review.md).

## Tables

| Table | Columns |
|---|---|
| `DIM_BOOK` | 13 |
| `DIM_BRANCH` | 9 |
| `DIM_CATEGORY` | 4 |
| `DIM_DATE` | 15 |
| `DIM_USER` | 12 |
| `FACT_INVENTORY_SNAPSHOT` | 16 |
| `FACT_LOAN` | 14 |
| `FACT_RESERVATION` | 10 |
| `_Measures` | 1 |

## Relationships (14)

| From (many) | To (one) | Active | Filter |
|---|---|---|---|
| `FACT_INVENTORY_SNAPSHOT[book_id]` | `DIM_BOOK[book_id]` | yes | Single |
| `FACT_INVENTORY_SNAPSHOT[category_id]` | `DIM_CATEGORY[category_id]` | yes | Single |
| `FACT_INVENTORY_SNAPSHOT[branch_id]` | `DIM_BRANCH[branch_id]` | yes | Single |
| `FACT_INVENTORY_SNAPSHOT[date_id]` | `DIM_DATE[date_id]` | yes | Single |
| `FACT_LOAN[book_id]` | `DIM_BOOK[book_id]` | yes | Single |
| `FACT_LOAN[category_id]` | `DIM_CATEGORY[category_id]` | yes | Single |
| `FACT_LOAN[branch_id]` | `DIM_BRANCH[branch_id]` | yes | Single |
| `FACT_LOAN[date_id]` | `DIM_DATE[date_id]` | yes | Single |
| `FACT_LOAN[user_id]` | `DIM_USER[user_id]` | yes | Single |
| `FACT_RESERVATION[book_id]` | `DIM_BOOK[book_id]` | yes | Single |
| `FACT_RESERVATION[category_id]` | `DIM_CATEGORY[category_id]` | yes | Single |
| `FACT_RESERVATION[branch_id]` | `DIM_BRANCH[branch_id]` | yes | Single |
| `FACT_RESERVATION[date_id]` | `DIM_DATE[date_id]` | yes | Single |
| `FACT_RESERVATION[user_id]` | `DIM_USER[user_id]` | yes | Single |

## Measures (57)

### (no folder)

| Measure | DAX |
|---|---|
| Current Reallocation Priority | `VAR d = [_Last Snapshot Date] RETURN CALCULATE ( SELECTEDVALUE ( FACT_INVENTORY_SNAPSHOT[reallocation_priority] ), FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d ), ALL ( FACT_INVENTORY_SNAPSHOT[reallocation_priority] ) )` |

### 00 - Common Model

| Measure | DAX |
|---|---|
| Active Branches | `DISTINCTCOUNT ( FACT_LOAN[branch_id] )` |
| Active Days | `DISTINCTCOUNT ( FACT_LOAN[date_id] )` |
| Active Users | `DISTINCTCOUNT ( FACT_LOAN[user_id] )` |
| Cancelled Reservations | `CALCULATE ( [Total Reservations], FACT_RESERVATION[reservation_status] = "cancelled" )` |
| Closed Loans | `CALCULATE ( COUNTROWS ( FACT_LOAN ), NOT ISBLANK ( FACT_LOAN[return_date] ) )` |
| Distinct Books Loaned | `DISTINCTCOUNT ( FACT_LOAN[book_id] )` |
| Fulfilled Reservations | `CALCULATE ( [Total Reservations], FACT_RESERVATION[reservation_status] = "fulfilled" )` |
| Loaned Quantity | `SUM ( FACT_LOAN[quantity] )` |
| Open Loans | `CALCULATE ( COUNTROWS ( FACT_LOAN ), ISBLANK ( FACT_LOAN[return_date] ) )` |
| Pending Reservations | `CALCULATE ( [Total Reservations], FACT_RESERVATION[reservation_status] = "pending" )` |
| Total Loans | `COUNTROWS ( FACT_LOAN )` |
| Total Reservations | `COUNTROWS ( FACT_RESERVATION )` |
| _Last Snapshot Date | `CALCULATE ( MAX ( FACT_INVENTORY_SNAPSHOT[date_id] ), ALL ( FACT_INVENTORY_SNAPSHOT ), ALLSELECTED ( DIM_DATE ) )` |

### 01 - Page 1

| Measure | DAX |
|---|---|
| Avg Daily Loans | `DIVIDE ( [Total Loans], COUNTROWS ( DIM_DATE ) )` |
| Loans LM | `CALCULATE ( [Total Loans], DATEADD ( DIM_DATE[full_date], -1, MONTH ) )` |
| Loans LY | `CALCULATE ( [Total Loans], SAMEPERIODLASTYEAR ( DIM_DATE[full_date] ) )` |
| Loans MoM % | `VAR Prev = [Loans LM] RETURN DIVIDE ( [Total Loans] - Prev, Prev )` |
| Loans YTD | `TOTALYTD ( [Total Loans], DIM_DATE[full_date] )` |
| Loans YoY % | `VAR Prev = [Loans LY] RETURN DIVIDE ( [Total Loans] - Prev, Prev )` |
| Running Total Loans | `CALCULATE ( [Total Loans], FILTER ( ALL ( DIM_DATE ), DIM_DATE[full_date] <= MAX ( DIM_DATE[full_date] ) ) )` |

### 02 - Page 2

| Measure | DAX |
|---|---|
| Daily Loans (Exam Period) | `DIVIDE ( [Loans (Exam Period)], [_Exam Days] )` |
| Daily Loans (Off-Exam) | `DIVIDE ( [Loans (Off-Exam)], [_Off-Exam Days] )` |
| Exam Overload Index | `DIVIDE ( [Daily Loans (Exam Period)], [Daily Loans (Off-Exam)] )` |
| Exam-Period Loans % | `DIVIDE ( [Loans (Exam Period)], [Total Loans] )` |
| Loans (Exam Period) | `CALCULATE ( [Total Loans], DIM_DATE[is_exam_period] = TRUE () )` |
| Loans (Off-Exam) | `CALCULATE ( [Total Loans], DIM_DATE[is_exam_period] = FALSE () )` |
| Weekend Loans % | `DIVIDE ( CALCULATE ( [Total Loans], DIM_DATE[is_weekend] = TRUE () ), [Total Loans] )` |
| _Exam Days | `CALCULATE ( COUNTROWS ( DIM_DATE ), DIM_DATE[is_exam_period] = TRUE () )` |
| _Off-Exam Days | `CALCULATE ( COUNTROWS ( DIM_DATE ), DIM_DATE[is_exam_period] = FALSE () )` |

### 03 - Page 3

| Measure | DAX |
|---|---|
| Avg Branch Daily Load | `VAR _TotalDays = CALCULATE( COUNTROWS( DIM_DATE ), DIM_DATE[full_date] <= MAX(DIM_DATE[full_date]) ) RETURN DIVIDE( [Total Loans], _TotalDays )` |
| Branch Loan Share % | `VAR _BranchTotal = [Total Loans] VAR _GrandTotal = CALCULATE( [Total Loans], ALL( DIM_BRANCH ) ) RETURN DIVIDE( _BranchTotal, _GrandTotal )` |

### 04 - Page 4

| Measure | DAX |
|---|---|
| Avg Loan Duration (days) | `AVERAGE ( FACT_LOAN[loan_duration_days] )` |
| Avg Overdue Days (overdue only) | `AVERAGEX ( FILTER ( FACT_LOAN, FACT_LOAN[days_overdue] > 0 ), FACT_LOAN[days_overdue] )` |
| Avg Penalty per User | `DIVIDE ( [Total Penalties], [Active Users] )` |
| Loans per User | `DIVIDE ( [Total Loans], [Active Users] )` |
| Overdue Loans | `CALCULATE ( COUNTROWS ( FACT_LOAN ), FACT_LOAN[days_overdue] > 0 )` |
| Overdue Rate % | `DIVIDE ( [Overdue Loans], [Closed Loans] )` |
| Total Penalties | `SUM ( FACT_LOAN[penalty_amount] )` |

### 05 - Page 5

| Measure | DAX |
|---|---|
| Avg Reservation Wait (days) | `AVERAGE ( FACT_RESERVATION[wait_days] )` |
| Book Rank | `IF ( HASONEVALUE ( DIM_BOOK[book_id] ), RANKX ( ALL ( DIM_BOOK[book_id] ), [Total Loans],, DESC, DENSE ) )` |
| Cumulative Loans % (Pareto) | `VAR CurLoans = [Total Loans] VAR Books = ADDCOLUMNS ( ALLSELECTED ( DIM_BOOK[title] ), "@loans", [Total Loans] ) VAR Grand = SUMX ( Books, [@loans] ) VAR CumLoans = SUMX ( FILTER ( Books, [@loans] >= CurLoans ), [@loans] ) RETURN IF ( NOT ISBLANK ( CurLoans ), DIVIDE ( CumLoans, Grand ) )` |
| Demand Pressure (Resv per Loan) | `DIVIDE ( [Total Reservations], [Total Loans] )` |
| Reservation Cancel Rate % | `DIVIDE ( [Cancelled Reservations], [Total Reservations] )` |
| Reservation Fulfillment Rate % | `DIVIDE ( [Fulfilled Reservations], [Total Reservations] )` |
| Top 20% Books Loan Share % | `VAR N = COUNTROWS ( ALL ( DIM_BOOK[book_id] ) ) VAR NbTop = ROUNDUP ( N * 0.2, 0 ) VAR T = ADDCOLUMNS ( ALL ( DIM_BOOK[book_id] ), "@l", [Total Loans] ) VAR TopBooks = TOPN ( NbTop, T, [@l], DESC ) RETURN DIVIDE ( SUMX ( TopBooks, [@l] ), SUMX ( T, [@l] ) )` |

### 06 - Page 6

| Measure | DAX |
|---|---|
| Available Copies (Last Month) | `VAR d = [_Last Snapshot Date] RETURN CALCULATE ( SUM ( FACT_INVENTORY_SNAPSHOT[available_copies] ), FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d ) )` |
| Avg Utilization (Last Month) | `VAR d = [_Last Snapshot Date] RETURN CALCULATE ( AVERAGE ( FACT_INVENTORY_SNAPSHOT[utilization_rate] ), FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d ) )` |
| Avg Utilization (Month) | `AVERAGE ( FACT_INVENTORY_SNAPSHOT[utilization_rate] )` |
| Critical Pairs (Last Month) | `VAR d = [_Last Snapshot Date] RETURN CALCULATE ( COUNTROWS ( FACT_INVENTORY_SNAPSHOT ), FACT_INVENTORY_SNAPSHOT[reallocation_priority] = "Critical", FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d ) )` |
| Idle Copies (Last Month) | `VAR d = [_Last Snapshot Date] RETURN CALCULATE ( SUM ( FACT_INVENTORY_SNAPSHOT[available_copies] ), FACT_INVENTORY_SNAPSHOT[reallocation_priority] = "Low", FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d ) )` |
| Movable Idle Copies (Last Month) | `VAR d = [_Last Snapshot Date] RETURN CALCULATE ( SUMX ( FACT_INVENTORY_SNAPSHOT, MAX ( FACT_INVENTORY_SNAPSHOT[available_copies] - 1, 0 ) ), FACT_INVENTORY_SNAPSHOT[reallocation_priority] = "Low", FACT_INVENTORY_SNAPSHOT[available_copies] >= 2, FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d ) )` |
| Out-of-Stock Rate % (Last Month) | `VAR d = [_Last Snapshot Date] RETURN CALCULATE ( DIVIDE ( CALCULATE ( COUNTROWS ( FACT_INVENTORY_SNAPSHOT ), FACT_INVENTORY_SNAPSHOT[out_of_stock] = TRUE () ), COUNTROWS ( FACT_INVENTORY_SNAPSHOT ) ), FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d ) )` |
| Reallocation Coverage Rate % | `DIVIDE ( [Movable Idle Copies (Last Month)], [Unsatisfied Demand (Last Month)] )` |
| Total Copies (Last Month) | `VAR d = [_Last Snapshot Date] RETURN CALCULATE ( SUM ( FACT_INVENTORY_SNAPSHOT[total_copies] ), FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d ) )` |
| Unsatisfied Demand (Last Month) | `VAR d = [_Last Snapshot Date] RETURN CALCULATE ( SUM ( FACT_INVENTORY_SNAPSHOT[unsatisfied_reservations] ), FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d ) )` |
| Unsatisfied Reservations (Month) | `SUM ( FACT_INVENTORY_SNAPSHOT[unsatisfied_reservations] )` |

