"""Write docs/model.md from powerbi/build_report.py, the source of the report.

The measures, relationships and pages are described in code; this page makes
them readable on GitHub without opening Power BI Desktop.

    pip install -r powerbi/requirements.txt
    python tools/export_model.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "powerbi"))

from build_report import DEFAULT_DATA_FOLDER, build_project  # noqa: E402

OUT = ROOT / "docs" / "model.md"


def main() -> None:
    project = build_project(DEFAULT_DATA_FOLDER)
    lines = [
        "# Semantic model",
        "",
        "Generated from `powerbi/build_report.py` by `tools/export_model.py`. Do not edit by hand.",
        "Review notes: [model_review.md](model_review.md).",
        "",
        "## Tables",
        "",
        "| Table | Role | Columns | Measures |",
        "|---|---|---|---|",
    ]
    for t in project.tables:
        lines.append(f"| `{t.name}` | {t.role.value} | {len(t.columns)} | {len(t.measures)} |")

    lines += ["", f"## Relationships ({len(project.relationships)})", "", "| From (many) | To (one) |", "|---|---|"]
    for r in project.relationships:
        lines.append(f"| `{r.from_table}[{r.from_column}]` | `{r.to_table}[{r.to_column}]` |")

    measures = sorted(project.all_measures(), key=lambda tm: (tm[1].display_folder or "", tm[1].name))
    lines += ["", f"## Measures ({len(measures)})", ""]
    folder = None
    for table, m in measures:
        if m.display_folder != folder:
            folder = m.display_folder
            lines += ["", f"### {folder}", ""]
        lines += [f"**{m.name}** (`{table.name}`, format `{m.format_string or 'default'}`)"]
        if m.description:
            lines += ["", f"> {m.description}"]
        lines += ["", "```dax", m.expression, "```", ""]

    lines += ["## Pages", ""]
    for page in project.pages:
        titles = [v.title or v.text for v in page.visuals if v.visual_type not in ("slicer", "card", "textbox")]
        lines.append(f"- **{page.display_name}**: {', '.join(titles)}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(project.relationships)} relationships, {len(measures)} measures")


if __name__ == "__main__":
    main()
