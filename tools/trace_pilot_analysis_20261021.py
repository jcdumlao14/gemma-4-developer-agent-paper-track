import csv
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "experiments" / "results"

pilot_path = RESULTS / "TRACE_GEMMA4_CONSOLIDATED_PILOT_REPORT.json"
finalization_path = RESULTS / "TRACE_FINALIZATION_REPORT.json"

if not pilot_path.is_file():
    raise FileNotFoundError(f"Required pilot report not found: {pilot_path}")

with pilot_path.open("r", encoding="utf-8-sig") as f:
    pilot = json.load(f)

finalization = {}
if finalization_path.is_file():
    with finalization_path.open("r", encoding="utf-8-sig") as f:
        finalization = json.load(f)

cases = pilot.get("cases", [])
if not cases:
    raise ValueError("The consolidated pilot report contains no cases.")

# Preserve the reported fields; do not infer missing control results.
columns = [
    "id",
    "provenance",
    "target_passed",
    "controls_passed",
    "broader_validation",
    "source_restored",
    "interpretation",
]

rows = []
for case in cases:
    rows.append({
        "id": case.get("id"),
        "provenance": case.get("provenance"),
        "target_passed": case.get("target_passed"),
        "controls_passed": case.get("controls_passed"),
        "broader_validation": case.get("broader_validation"),
        "source_restored": case.get("source_restored"),
        "interpretation": case.get("interpretation"),
    })

def parse_fraction(value):
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"\s*(\d+)\s*/\s*(\d+)\s*", value)
    if not match:
        return None
    passed, total = map(int, match.groups())
    return {"passed": passed, "total": total}

target_known = [r for r in rows if isinstance(r["target_passed"], bool)]
target_passed = sum(r["target_passed"] is True for r in target_known)

controls_known = [
    r for r in rows if parse_fraction(r["controls_passed"]) is not None
]
controls_all_passed = sum(
    parse_fraction(r["controls_passed"])["passed"]
    == parse_fraction(r["controls_passed"])["total"]
    for r in controls_known
)

gemma_mentioned = sum(
    "gemma" in str(r["provenance"]).lower()
    for r in rows
)

source_restored_known = [
    r for r in rows if isinstance(r["source_restored"], bool)
]
source_restored_true = sum(
    r["source_restored"] is True for r in source_restored_known
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = RESULTS / f"trace_pilot_analysis_{timestamp}"
out_dir.mkdir(parents=True, exist_ok=False)

csv_path = out_dir / "case_level_outcomes.csv"
with csv_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

summary = {
    "analysis_type": "descriptive_four_case_pilot",
    "generated_local": datetime.now().astimezone().isoformat(),
    "source_report": str(pilot_path.relative_to(ROOT)),
    "finalization_report": (
        str(finalization_path.relative_to(ROOT))
        if finalization else None
    ),
    "reported_case_count": pilot.get("pilot_case_count"),
    "rows_analyzed": len(rows),
    "target_test": {
        "known_outcomes": len(target_known),
        "passed": target_passed,
        "descriptive_pass_fraction": (
            target_passed / len(target_known) if target_known else None
        ),
    },
    "selected_controls": {
        "cases_with_recorded_fraction": len(controls_known),
        "cases_with_all_recorded_controls_passing": controls_all_passed,
        "missing_control_fraction_cases": [
            r["id"] for r in rows
            if parse_fraction(r["controls_passed"]) is None
        ],
    },
    "source_restoration": {
        "known_outcomes": len(source_restored_known),
        "restored": source_restored_true,
    },
    "provenance": {
        "cases_whose_provenance_mentions_gemma": gemma_mentioned,
        "warning": (
            "This is a provenance-text count, not an initial-proposal "
            "success rate or a causal attribution."
        ),
    },
    "broader_validation_by_case": [
        {
            "case_id": r["id"],
            "reported_validation": r["broader_validation"],
        }
        for r in rows
    ],
    "controlled_baseline_comparison_complete":
        finalization.get("controlled_baseline_comparison_complete"),
    "limitations": pilot.get("limitations", []),
    "interpretation_warning": (
        "Descriptive results only. The four issues are not independent "
        "candidate attempts; test scopes differ; no benchmark-wide or "
        "comparative performance claim is justified."
    ),
}

json_path = out_dir / "descriptive_summary.json"
json_path.write_text(
    json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

md = [
    "# TRACE Four-Case Pilot: Descriptive Analysis",
    "",
    f"- Cases analyzed: **{len(rows)}**",
    f"- Recorded target-test outcomes: **{target_passed}/{len(target_known)} passed**",
    f"- Cases with recorded control fractions: **{len(controls_known)}**",
    f"- Cases with all recorded controls passing: **{controls_all_passed}**",
    f"- Cases with source-restoration status recorded as true: "
    f"**{source_restored_true}/{len(source_restored_known)}**",
    "",
    "## Case-level outcomes",
    "",
    "| Case | Target | Controls | Broader validation | Source restored |",
    "|---|---|---|---|---|",
]
for r in rows:
    target = (
        "Pass" if r["target_passed"] is True
        else "Fail" if r["target_passed"] is False
        else "Not recorded"
    )
    restored = (
        "Yes" if r["source_restored"] is True
        else "No" if r["source_restored"] is False
        else "Not recorded"
    )
    broader = str(r["broader_validation"] or "Not recorded").replace("|", "\\|")
    md.append(
        f"| {r['id']} | {target} | "
        f"{r['controls_passed'] or 'Not recorded'} | "
        f"{broader} | {restored} |"
    )

md.extend([
    "",
    "## Interpretation and limitations",
    "",
    "- This is a descriptive analysis of four selected cases.",
    "- Candidate provenance differs by case; SQLFluff-1733 is explicitly "
    "not a Gemma-attributed success.",
    "- Initial and refined candidates must not be counted as separate "
    "benchmark issues.",
    "- Test scopes differ, so their pass counts should not be summed into "
    "a comparative score.",
    "- Missing control outcomes remain missing, not failures.",
    "- The finalization record says the controlled baseline comparison "
    "is incomplete; no comparative effectiveness claim is made.",
    "",
    "## Source",
    "",
    f"`{pilot_path.relative_to(ROOT)}`",
    "",
])

md_path = out_dir / "analysis_report.md"
md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

print("TRACE PILOT ANALYSIS: PASS")
print(f"Cases analyzed: {len(rows)}")
print(f"Target tests passed: {target_passed}/{len(target_known)}")
print(f"Cases with known control fractions: {len(controls_known)}/{len(rows)}")
print(f"Cases with all recorded controls passing: {controls_all_passed}")
print(
    "Controlled baseline comparison complete: "
    f"{summary['controlled_baseline_comparison_complete']}"
)
print(f"\nOutput folder: {out_dir}")
print(f"CSV: {csv_path.name}")
print(f"JSON: {json_path.name}")
print(f"Markdown: {md_path.name}")
