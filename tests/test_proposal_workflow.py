import hashlib

import pytest

from trace_research import proposal_workflow as pw


def test_proposal_records_hashes_and_never_applies_patch(tmp_path, monkeypatch):
    source = tmp_path / "src" / "queue.py"
    source.parent.mkdir()
    source.write_text("def next_item(items):\n    return items.pop(0)\n", encoding="utf-8")
    trace = {"candidates": [{"path": "src/queue.py"}]}

    monkeypatch.setattr(pw, "run_trace", lambda *a, **k: trace)

    def fake_propose(**kwargs):
        assert kwargs["files"]["src/queue.py"] == source.read_text(encoding="utf-8")
        return {
            "model_invoked": True,
            "patch_applied": False,
            "commands_executed": False,
            "repair_verified": False,
            "response": "Proposal only",
        }

    monkeypatch.setattr(pw, "propose_repair", fake_propose)
    report = pw.run_trace_proposal(
        tmp_path, "queue failing test", "AssertionError", case_id="synthetic-1"
    )
    expected = hashlib.sha256(source.read_bytes()).hexdigest()
    assert report["supplied_files"][0]["sha256"] == expected
    assert report["patch_applied"] is False
    assert report["commands_executed"] is False
    assert report["tests_executed"] is False
    assert report["repair_verified"] is False
    assert report["not_a_benchmark"] is True


@pytest.mark.parametrize("bad_path", ["../outside.py", r"..\outside.py", "C:\\outside.py"])
def test_unsafe_paths_are_skipped(tmp_path, monkeypatch, bad_path):
    monkeypatch.setattr(
        pw, "run_trace", lambda *a, **k: {"candidates": [{"path": bad_path}]}
    )
    with pytest.raises(ValueError, match="no readable"):
        pw.run_trace_proposal(
            tmp_path, "failing test", "AssertionError", case_id="synthetic-unsafe"
        )


def test_invalid_max_files_rejected(tmp_path):
    with pytest.raises(ValueError, match="max_files"):
        pw.run_trace_proposal(
            tmp_path, "failing test", "AssertionError",
            case_id="synthetic-invalid", max_files=0
        )


def test_missing_candidate_file_does_not_call_model(tmp_path, monkeypatch):
    monkeypatch.setattr(
        pw, "run_trace", lambda *a, **k: {"candidates": [{"path": "missing.py"}]}
    )
    monkeypatch.setattr(
        pw, "propose_repair",
        lambda **kwargs: pytest.fail("Model adapter must not be called")
    )
    with pytest.raises(ValueError, match="no readable"):
        pw.run_trace_proposal(
            tmp_path, "missing file test", "AssertionError", case_id="synthetic-missing"
        )