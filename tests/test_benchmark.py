import json
from pathlib import Path

import pytest

from trace_research.benchmark import (
    load_benchmark_cases,
    validate_benchmark_payload,
)


def valid_case():
    return {
        "case_id": "queue-off-by-one",
        "repository_url": "https://example.invalid/queue",
        "base_commit": "a" * 40,
        "issue": "Return the first waiting guest.",
        "split": "development",
        "test_command": ["python", "-m", "pytest", "-q"],
        "expected_failing_tests": ["tests/test_queue.py::test_next_guest"],
        "relevant_files": ["src/queue.py", "tests/test_queue.py"],
        "license": "Synthetic test fixture",
        "provenance": "Unit test only",
        "synthetic": True,
    }


def test_valid_case_has_no_validation_errors():
    assert validate_benchmark_payload({"cases": [valid_case()]}) == []


def test_example_case_loads_and_is_explicitly_synthetic():
    root = Path(__file__).resolve().parents[1]
    cases = load_benchmark_cases(root / "experiments" / "benchmark_cases.example.json")

    assert len(cases) == 1
    assert cases[0]["synthetic"] is True
    assert cases[0]["split"] == "development"


def test_invalid_commit_is_rejected():
    case = valid_case()
    case["base_commit"] = "not-a-commit"

    errors = validate_benchmark_payload({"cases": [case]})

    assert any("base_commit" in error for error in errors)


def test_duplicate_case_ids_are_rejected():
    case = valid_case()

    errors = validate_benchmark_payload({"cases": [case, case.copy()]})

    assert any("duplicates" in error for error in errors)


def test_unknown_split_is_rejected():
    case = valid_case()
    case["split"] = "training-data"

    errors = validate_benchmark_payload({"cases": [case]})

    assert any(".split" in error for error in errors)


def test_loader_rejects_invalid_json_document(tmp_path):
    path = tmp_path / "invalid.json"
    case = valid_case()
    case["base_commit"] = "short"
    path.write_text(json.dumps({"cases": [case]}), encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid benchmark document"):
        load_benchmark_cases(path)


def test_non_object_payload_is_rejected():
    assert validate_benchmark_payload([]) == [
        "The benchmark document must be a JSON object."
    ]


def test_unknown_fields_are_rejected():
    case = valid_case()
    case["unexpected_field"] = "not allowed by schema"

    errors = validate_benchmark_payload({"cases": [case]})

    assert any("unknown fields" in error for error in errors)


def test_empty_url_host_is_rejected():
    case = valid_case()
    case["repository_url"] = "https://"

    errors = validate_benchmark_payload({"cases": [case]})

    assert any("repository_url" in error for error in errors)


def test_non_string_split_is_rejected_without_crashing():
    case = valid_case()
    case["split"] = ["development"]

    errors = validate_benchmark_payload({"cases": [case]})

    assert any(".split" in error for error in errors)
