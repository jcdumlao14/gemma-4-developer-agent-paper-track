from pathlib import Path

import pytest

from trace_research.evaluation import (
    evaluate_cases,
    recall_at_k,
    reciprocal_rank,
)


def test_recall_at_k():
    ranked = ["a.py", "b.py", "c.py"]
    assert recall_at_k(ranked, {"b.py", "c.py"}, 2) == 0.5
    assert recall_at_k(ranked, {"b.py", "c.py"}, 3) == 1.0


def test_reciprocal_rank():
    assert reciprocal_rank(["a.py", "b.py"], {"b.py"}) == 0.5
    assert reciprocal_rank(["a.py"], {"missing.py"}) == 0.0


def test_metrics_reject_invalid_inputs():
    with pytest.raises(ValueError):
        recall_at_k(["a.py"], {"a.py"}, 0)
    with pytest.raises(ValueError):
        reciprocal_rank(["a.py"], set())


def test_evaluation_report_is_explicitly_development_only(tmp_path: Path):
    (tmp_path / "target.py").write_text(
        "def repository_evidence_test():\n    return True\n",
        encoding="utf-8",
    )
    report = evaluate_cases(
        tmp_path,
        [{
            "id": "small-test",
            "query": "repository evidence test",
            "relevant_paths": ["target.py"],
        }],
    )
    assert report["not_a_benchmark"] is True
    assert report["not_a_gemma_4_result"] is True
    assert report["summary"]["case_count"] == 1
    assert report["cases"][0]["reciprocal_rank"] > 0


def test_evaluation_rejects_missing_label(tmp_path: Path):
    with pytest.raises(ValueError, match="does not exist"):
        evaluate_cases(
            tmp_path,
            [{
                "id": "bad-label",
                "query": "missing file",
                "relevant_paths": ["missing.py"],
            }],
        )
