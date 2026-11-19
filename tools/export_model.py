"""Export the semantic model of library_analytics.pbix to docs/model.md.

A .pbix is a binary file: GitHub cannot show its measures or relationships.
This script reads them with pbixray and writes a Markdown page, so every DAX
measure can be read and reviewed without opening Power BI Desktop.

    pip install -r requirements-dev.txt
    python tools/export_model.py
"""

from __future__ import annotations

from pathlib import Path

from pbixray import PBIXRay

ROOT = Path(__file__).resolve().parents[1]
PBIX = ROOT / "library_analytics.pbix"
OUT = ROOT / "docs" / "model.md"
REVIEW = ROOT / "docs" / "model_review.md"


def one_line(dax: str) -> str:
    return " ".join(str(dax).split())


def main() -> None:
    model = PBIXRay(str(PBIX))
    lines = [
        "# Semantic model",
        "",
        f"Generated from `{PBIX.name}` by `tools/export_model.py`. Do not edit by hand.",
        "Review notes and fixes to apply in Power BI Desktop: [model_review.md](model_review.md).",
        "",
        "## Tables",
        "",
        "| Table | Columns |",
        "|---|---|",
    ]
    schema = model.schema
    for table in model.tables:
        cols = schema.loc[schema["TableName"] == table, "ColumnName"].tolist()
        lines.append(f"| `{table}` | {len(cols)} |")

    rels = model.relationships
    lines += ["", f"## Relationships ({len(rels)})", "", "| From (many) | To (one) | Active | Filter |", "|---|---|---|---|"]
    for _, r in rels.iterrows():
        lines.append(
            f"| `{r.FromTableName}[{r.FromColumnName}]` | `{r.ToTableName}[{r.ToColumnName}]` "
            f"| {'yes' if r.IsActive else 'no'} | {r.CrossFilteringBehavior} |"
        )

    measures = model.dax_measures.copy()
    measures["DisplayFolder"] = measures["DisplayFolder"].fillna("(no folder)")
    lines += ["", f"## Measures ({len(measures)})", ""]
    for folder, group in measures.sort_values(["DisplayFolder", "Name"]).groupby("DisplayFolder", sort=True):
        lines += [f"### {folder}", "", "| Measure | DAX |", "|---|---|"]
        for _, m in group.iterrows():
            dax = one_line(m.Expression).replace("|", "\\|")
            lines.append(f"| {m.Name} | `{dax}` |")
        lines.append("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(rels)} relationships, {len(measures)} measures")


if __name__ == "__main__":
    main()
