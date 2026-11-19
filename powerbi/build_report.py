"""Build the Library Analytics Power BI project (PBIP) from code.

Everything the report needs is described here: column types, relationships,
the 58 DAX measures and the 6 pages. pbip-generator then writes the project as
TMDL (semantic model) and PBIR (report), plain text files that can be reviewed
in a pull request, unlike the old binary .pbix.

    pip install -r powerbi/requirements.txt
    python powerbi/build_report.py
    python powerbi/build_report.py --data-folder "D:\\repos\\library-analytics-data-warehouse\\data\\"

The project opens without data: point the DataFolder parameter at the data
folder of this repository (with the final backslash) and click Refresh.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from pbip_generator.builder import write_project
from pbip_generator.model import (
    Column,
    DataType,
    FieldRef,
    Measure,
    Page,
    Project,
    Relationship,
    Source,
    Table,
    TableRole,
    Visual,
)

NAME = "LibraryAnalytics"
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent
THEME = OUT / "theme.json"
DEFAULT_DATA_FOLDER = "C:\\pbip\\library-analytics-data-warehouse\\data\\"

DIMENSIONS = ["DIM_DATE", "DIM_BOOK", "DIM_BRANCH", "DIM_CATEGORY", "DIM_USER"]
FACTS = ["FACT_LOAN", "FACT_RESERVATION", "FACT_INVENTORY_SNAPSHOT"]
KEYS = {"date_id": "DIM_DATE", "user_id": "DIM_USER", "book_id": "DIM_BOOK", "branch_id": "DIM_BRANCH", "category_id": "DIM_CATEGORY"}

# Columns sorted by another one (month names in calendar order, not A-Z).
SORT_BY = {
    ("DIM_DATE", "month_name"): "month_number",
    ("DIM_DATE", "day_name"): "day_of_week",
    ("DIM_DATE", "quarter_label"): "quarter",
}
DATE_COLUMNS = {"full_date", "event_date", "loan_date", "due_date", "return_date", "snapshot_date"}


# --------------------------------------------------------------------------- #
# Model
# --------------------------------------------------------------------------- #
def column_type(name: str, series: pd.Series) -> DataType:
    if name in DATE_COLUMNS:
        return DataType.DATETIME
    if pd.api.types.is_bool_dtype(series):
        return DataType.BOOLEAN
    if pd.api.types.is_integer_dtype(series):
        return DataType.INT64
    if pd.api.types.is_float_dtype(series):
        # Columns with blanks are read as float by pandas: keep integers as integers.
        non_null = series.dropna()
        return DataType.INT64 if len(non_null) and (non_null % 1 == 0).all() and name != "penalty_amount" else DataType.DOUBLE
    return DataType.STRING


def build_table(name: str) -> Table:
    frame = pd.read_csv(DATA / f"{name}.csv", nrows=5000)
    role = TableRole.FACT if name in FACTS else TableRole.DIMENSION
    if name == "DIM_DATE":
        role = TableRole.DATE
    columns = []
    for col in frame.columns:
        dtype = column_type(col, frame[col])
        is_id = col.endswith("_id")
        numeric = dtype in (DataType.INT64, DataType.DOUBLE)
        columns.append(
            Column(
                col,
                dtype,
                is_date_only=dtype == DataType.DATETIME,
                format_string="yyyy-mm-dd"
                if dtype == DataType.DATETIME
                else ("0" if dtype == DataType.INT64 and role != TableRole.FACT else None),
                is_key=name == "DIM_DATE" and col == "full_date",
                is_unique=name == "DIM_DATE" and col == "full_date",
                # Keys and raw numbers of the facts are hidden: visuals use dimensions and measures.
                is_hidden=(role == TableRole.FACT and (is_id or numeric))
                or col in ("month_number", "day_of_week")
                or col == "preferred_branch_id",
                summarize_by="sum" if numeric and not is_id and role == TableRole.FACT else "none",
                sort_by_column=SORT_BY.get((name, col)),
            )
        )
    table = Table(name, columns, Source(kind="csv", file_name=f"{name}.csv"), role=role)
    table.measures = [m for t, m in MEASURES if t == name]
    return table


def build_project(data_folder: str) -> Project:
    tables = [build_table(n) for n in DIMENSIONS + FACTS]
    relationships = [
        Relationship(fact, key, dim, key)
        for fact in FACTS
        for key, dim in KEYS.items()
        if any(c.name == key for c in next(t for t in tables if t.name == fact).columns)
    ]
    project = Project(NAME, tables, relationships, culture="en-US", data_folder=data_folder)
    project.theme = json.loads(THEME.read_text(encoding="utf-8"))
    project.pages = build_pages()
    return project


# --------------------------------------------------------------------------- #
# Measures: the 57 of the original report, plus the fixes of docs/model_review.md
# --------------------------------------------------------------------------- #
PCT, INT, DEC1, DEC2, EUR = "0.0%", "#,0", "#,0.0", "#,0.00", "#,0.00 €"
F0, F1, F2, F3, F4, F5, F6 = (
    "00 - Common",
    "01 - Overview",
    "02 - Time & Exams",
    "03 - Network",
    "04 - Users",
    "05 - Catalogue",
    "06 - Stock",
)
LAST = "FILTER ( ALL ( DIM_DATE ), DIM_DATE[date_id] = d )"


def m(table: str, name: str, dax: str, fmt: str | None, folder: str, description: str | None = None):
    return table, Measure(name, dax, fmt, folder, description)


L, R, S = "FACT_LOAN", "FACT_RESERVATION", "FACT_INVENTORY_SNAPSHOT"

MEASURES = [
    # 00 - Common
    m(L, "Total Loans", "COUNTROWS ( FACT_LOAN )", INT, F0),
    m(L, "Open Loans", "CALCULATE ( COUNTROWS ( FACT_LOAN ), ISBLANK ( FACT_LOAN[return_date] ) )", INT, F0),
    m(L, "Closed Loans", "CALCULATE ( COUNTROWS ( FACT_LOAN ), NOT ISBLANK ( FACT_LOAN[return_date] ) )", INT, F0),
    m(L, "Loaned Quantity", "SUM ( FACT_LOAN[quantity] )", INT, F0),
    m(L, "Active Users", "DISTINCTCOUNT ( FACT_LOAN[user_id] )", INT, F0),
    m(L, "Distinct Books Loaned", "DISTINCTCOUNT ( FACT_LOAN[book_id] )", INT, F0),
    m(L, "Active Branches", "DISTINCTCOUNT ( FACT_LOAN[branch_id] )", INT, F0),
    m(L, "Active Days", "DISTINCTCOUNT ( FACT_LOAN[date_id] )", INT, F0),
    m(R, "Total Reservations", "COUNTROWS ( FACT_RESERVATION )", INT, F0),
    m(R, "Fulfilled Reservations", 'CALCULATE ( [Total Reservations], FACT_RESERVATION[reservation_status] = "fulfilled" )', INT, F0),
    m(R, "Pending Reservations", 'CALCULATE ( [Total Reservations], FACT_RESERVATION[reservation_status] = "pending" )', INT, F0),
    m(R, "Cancelled Reservations", 'CALCULATE ( [Total Reservations], FACT_RESERVATION[reservation_status] = "cancelled" )', INT, F0),
    m(
        S,
        "_Last Snapshot Date",
        "CALCULATE ( MAX ( FACT_INVENTORY_SNAPSHOT[date_id] ), ALL ( FACT_INVENTORY_SNAPSHOT ), ALLSELECTED ( DIM_DATE ) )",
        "0",
        F0,
        "date_id of the latest monthly snapshot in the selected period.",
    ),
    # 01 - Overview
    m(L, "Avg Daily Loans", "DIVIDE ( [Total Loans], COUNTROWS ( DIM_DATE ) )", DEC1, F1),
    m(
        L,
        "Loans YTD",
        'TOTALYTD ( [Total Loans], DIM_DATE[full_date], "08-31" )',
        INT,
        F1,
        "Academic year to date (September to August).",
    ),
    m(L, "Loans LY", "CALCULATE ( [Total Loans], SAMEPERIODLASTYEAR ( DIM_DATE[full_date] ) )", INT, F1),
    m(L, "Loans YoY %", "VAR Prev = [Loans LY]\nRETURN DIVIDE ( [Total Loans] - Prev, Prev )", "+0.0%;-0.0%;0.0%", F1),
    m(L, "Loans LM", "CALCULATE ( [Total Loans], DATEADD ( DIM_DATE[full_date], -1, MONTH ) )", INT, F1),
    m(L, "Loans MoM %", "VAR Prev = [Loans LM]\nRETURN DIVIDE ( [Total Loans] - Prev, Prev )", "+0.0%;-0.0%;0.0%", F1),
    m(
        L,
        "Running Total Loans",
        "CALCULATE ( [Total Loans], FILTER ( ALL ( DIM_DATE ), DIM_DATE[full_date] <= MAX ( DIM_DATE[full_date] ) ) )",
        INT,
        F1,
    ),
    m(
        L,
        "Total Loans (Top 10 Users)",
        "IF (\n"
        "    RANKX ( ALLSELECTED ( DIM_USER[full_name] ), [Total Loans],, DESC, DENSE ) <= 10,\n"
        "    [Total Loans]\n"
        ")",
        INT,
        F1,
        "Blank outside the top 10, so the bar chart keeps 10 bars without a visual filter.",
    ),
    # 02 - Time & Exams
    m(L, "Loans (Exam Period)", "CALCULATE ( [Total Loans], DIM_DATE[is_exam_period] = TRUE () )", INT, F2),
    m(L, "Loans (Off-Exam)", "CALCULATE ( [Total Loans], DIM_DATE[is_exam_period] = FALSE () )", INT, F2),
    m(L, "Exam-Period Loans %", "DIVIDE ( [Loans (Exam Period)], [Total Loans] )", PCT, F2),
    m(L, "_Exam Days", "CALCULATE ( COUNTROWS ( DIM_DATE ), DIM_DATE[is_exam_period] = TRUE () )", INT, F2),
    m(L, "_Off-Exam Days", "CALCULATE ( COUNTROWS ( DIM_DATE ), DIM_DATE[is_exam_period] = FALSE () )", INT, F2),
    m(L, "Daily Loans (Exam Period)", "DIVIDE ( [Loans (Exam Period)], [_Exam Days] )", DEC1, F2),
    m(L, "Daily Loans (Off-Exam)", "DIVIDE ( [Loans (Off-Exam)], [_Off-Exam Days] )", DEC1, F2),
    m(L, "Exam Overload Index", "DIVIDE ( [Daily Loans (Exam Period)], [Daily Loans (Off-Exam)] )", DEC2, F2),
    m(
        L,
        "Weekend Loans %",
        "DIVIDE ( CALCULATE ( [Total Loans], DIM_DATE[is_weekend] = TRUE () ), [Total Loans] )",
        PCT,
        F2,
    ),
    # 03 - Network
    m(
        L,
        "Avg Branch Daily Load",
        "VAR _TotalDays = CALCULATE ( COUNTROWS ( DIM_DATE ), DIM_DATE[full_date] <= MAX ( DIM_DATE[full_date] ) )\n"
        "RETURN DIVIDE ( [Total Loans], _TotalDays )",
        DEC1,
        F3,
    ),
    m(
        L,
        "Branch Loan Share %",
        "DIVIDE ( [Total Loans], CALCULATE ( [Total Loans], ALL ( DIM_BRANCH ) ) )",
        PCT,
        F3,
    ),
    # 04 - Users
    m(L, "Loans per User", "DIVIDE ( [Total Loans], [Active Users] )", DEC1, F4),
    m(L, "Overdue Loans", "CALCULATE ( COUNTROWS ( FACT_LOAN ), FACT_LOAN[days_overdue] > 0 )", INT, F4),
    m(
        L,
        "Overdue Rate %",
        "DIVIDE ( [Overdue Loans], [Closed Loans] )",
        PCT,
        F4,
        "Overdue loans / closed loans: open loans always have 0 overdue days.",
    ),
    m(
        L,
        "Avg Overdue Days (overdue only)",
        "AVERAGEX ( FILTER ( FACT_LOAN, FACT_LOAN[days_overdue] > 0 ), FACT_LOAN[days_overdue] )",
        DEC1,
        F4,
    ),
    m(L, "Total Penalties", "SUM ( FACT_LOAN[penalty_amount] )", EUR, F4),
    m(L, "Avg Penalty per User", "DIVIDE ( [Total Penalties], [Active Users] )", EUR, F4),
    m(L, "Avg Loan Duration (days)", "AVERAGE ( FACT_LOAN[loan_duration_days] )", DEC1, F4),
    # 05 - Catalogue
    m(
        L,
        "Book Rank",
        "IF ( HASONEVALUE ( DIM_BOOK[book_id] ), RANKX ( ALL ( DIM_BOOK[book_id] ), [Total Loans],, DESC, DENSE ) )",
        "0",
        F5,
    ),
    m(
        L,
        "Cumulative Loans % (Pareto)",
        "VAR CurLoans = [Total Loans]\n"
        'VAR Books = ADDCOLUMNS ( ALLSELECTED ( DIM_BOOK[title] ), "@loans", [Total Loans] )\n'
        "VAR Grand = SUMX ( Books, [@loans] )\n"
        "VAR CumLoans = SUMX ( FILTER ( Books, [@loans] >= CurLoans ), [@loans] )\n"
        "RETURN IF ( NOT ISBLANK ( CurLoans ), DIVIDE ( CumLoans, Grand ) )",
        PCT,
        F5,
    ),
    m(
        L,
        "Top 20% Books Loan Share %",
        "VAR N = COUNTROWS ( ALL ( DIM_BOOK[book_id] ) )\n"
        "VAR NbTop = ROUNDUP ( N * 0.2, 0 )\n"
        'VAR T = ADDCOLUMNS ( ALL ( DIM_BOOK[book_id] ), "@l", [Total Loans] )\n'
        "VAR TopBooks = TOPN ( NbTop, T, [@l], DESC )\n"
        "RETURN DIVIDE ( SUMX ( TopBooks, [@l] ), SUMX ( T, [@l] ) )",
        PCT,
        F5,
    ),
    m(R, "Reservation Fulfillment Rate %", "DIVIDE ( [Fulfilled Reservations], [Total Reservations] )", PCT, F5),
    m(R, "Reservation Cancel Rate %", "DIVIDE ( [Cancelled Reservations], [Total Reservations] )", PCT, F5),
    m(R, "Avg Reservation Wait (days)", "AVERAGE ( FACT_RESERVATION[wait_days] )", DEC1, F5),
    m(R, "Demand Pressure (Resv per Loan)", "DIVIDE ( [Total Reservations], [Total Loans] )", DEC2, F5),
    # 06 - Stock (snapshots: never summed across months, the "Last Month" measures pin the latest one)
    m(
        S,
        "Total Copies (Last Month)",
        f"VAR d = [_Last Snapshot Date]\nRETURN CALCULATE ( SUM ( FACT_INVENTORY_SNAPSHOT[total_copies] ), {LAST} )",
        INT,
        F6,
    ),
    m(
        S,
        "Available Copies (Last Month)",
        f"VAR d = [_Last Snapshot Date]\nRETURN CALCULATE ( SUM ( FACT_INVENTORY_SNAPSHOT[available_copies] ), {LAST} )",
        INT,
        F6,
    ),
    m(
        S,
        "Avg Utilization (Last Month)",
        "VAR d = [_Last Snapshot Date]\n"
        "RETURN\n"
        "    CALCULATE (\n"
        "        DIVIDE ( SUM ( FACT_INVENTORY_SNAPSHOT[active_loans] ), SUM ( FACT_INVENTORY_SNAPSHOT[total_copies] ) ),\n"
        f"        {LAST}\n"
        "    )",
        PCT,
        F6,
        "Weighted by copies: a pair with 30 copies weighs more than a pair with 1.",
    ),
    m(
        S,
        "Out-of-Stock Rate % (Last Month)",
        "VAR d = [_Last Snapshot Date]\n"
        "RETURN\n"
        "    CALCULATE (\n"
        "        DIVIDE (\n"
        "            CALCULATE ( COUNTROWS ( FACT_INVENTORY_SNAPSHOT ), FACT_INVENTORY_SNAPSHOT[out_of_stock] = TRUE () ),\n"
        "            COUNTROWS ( FACT_INVENTORY_SNAPSHOT )\n"
        "        ),\n"
        f"        {LAST}\n"
        "    )",
        PCT,
        F6,
    ),
    m(
        S,
        "Avg Utilization (Month)",
        "DIVIDE ( SUM ( FACT_INVENTORY_SNAPSHOT[active_loans] ), SUM ( FACT_INVENTORY_SNAPSHOT[total_copies] ) )",
        PCT,
        F6,
        "Weighted by copies.",
    ),
    m(S, "Unsatisfied Reservations (Month)", "SUM ( FACT_INVENTORY_SNAPSHOT[unsatisfied_reservations] )", INT, F6),
    m(
        S,
        "Critical Pairs (Last Month)",
        "VAR d = [_Last Snapshot Date]\n"
        'RETURN CALCULATE ( COUNTROWS ( FACT_INVENTORY_SNAPSHOT ), FACT_INVENTORY_SNAPSHOT[reallocation_priority] = "Critical", '
        f"{LAST} )",
        INT,
        F6,
    ),
    m(
        S,
        "Unsatisfied Demand (Last Month)",
        "VAR d = [_Last Snapshot Date]\n"
        f"RETURN CALCULATE ( SUM ( FACT_INVENTORY_SNAPSHOT[unsatisfied_reservations] ), {LAST} )",
        INT,
        F6,
    ),
    m(
        S,
        "Idle Copies (Last Month)",
        "VAR d = [_Last Snapshot Date]\n"
        "RETURN CALCULATE ( SUM ( FACT_INVENTORY_SNAPSHOT[available_copies] ), "
        f'FACT_INVENTORY_SNAPSHOT[reallocation_priority] = "Low", {LAST} )',
        INT,
        F6,
    ),
    m(
        S,
        "Movable Idle Copies (Last Month)",
        "VAR d = [_Last Snapshot Date]\n"
        "RETURN\n"
        "    CALCULATE (\n"
        "        SUMX ( FACT_INVENTORY_SNAPSHOT, MAX ( FACT_INVENTORY_SNAPSHOT[available_copies] - 1, 0 ) ),\n"
        '        FACT_INVENTORY_SNAPSHOT[reallocation_priority] = "Low",\n'
        "        FACT_INVENTORY_SNAPSHOT[available_copies] >= 2,\n"
        f"        {LAST}\n"
        "    )",
        INT,
        F6,
        "Idle copies that can move while keeping one copy on site.",
    ),
    m(
        S,
        "Reallocation Coverage Rate %",
        "DIVIDE ( [Movable Idle Copies (Last Month)], [Unsatisfied Demand (Last Month)] )",
        PCT,
        F6,
        "Share of last month's unmet demand coverable by moving idle stock, with no new purchase.",
    ),
    m(
        S,
        "Current Reallocation Priority",
        "VAR d = [_Last Snapshot Date]\n"
        "RETURN\n"
        "    CALCULATE (\n"
        "        SELECTEDVALUE ( FACT_INVENTORY_SNAPSHOT[reallocation_priority] ),\n"
        f"        {LAST},\n"
        "        ALL ( FACT_INVENTORY_SNAPSHOT[reallocation_priority] )\n"
        "    )",
        None,
        F6,
    ),
]


# --------------------------------------------------------------------------- #
# Pages (1280 x 720): title and slicers on top, KPI cards, then charts
# --------------------------------------------------------------------------- #
W, H, M, G = 1280, 720, 16, 12
HEAD_H, CARD_H = 60, 96
TOP = M + HEAD_H + G
BODY = TOP + CARD_H + G
BODY_H = H - BODY - M


def c(table: str, name: str) -> FieldRef:
    return FieldRef(table, name)


def x(name: str) -> FieldRef:
    table = next(t for t, mm in MEASURES if mm.name == name)
    return FieldRef(table, name, is_measure=True)


YEAR = c("DIM_DATE", "year")
YEAR_MONTH = c("DIM_DATE", "year_month")
COUNTRY = c("DIM_BRANCH", "country")
BRANCH = c("DIM_BRANCH", "branch_name")
CITY = c("DIM_BRANCH", "city")
CATEGORY = c("DIM_CATEGORY", "category")
TITLE = c("DIM_BOOK", "title")


def header(title: str, *slicers: tuple[FieldRef, str]) -> list[Visual]:
    visuals = [Visual("textbox", {}, M, M, 560, HEAD_H, text=title, text_size=24)]
    width = 170
    start = W - M - len(slicers) * width - (len(slicers) - 1) * G
    visuals += [
        Visual("slicer", {"Values": [field]}, start + i * (width + G), M, width, HEAD_H, title=label)
        for i, (field, label) in enumerate(slicers)
    ]
    return visuals


def cards(*names: str) -> list[Visual]:
    n = len(names)
    w = (W - 2 * M - (n - 1) * G) / n
    return [Visual("card", {"Values": [x(name)]}, M + i * (w + G), TOP, w, CARD_H, title=name) for i, name in enumerate(names)]


def grid(*specs: tuple[float, float, float, float, Visual]) -> list[Visual]:
    """Place visuals on the body with fractions (x, y, w, h) of the free area."""
    out = []
    for fx, fy, fw, fh, v in specs:
        area_w, area_h = W - 2 * M, BODY_H
        v.x = M + fx * area_w + (G / 2 if fx > 0 else 0)
        v.y = BODY + fy * area_h + (G / 2 if fy > 0 else 0)
        v.width = fw * area_w - (G / 2 if fx > 0 else 0) - (G / 2 if fx + fw < 1 else 0)
        v.height = fh * area_h - (G / 2 if fy > 0 else 0) - (G / 2 if fy + fh < 1 else 0)
        out.append(v)
    return out


def chart(kind: str, roles: dict, title: str, sort: FieldRef | None = None, ascending: bool = False) -> Visual:
    return Visual(kind, roles, 0, 0, 0, 0, title=title, sort_by=sort, sort_descending=not ascending)


def build_pages() -> list[Page]:
    overview = Page("Overview")
    overview.visuals += header("Overview", (YEAR, "Year"), (COUNTRY, "Country"), (BRANCH, "Branch"), (CATEGORY, "Category"))
    overview.visuals += cards("Total Loans", "Avg Daily Loans", "Loans YoY %", "Loans MoM %", "Loans YTD")
    overview.visuals += grid(
        (0, 0, 0.56, 0.52, chart("areaChart", {"Category": [YEAR_MONTH], "Y": [x("Total Loans"), x("Loans LY")]}, "Monthly Loans vs Last Year", YEAR_MONTH, True)),
        (0.56, 0, 0.44, 0.52, chart("lineChart", {"Category": [c("DIM_DATE", "full_date")], "Y": [x("Running Total Loans")]}, "Cumulative Loans", c("DIM_DATE", "full_date"), True)),
        (0, 0.52, 0.5, 0.48, chart("clusteredBarChart", {"Category": [CATEGORY], "Y": [x("Total Loans")]}, "Loans by Category", x("Total Loans"))),
        (0.5, 0.52, 0.5, 0.48, chart("clusteredBarChart", {"Category": [c("DIM_USER", "full_name")], "Y": [x("Total Loans (Top 10 Users)")]}, "Top 10 Users by Loans", x("Total Loans (Top 10 Users)"))),
    )

    time = Page("Time & Exam Periods")
    time.visuals += header("Time & Exam Periods", (YEAR, "Year"), (COUNTRY, "Country"), (BRANCH, "Branch"))
    time.visuals += cards("Loans (Exam Period)", "Loans (Off-Exam)", "Exam-Period Loans %", "Exam Overload Index", "Weekend Loans %")
    time.visuals += grid(
        (0, 0, 0.5, 0.5, chart("clusteredBarChart", {"Category": [CATEGORY], "Y": [x("Daily Loans (Exam Period)"), x("Daily Loans (Off-Exam)")]}, "Daily Loans by Category: Exam vs Off-Exam", x("Daily Loans (Exam Period)"))),
        (0.5, 0, 0.5, 0.5, chart("clusteredBarChart", {"Category": [c("DIM_DATE", "academic_period")], "Y": [x("Total Loans")]}, "Loans by Academic Period", x("Total Loans"))),
        (0, 0.5, 0.68, 0.5, chart("clusteredColumnChart", {"Category": [c("DIM_DATE", "week_number")], "Y": [x("Total Loans")], "Series": [c("DIM_DATE", "is_exam_period")]}, "Weekly Loans: Exam vs Non-Exam Weeks", c("DIM_DATE", "week_number"), True)),
        (0.68, 0.5, 0.32, 0.5, chart("gauge", {"Y": [x("Weekend Loans %")]}, "Weekend Loans Share")),
    )

    network = Page("Network & Branches")
    network.visuals += header("Network & Branches", (YEAR, "Year"), (COUNTRY, "Country"), (BRANCH, "Branch"))
    network.visuals += cards("Active Branches", "Avg Branch Daily Load", "Loans YoY %", "Total Loans")
    network.visuals += grid(
        (0, 0, 0.4, 1, chart("clusteredBarChart", {"Category": [CITY], "Y": [x("Total Loans")]}, "Loans by City", x("Total Loans"))),
        (0.4, 0, 0.6, 0.46, chart("clusteredColumnChart", {"Category": [CITY], "Y": [x("Branch Loan Share %")]}, "Branch Loan Share by City", x("Branch Loan Share %"))),
        (0.4, 0.46, 0.6, 0.54, chart("lineChart", {"Category": [YEAR_MONTH], "Y": [x("Total Loans")], "Series": [CITY]}, "Monthly Loans by City", YEAR_MONTH, True)),
    )

    users = Page("Users & Overdue")
    users.visuals += header("Users & Overdue", (YEAR, "Year"), (c("DIM_USER", "user_type"), "User type"), (COUNTRY, "Country"), (BRANCH, "Branch"))
    users.visuals += cards("Loans per User", "Overdue Rate %", "Avg Overdue Days (overdue only)", "Avg Penalty per User", "Avg Loan Duration (days)")
    users.visuals += grid(
        (0, 0, 0.6, 0.5, chart("clusteredBarChart", {"Category": [c("DIM_USER", "user_type")], "Y": [x("Overdue Rate %")]}, "Overdue Rate by User Type", x("Overdue Rate %"))),
        (0, 0.5, 0.6, 0.5, chart("clusteredBarChart", {"Category": [c("DIM_USER", "faculty")], "Y": [x("Total Loans")]}, "Loans by Faculty", x("Total Loans"))),
        (0.6, 0, 0.4, 1, chart("tableEx", {"Values": [c("DIM_USER", "full_name"), x("Total Loans"), x("Avg Overdue Days (overdue only)"), x("Total Penalties")]}, "Top Users by Loans & Penalties", x("Total Loans"))),
    )

    catalogue = Page("Catalogue & Demand")
    catalogue.visuals += header("Catalogue & Demand", (YEAR, "Year"), (COUNTRY, "Country"), (BRANCH, "Branch"), (CATEGORY, "Category"))
    catalogue.visuals += cards("Top 20% Books Loan Share %", "Reservation Fulfillment Rate %", "Reservation Cancel Rate %", "Avg Reservation Wait (days)")
    catalogue.visuals += grid(
        (0, 0, 0.45, 1, chart("clusteredBarChart", {"Category": [CATEGORY], "Y": [x("Total Loans")]}, "Loans by Category", x("Total Loans"))),
        (0.45, 0, 0.55, 0.5, chart("lineStackedColumnComboChart", {"Category": [TITLE], "Y": [x("Total Loans")], "Y2": [x("Cumulative Loans % (Pareto)")]}, "Book Pareto: Loans & Cumulative Share", x("Total Loans"))),
        (0.45, 0.5, 0.55, 0.5, chart("tableEx", {"Values": [TITLE, x("Total Loans"), x("Avg Reservation Wait (days)"), x("Reservation Cancel Rate %")]}, "Book Demand & Reservations", x("Total Loans"))),
    )

    stock = Page("Stock & Reallocation")
    stock.visuals += header("Stock & Reallocation", (YEAR, "Year"), (COUNTRY, "Country"), (BRANCH, "Branch"))
    stock.visuals += cards("Out-of-Stock Rate % (Last Month)", "Critical Pairs (Last Month)", "Unsatisfied Demand (Last Month)", "Reallocation Coverage Rate %")
    stock.visuals += grid(
        (0, 0, 0.26, 1, chart("clusteredBarChart", {"Category": [BRANCH], "Y": [x("Avg Utilization (Last Month)")]}, "Branch Utilization (Last Month)", x("Avg Utilization (Last Month)"))),
        (0.26, 0, 0.74, 0.55, chart("lineStackedColumnComboChart", {"Category": [YEAR_MONTH], "Y": [x("Unsatisfied Reservations (Month)")], "Y2": [x("Avg Utilization (Month)")]}, "Monthly Unmet Demand & Utilization", YEAR_MONTH, True)),
        (0.26, 0.55, 0.74, 0.45, chart("tableEx", {"Values": [TITLE, BRANCH, x("Current Reallocation Priority"), x("Available Copies (Last Month)"), x("Unsatisfied Demand (Last Month)")]}, "Reallocation Plan: Critical vs Idle Stock", x("Unsatisfied Demand (Last Month)"))),
    )
    return [overview, time, network, users, catalogue, stock]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-folder", default=DEFAULT_DATA_FOLDER)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    folder = args.data_folder if args.data_folder.endswith(("\\", "/")) else args.data_folder + "\\"
    root = write_project(build_project(folder), args.out, overwrite=True)
    print(f"Power BI project written to {root}")


if __name__ == "__main__":
    main()
