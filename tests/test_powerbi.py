"""The generated Power BI project is consistent: every field used exists."""

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
pytest.importorskip("pbip_generator")
sys.path.insert(0, str(ROOT / "powerbi"))

from build_report import DEFAULT_DATA_FOLDER, MEASURES, build_project  # noqa: E402
from pbip_generator.builder import render_project  # noqa: E402


@pytest.fixture(scope="module")
def project():
    return build_project(DEFAULT_DATA_FOLDER)


def test_six_pages_and_all_measures(project):
    assert [p.display_name for p in project.pages] == [
        "Overview",
        "Time & Exam Periods",
        "Network & Branches",
        "Users & Overdue",
        "Catalogue & Demand",
        "Stock & Reallocation",
    ]
    assert len(MEASURES) == 58
    assert len({m.name for _, m in MEASURES}) == 58


def test_visual_fields_exist(project):
    fields = {(t.name, c.name) for t in project.tables for c in t.columns}
    fields |= {(t.name, m.name) for t, m in project.all_measures()}
    for page in project.pages:
        for visual in page.visuals:
            for refs in visual.roles.values():
                for ref in refs:
                    assert (ref.table, ref.name) in fields, (page.display_name, ref)


def test_dax_references_exist(project):
    columns = {(t.name, c.name) for t in project.tables for c in t.columns}
    measures = {m.name for _, m in project.all_measures()}
    for _, m in project.all_measures():
        for table, col in re.findall(r"\b([A-Z_]+)\[([^\]]+)\]", m.expression):
            assert (table, col) in columns, (m.name, table, col)
        for ref in re.findall(r"(?<![\w\]])\[([^\]@]+)\]", m.expression):
            assert ref in measures or any(ref == c for _, c in columns), (m.name, ref)


def test_model_review_fixes_are_applied(project):
    dax = {m.name: m.expression for _, m in project.all_measures()}
    assert "active_loans" in dax["Avg Utilization (Last Month)"]  # weighted by copies
    assert '"08-31"' in dax["Loans YTD"]  # academic year
    assert project.table("DIM_DATE").role.value == "date"


def test_committed_project_is_up_to_date(project):
    committed = ROOT / "powerbi" / "LibraryAnalytics"
    for rel, content in render_project(project).items():
        path = committed / rel
        assert path.exists(), f"missing {rel}: run python powerbi/build_report.py"
        assert path.read_text(encoding="utf-8") == content, f"{rel} is stale: run python powerbi/build_report.py"
