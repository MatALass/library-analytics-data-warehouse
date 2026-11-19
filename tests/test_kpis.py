"""Every figure quoted in the README is recomputed from the CSVs.

The DAX measures of the report are reproduced in pandas with the same logic,
so a change in the generator that breaks a README claim fails here.
"""

from math import ceil
from pathlib import Path

import pandas as pd
import pytest

DATA = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture(scope="module")
def t():
    read = lambda name: pd.read_csv(DATA / f"{name}.csv")  # noqa: E731
    return {n: read(n) for n in ["FACT_LOAN", "FACT_RESERVATION", "FACT_INVENTORY_SNAPSHOT", "DIM_USER", "DIM_BRANCH", "DIM_BOOK"]}


@pytest.fixture(scope="module")
def last_month(t):
    snap = t["FACT_INVENTORY_SNAPSHOT"]
    return snap[snap["date_id"] == snap["date_id"].max()]


def test_volumes(t):
    assert len(t["FACT_LOAN"]) == 16_000
    assert len(t["FACT_RESERVATION"]) == 3_600


def test_reallocation_headline(last_month):
    # Measures: Critical Pairs, Unsatisfied Demand, Movable Idle Copies (Last Month)
    critical = (last_month["reallocation_priority"] == "Critical").sum()
    unmet = last_month["unsatisfied_reservations"].sum()
    idle = last_month[(last_month["reallocation_priority"] == "Low") & (last_month["available_copies"] >= 2)]
    movable = (idle["available_copies"] - 1).sum()
    assert critical == 124
    assert unmet == 353
    assert movable / unmet == pytest.approx(0.3229, abs=1e-4)


def test_top_20_percent_books_share(t):
    # Measure: Top 20% Books Loan Share % (ROUNDUP(N * 0.2) books)
    loans = t["FACT_LOAN"].groupby("book_id").size().sort_values(ascending=False)
    n_top = ceil(len(t["DIM_BOOK"]) * 0.2)
    assert loans.head(n_top).sum() / loans.sum() == pytest.approx(0.464, abs=0.001)


def test_overdue_rate_by_user_type(t):
    # Measure: Overdue Rate % = overdue loans / closed loans
    loans = t["FACT_LOAN"].merge(t["DIM_USER"][["user_id", "user_type"]])
    closed = loans[loans["return_date"].notna()]
    rate = (closed["days_overdue"] > 0).groupby(closed["user_type"]).mean()
    assert rate["Student"] == pytest.approx(0.261, abs=0.001)
    assert rate["Researcher"] == pytest.approx(0.167, abs=0.001)
    assert rate["Faculty"] == pytest.approx(0.158, abs=0.001)


def test_open_loans_are_never_overdue(t):
    # Why the overdue rate divides by closed loans: open loans always carry 0.
    loans = t["FACT_LOAN"]
    assert (loans.loc[loans["return_date"].isna(), "days_overdue"] == 0).all()


def test_branch_load_ranking(t):
    loads = t["FACT_LOAN"].merge(t["DIM_BRANCH"][["branch_id", "city"]]).groupby("city").size()
    assert loads.sort_values(ascending=False).index.tolist() == [
        "Paris",
        "Lyon",
        "Brussels",
        "Lille",
        "Marseille",
        "Liège",
    ]


def test_weighted_utilization_differs_from_simple_average(last_month):
    # Documented in docs/model_review.md: the report averages rates (71.9 %),
    # the copy-weighted utilization is 77.7 %.
    simple = last_month["utilization_rate"].mean()
    weighted = last_month["active_loans"].sum() / last_month["total_copies"].sum()
    assert simple == pytest.approx(0.719, abs=0.001)
    assert weighted == pytest.approx(0.777, abs=0.001)
