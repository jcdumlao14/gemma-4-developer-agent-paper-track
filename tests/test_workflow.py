import json

import pytest

from trace_research.workflow import run_trace


def make_repo(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "queue.py").write_text(
        "def call_next(waiting_queue):\n"
        "    # remove next guest from waiting queue\n"
        "    return waiting_queue.pop(0)\n",
        encoding="utf-8",
    )
    (tmp_path / "tests" / "test_queue.py").write_text(
        "def test_call_next():\n"
        "    assert call_next(['guest']) == 'guest'\n",
        encoding="utf-8",
    )
    return tmp_path


def test_trace_returns_bounded_evidence_and_discloses_scope(tmp_path):
    root = make_repo(tmp_path)
    report = run_trace(root, "test call next waiting queue", budget=4, limit=3)

    assert report["kind"] == "trace_bounded_evidence_report"
    assert report["not_a_benchmark"] is True
    assert report["not_a_gemma_4_result"] is True
    assert report["repair_attempted"] is False
    assert report["tests_executed"] is False
    assert report["budget"]["actions_used"] <= 4
    assert report["candidates"]
    assert all("path" in item and "excerpts" in item for item in report["candidates"])
    json.dumps(report)


def test_trace_rejects_invalid_inputs(tmp_path):
    root = make_repo(tmp_path)

    with pytest.raises(ValueError, match="nonempty"):
        run_trace(root, "  ")

    with pytest.raises(ValueError, match="budget"):
        run_trace(root, "queue bug", budget=0)

    with pytest.raises(ValueError, match="limit"):
        run_trace(root, "queue bug", limit=0)


def test_trace_prioritizes_test_candidate_when_issue_mentions_failure(tmp_path):
    root = make_repo(tmp_path)
    report = run_trace(root, "failing test call next queue", budget=3, limit=2)

    inspected = [
        step["path"] for step in report["steps"]
        if step["action"] == "inspect_candidate"
    ]
    if "tests/test_queue.py" in inspected:
        assert inspected[0] == "tests/test_queue.py"
