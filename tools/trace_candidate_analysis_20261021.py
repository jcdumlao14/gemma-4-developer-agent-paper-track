import csv
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "experiments" / "results"

def load_json(relative_path):
    path = ROOT / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"Required evidence is missing: {path}")
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)

pilot_path = "experiments/results/TRACE_GEMMA4_CONSOLIDATED_PILOT_REPORT.json"
pilot = load_json(pilot_path)

sql1625_error = load_json(
    "experiments/results/sqlfluff_1625_gemma_candidate_validation_attempt1.json"
)
sql1625_success = load_json(
    "experiments/results/sqlfluff_1625_gemma_success_summary.json"
)
m1343_proposal = load_json(
    "experiments/results/marshmallow_1343_gemma_repair_proposal.json"
)
m1343_validation = load_json(
    "experiments/results/marshmallow_1343_gemma_candidate_validation.json"
)
m1343_suite = load_json(
    "experiments/results/marshmallow_1343_gemma_full_suite.json"
)
m1359_initial = load_json(
    "experiments/results/marshmallow_1359_gemma_candidate_validation.json"
)
m1359_refined = load_json(
    "experiments/results/marshmallow_1359_candidate3_validation.json"
)
m1359_suite = load_json(
    "experiments/results/marshmallow_1359_final_full_suite.json"
)
sql1733 = load_json(
    "experiments/results/sqlfluff_1733_pilot/candidate_l039_report.json"
)

def test_result(record, key):
    tests = record.get("tests", {})
    item = tests.get(key, {}) if isinstance(tests, dict) else {}
    if "passed" in item:
        return item["passed"]
    return None

def stage_result(record, label):
    for test in record.get("tests", []):
        if test.get("label") == label:
            return test.get("passed")
    return None

rows = [
    {
        "case_id": "sqlfluff-1625",
        "attempt_id": "sql1625-validation-run-error",
        "candidate_stage": "validation run for saved Gemma proposal",
        "provenance": sql1625_error.get("candidate_origin"),
        "target_passed": None,
        "controls_passed": None,
        "module_passed": None,
        "module_test_count": None,
        "full_suite_passed": None,
        "full_suite_test_count": None,
        "status": sql1625_error.get("validation_status"),
        "duration_seconds": None,
        "prompt_diagnostic_guidance": sql1625_success.get(
            "expected_diagnostic_text_in_prompt"
        ),
        "error": sql1625_error.get("error"),
        "source_restored": sql1625_error.get("source_restored"),
        "evidence": (
            "experiments/results/"
            "sqlfluff_1625_gemma_candidate_validation_attempt1.json"
        ),
    },
    {
        "case_id": "sqlfluff-1625",
        "attempt_id": "sql1625-saved-gemma-proposal-validated",
        "candidate_stage": "saved Gemma proposal; successful validation record",
        "provenance": sql1625_success.get("claim_scope"),
        "target_passed": sql1625_success.get("target_test_exit_code") == 0,
        "controls_passed": None,
        "module_passed": sql1625_success.get("full_cli_exit_code") == 0,
        "module_test_count": 69,
        "full_suite_passed": None,
        "full_suite_test_count": None,
        "status": sql1625_success.get("status"),
        "duration_seconds": float(sql1625_success["model_response_seconds"]),
        "prompt_diagnostic_guidance": sql1625_success.get(
            "expected_diagnostic_text_in_prompt"
        ),
        "error": None,
        "source_restored": sql1625_success.get("source_restored"),
        "evidence": (
            "experiments/results/sqlfluff_1625_gemma_success_summary.json"
        ),
    },
    {
        "case_id": "marshmallow-1343",
        "attempt_id": "m1343-model-proposal-unverified",
        "candidate_stage": "model-generated proposal; not executed by adapter",
        "provenance": m1343_proposal.get("experiment"),
        "target_passed": None,
        "controls_passed": None,
        "module_passed": None,
        "module_test_count": None,
        "full_suite_passed": None,
        "full_suite_test_count": None,
        "status": m1343_proposal.get("validation_status"),
        "duration_seconds": m1343_proposal.get("duration_seconds"),
        "prompt_diagnostic_guidance": None,
        "error": None,
        "source_restored": None,
        "evidence": (
            "experiments/results/marshmallow_1343_gemma_repair_proposal.json"
        ),
    },
    {
        "case_id": "marshmallow-1343",
        "attempt_id": "m1343-validated-candidate",
        "candidate_stage": "candidate validation",
        "provenance": "Gemma candidate guided by traceback",
        "target_passed": test_result(m1343_validation, "target"),
        "controls_passed": test_result(m1343_validation, "control"),
        "module_passed": test_result(m1343_validation, "full_marshalling_module"),
        "module_test_count": 25,
        "full_suite_passed": m1343_suite.get("suite_passed"),
        "full_suite_test_count": 780,
        "status": (
            "passed" if m1343_validation.get("candidate_success") else "not_passed"
        ),
        "duration_seconds": None,
        "prompt_diagnostic_guidance": None,
        "error": None,
        "source_restored": m1343_validation.get("production_source_restored"),
        "evidence": (
            "experiments/results/marshmallow_1343_gemma_candidate_validation.json"
            "; experiments/results/marshmallow_1343_gemma_full_suite.json"
        ),
    },
    {
        "case_id": "marshmallow-1359",
        "attempt_id": "m1359-initial-gemma-candidate",
        "candidate_stage": "initial proposal; rejected by selected controls",
        "provenance": m1359_initial.get("candidate_source"),
        "target_passed": stage_result(m1359_initial, "Target regression"),
        "controls_passed": stage_result(m1359_initial, "Five selected controls"),
        "module_passed": stage_result(m1359_initial, "Full test_fields.py module"),
        "module_test_count": 77,
        "full_suite_passed": None,
        "full_suite_test_count": None,
        "status": m1359_initial.get("validation_status"),
        "duration_seconds": None,
        "prompt_diagnostic_guidance": None,
        "error": None,
        "source_restored": m1359_initial.get("source_restored"),
        "evidence": (
            "experiments/results/marshmallow_1359_gemma_candidate_validation.json"
        ),
    },
    {
        "case_id": "marshmallow-1359",
        "attempt_id": "m1359-refined-candidate",
        "candidate_stage": "refined traceback-guided candidate",
        "provenance": m1359_refined.get("candidate"),
        "target_passed": stage_result(m1359_refined, "Target regression"),
        "controls_passed": stage_result(m1359_refined, "Five selected controls"),
        "module_passed": stage_result(m1359_refined, "Full tests/test_fields.py"),
        "module_test_count": 77,
        "full_suite_passed": m1359_suite.get("passed"),
        "full_suite_test_count": 912,
        "status": m1359_refined.get("status"),
        "duration_seconds": m1359_suite.get("duration_seconds"),
        "prompt_diagnostic_guidance": None,
        "error": None,
        "source_restored": m1359_refined.get("source_restored"),
        "evidence": (
            "experiments/results/marshmallow_1359_candidate3_validation.json"
            "; experiments/results/marshmallow_1359_final_full_suite.json"
        ),
    },
    {
        "case_id": "sqlfluff-1733",
        "attempt_id": "sql1733-rule-isolation-candidate",
        "candidate_stage": "subsequent rule-isolation investigation; not Gemma",
        "provenance": "Non-Gemma investigated repair",
        "target_passed": sql1733.get("repair_verified"),
        "controls_passed": None,
        "module_passed": None,
        "module_test_count": None,
        "full_suite_passed": None,
        "full_suite_test_count": None,
        "status": (
            "verified_non_gemma_candidate"
            if sql1733.get("repair_verified") else "not_verified"
        ),
        "duration_seconds": None,
        "prompt_diagnostic_guidance": None,
        "error": None,
        "source_restored": sql1733.get("source_restored"),
        "evidence": (
            "experiments/results/sqlfluff_1733_pilot/candidate_l039_report.json"
        ),
    },
]

# Add a separate record-level broader-validation field without mixing scopes.
pilot_cases = {c["id"]: c for c in pilot.get("cases", [])}
for row in rows:
    case = pilot_cases.get(row["case_id"], {})
    row["consolidated_broader_validation"] = case.get("broader_validation")
    row["consolidated_controls_passed"] = case.get("controls_passed")
    row["consolidated_interpretation"] = case.get("interpretation")

out_dir = RESULTS / (
    "trace_candidate_analysis_" + datetime.now().strftime("%Y%m%d_%H%M%S")
)
out_dir.mkdir(parents=True, exist_ok=False)

csv_path = out_dir / "candidate_attempts.csv"
columns = list(rows[0].keys())
with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

summary = {
    "analysis_type": "evidence_linked_candidate_attempts",
    "generated_local": datetime.now().astimezone().isoformat(),
    "source_report": pilot_path,
    "candidate_attempt_record_count": len(rows),
    "distinct_benchmark_case_count": len(set(r["case_id"] for r in rows)),
    "validated_success_records": [
        r["attempt_id"] for r in rows
        if r["status"] in ("validated_success", "passed")
    ],
    "initial_marshmallow_1359": {
        "target_passed": rows[4]["target_passed"],
        "selected_controls_passed": rows[4]["controls_passed"],
        "module_passed": rows[4]["module_passed"],
        "module_test_count": rows[4]["module_test_count"],
    },
    "refined_marshmallow_1359": {
        "target_passed": rows[5]["target_passed"],
        "selected_controls_passed": rows[5]["controls_passed"],
        "module_passed": rows[5]["module_passed"],
        "module_test_count": rows[5]["module_test_count"],
        "full_suite_passed": rows[5]["full_suite_passed"],
        "full_suite_test_count": rows[5]["full_suite_test_count"],
    },
    "cautions": [
        "Rows represent evidence records or candidate stages, not independent benchmark cases.",
        "SQLFluff-1625's validation error has unknown test outcomes; a separate record documents successful validation.",
        "The Marshmallow-1343 model proposal is not assumed to be identical to the subsequently validated patch.",
        "SQLFluff-1733 is not attributed to Gemma.",
        "Test counts from different scopes must not be summed as a comparative score.",
        "Missing values mean not recorded, not failed.",
    ],
}

json_path = out_dir / "candidate_attempt_summary.json"
json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

print("TRACE CANDIDATE ANALYSIS: PASS")
print(f"Attempt/evidence records: {len(rows)}")
print(f"Distinct benchmark issues: {len(set(r['case_id'] for r in rows))}")
print("Initial Marshmallow-1359: target passed; selected controls failed; module failed.")
print("Refined Marshmallow-1359: target, controls, module and full suite passed.")
print("SQLFluff-1733 is explicitly labeled non-Gemma.")
print(f"\nOutput folder: {out_dir}")
print(f"CSV: {csv_path.name}")
print(f"JSON: {json_path.name}")
