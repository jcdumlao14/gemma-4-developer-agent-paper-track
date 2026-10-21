from pathlib import Path
from datetime import datetime
import hashlib
import json
import subprocess
import sys

ROOT = Path.cwd()
RESULTS = ROOT / "experiments" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
CHECKS = {f"Milestone {i}": [] for i in range(1, 5)}
DETAILS = {}

def add(milestone, name, passed, detail, severity="required"):
    CHECKS[f"Milestone {milestone}"].append({
        "check": name,
        "status": "PASS" if passed else "REVIEW",
        "passed": bool(passed),
        "severity": severity,
        "detail": str(detail),
    })

def exists(rel):
    return (ROOT / rel).is_file()

def nonempty(rel):
    p = ROOT / rel
    return p.is_file() and p.stat().st_size > 0

def read_json(rel):
    p = ROOT / rel
    if not p.is_file():
        return None, f"Missing file: {rel}"
    try:
        return json.loads(p.read_text(encoding="utf-8-sig")), "Valid JSON"
    except Exception as exc:
        return None, f"JSON parse error: {exc}"

print("=" * 72)
print("TRACE MILESTONES 1–4: REPOSITORY EVIDENCE VERIFICATION")
print("=" * 72)
print(f"Repository: {ROOT}")
print("Note: checks are inferred from available repository artifacts.")
print("Official milestone acceptance criteria were not found in the supplied listing.")

# ---------------------------------------------------------------
# MILESTONE 1: Research plan and environment evidence
# ---------------------------------------------------------------
print("\n===== MILESTONE 1: PLAN AND ENVIRONMENT =====")

plan_rel = "experiments/datasets/pilot_plan_v1.json"
env_rel = "experiments/datasets/pilot_environment_audit.json"
plan, plan_msg = read_json(plan_rel)
env, env_msg = read_json(env_rel)

add(1, "Pilot plan exists and is valid JSON",
    plan is not None, f"{plan_rel}: {plan_msg}")
add(1, "Pilot environment audit exists and is valid JSON",
    env is not None, f"{env_rel}: {env_msg}")
add(1, "README exists and is non-empty",
    nonempty("README.md"), "README.md")
add(1, "Project configuration exists",
    nonempty("pyproject.toml"), "pyproject.toml")

if plan is not None:
    DETAILS["pilot_plan_top_level_keys"] = (
        list(plan.keys()) if isinstance(plan, dict) else
        f"JSON type: {type(plan).__name__}"
    )
if env is not None:
    DETAILS["environment_audit_top_level_keys"] = (
        list(env.keys()) if isinstance(env, dict) else
        f"JSON type: {type(env).__name__}"
    )

# ---------------------------------------------------------------
# MILESTONE 2: Implementation and automated tests
# ---------------------------------------------------------------
print("\n===== MILESTONE 2: IMPLEMENTATION AND TESTS =====")

source_files = [
    "src/trace_research/cli.py",
    "src/trace_research/benchmark.py",
    "src/trace_research/model_adapter.py",
    "src/trace_research/runner.py",
    "src/trace_research/workflow.py",
]
test_files = [
    "tests/test_benchmark.py",
    "tests/test_model_adapter.py",
    "tests/test_runner.py",
    "tests/test_workflow.py",
]

for rel in source_files:
    add(2, f"Implementation file: {rel}",
        nonempty(rel), "File exists and is non-empty")

for rel in test_files:
    add(2, f"Test file: {rel}",
        nonempty(rel), "File exists and is non-empty")

print("Running full test suite...")
test = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "tests"],
    cwd=ROOT, capture_output=True, text=True
)
test_output = (test.stdout + "\n" + test.stderr).strip()
(RESULTS / "TRACE_MILESTONES_1_TO_4_TESTS.log").write_text(
    test_output + "\n", encoding="utf-8"
)
add(2, "Full pytest suite",
    test.returncode == 0,
    f"Exit code: {test.returncode}; output: {test_output[-1200:]}")
DETAILS["pytest_exit_code"] = test.returncode

# ---------------------------------------------------------------
# MILESTONE 3: Pilot runs and saved evidence
# ---------------------------------------------------------------
print("\n===== MILESTONE 3: PILOT EVIDENCE =====")

pilot_files = [
    "experiments/results/TRACE_FINAL_PILOT_SUMMARY.md",
    "experiments/results/TRACE_GEMMA4_CONSOLIDATED_PILOT_REPORT.md",
    "experiments/results/TRACE_GEMMA4_CONSOLIDATED_PILOT_REPORT.json",
    "experiments/results/sqlfluff_1733_pilot/final_validation_report.json",
    "experiments/results/sqlfluff_1625_gemma_success_summary.json",
    "experiments/results/marshmallow_1343_final_case_record.json",
    "experiments/results/marshmallow_1359_candidate3_validation.json",
    "experiments/results/marshmallow_1359_final_full_suite.json",
]

for rel in pilot_files:
    add(3, f"Pilot artifact: {rel}",
        nonempty(rel), "File exists and is non-empty")

json_files = [
    "experiments/datasets/pilot_plan_v1.json",
    "experiments/datasets/pilot_environment_audit.json",
    "experiments/results/TRACE_GEMMA4_CONSOLIDATED_PILOT_REPORT.json",
    "experiments/results/sqlfluff_1733_pilot/final_validation_report.json",
    "experiments/results/sqlfluff_1625_gemma_success_summary.json",
    "experiments/results/marshmallow_1343_final_case_record.json",
    "experiments/results/marshmallow_1359_candidate3_validation.json",
    "experiments/results/marshmallow_1359_final_full_suite.json",
]

json_details = {}
for rel in json_files:
    obj, msg = read_json(rel)
    json_details[rel] = msg
    add(3, f"JSON evidence parses: {rel}",
        obj is not None, msg)

DETAILS["pilot_json_validation"] = json_details
DETAILS["pilot_cases_expected"] = [
    "SQLFluff-1733",
    "SQLFluff-1625",
    "Marshmallow-1343",
    "Marshmallow-1359",
]

# ---------------------------------------------------------------
# MILESTONE 4: Manuscript and reproducibility checks
# ---------------------------------------------------------------
print("\n===== MILESTONE 4: MANUSCRIPT AND REPRODUCIBILITY =====")

paper_rel = "paper/manuscript.md"
paper = ROOT / paper_rel
paper_text = (
    paper.read_text(encoding="utf-8-sig") if paper.is_file() else ""
)
paper_hash = (
    hashlib.sha256(paper.read_bytes()).hexdigest().upper()
    if paper.is_file() else None
)

add(4, "Manuscript exists and contains text",
    bool(paper_text.strip()), paper_rel)

headings = [
    line.strip().lstrip("#").strip().lower()
    for line in paper_text.splitlines()
    if line.strip().startswith("#")
]
heading_checks = {
    "abstract": lambda h: h == "abstract",
    "introduction": lambda h: "introduction" in h,
    "methods": lambda h: h == "2. method" or h == "method" or h.endswith(" methods"),
    "results": lambda h: "results" in h,
    "discussion": lambda h: h == "4. discussion" or h == "discussion",
    "limitations": lambda h: "limitations" in h,
    "conclusion": lambda h: "conclusion" in h,
    "references": lambda h: h == "references",
}
section_results = []
for section, predicate in heading_checks.items():
    found = any(predicate(h) for h in headings)
    section_results.append({"section": section, "found": found})
    add(4, f"Manuscript section: {section}",
        found, "Heading present" if found else "Heading not found")

add(4, "Consolidated pilot report is available",
    nonempty("experiments/results/TRACE_GEMMA4_CONSOLIDATED_PILOT_REPORT.md")
    and nonempty("experiments/results/TRACE_GEMMA4_CONSOLIDATED_PILOT_REPORT.json"),
    "Markdown and JSON consolidated reports")

# Ensure the manuscript does not falsely claim a controlled baseline is complete.
baseline_is_explicitly_incomplete = (
    "No controlled baseline comparison" in paper_text
    or "does not yet demonstrate" in paper_text
    or "lacks a controlled baseline" in paper_text
)
add(4, "Baseline limitations are disclosed",
    baseline_is_explicitly_incomplete,
    "Checks that the manuscript states comparative evidence is not established")

print("Running git diff --check...")
diff = subprocess.run(
    ["git", "diff", "--check"],
    cwd=ROOT, capture_output=True, text=True
)
diff_output = (diff.stdout + "\n" + diff.stderr).strip()
(RESULTS / "TRACE_MILESTONES_1_TO_4_GIT_DIFF_CHECK.log").write_text(
    diff_output + "\n", encoding="utf-8"
)
add(4, "git diff --check",
    diff.returncode == 0,
    f"Exit code: {diff.returncode}; output: {diff_output[-1000:]}")
DETAILS["git_diff_check_exit_code"] = diff.returncode
DETAILS["manuscript_sha256"] = paper_hash
DETAILS["manuscript_sections"] = section_results

# ---------------------------------------------------------------
# Summarize. A PASS means the listed evidence checks passed,
# not that an unknown official milestone rubric is certified.
# ---------------------------------------------------------------
milestone_summary = {}
for milestone, items in CHECKS.items():
    failed = [item for item in items if not item["passed"]]
    milestone_summary[milestone] = {
        "status": "PASS" if not failed else "REVIEW",
        "passed_checks": sum(item["passed"] for item in items),
        "total_checks": len(items),
        "review_checks": [item["check"] for item in failed],
    }

all_checks_pass = all(
    info["status"] == "PASS" for info in milestone_summary.values()
)

audit = {
    "project": "TRACE",
    "audit_scope": "Milestones 1–4 evidence checks",
    "generated_at": datetime.now().astimezone().isoformat(),
    "project_root": str(ROOT),
    "status": "EVIDENCE_CHECKS_PASSED" if all_checks_pass else "REVIEW_REQUIRED",
    "important_qualification": (
        "Milestone boundaries and acceptance criteria are inferred from the "
        "available repository artifacts. PASS indicates listed evidence checks "
        "passed; it does not certify undocumented official acceptance criteria."
    ),
    "milestones": milestone_summary,
    "checks": CHECKS,
    "details": DETAILS,
    "research_limitations": {
        "pilot_cases": 4,
        "controlled_baseline_comparison_complete": False,
        "ablations_complete": False,
        "standardized_resource_measurements_complete": False,
    },
    "commit_performed": False,
    "push_performed": False,
}

json_path = RESULTS / f"TRACE_MILESTONES_1_TO_4_AUDIT_{STAMP}.json"
md_path = RESULTS / f"TRACE_MILESTONES_1_TO_4_AUDIT_{STAMP}.md"
json_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

lines = [
    "# TRACE Milestones 1–4 Evidence Audit",
    "",
    f"- Generated: {audit['generated_at']}",
    f"- Overall evidence-check status: **{audit['status']}**",
    "",
    "> PASS means the listed checks passed. It does not certify acceptance criteria",
    "> that are not documented in the repository.",
    "",
    "## Summary",
    "",
    "| Milestone | Status | Passed | Total |",
    "|---|---|---:|---:|",
]
for name, info in milestone_summary.items():
    lines.append(
        f"| {name} | {info['status']} | {info['passed_checks']} | {info['total_checks']} |"
    )

for milestone, items in CHECKS.items():
    lines += ["", f"## {milestone}", ""]
    for item in items:
        lines.append(
            f"- **{item['status']}** — {item['check']}: {item['detail']}"
        )

lines += [
    "",
    "## Research limitations",
    "",
    "- Pilot size: four cases.",
    "- Controlled baseline comparison: incomplete.",
    "- Ablations: incomplete.",
    "- Standardized resource measurements: incomplete.",
    "- No commit or push performed.",
    "",
]
md_path.write_text("\n".join(lines), encoding="utf-8")

print("\n===== MILESTONE SUMMARY =====")
for name, info in milestone_summary.items():
    print(
        f"{name}: {info['status']} "
        f"({info['passed_checks']}/{info['total_checks']} checks passed)"
    )
    for failed in info["review_checks"]:
        print(f"  REVIEW: {failed}")

print(f"\nOverall evidence-check status: {audit['status']}")
print(f"JSON audit: {json_path}")
print(f"Markdown audit: {md_path}")
print(f"Tests log: {RESULTS / 'TRACE_MILESTONES_1_TO_4_TESTS.log'}")
print(f"Git diff log: {RESULTS / 'TRACE_MILESTONES_1_TO_4_GIT_DIFF_CHECK.log'}")
print("Commit performed: False")
print("Push performed: False")
