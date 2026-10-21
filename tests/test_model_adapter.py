import io
import json

import pytest

from trace_research import model_adapter


def test_build_prompt_includes_failure_and_source():
    prompt = model_adapter.build_repair_prompt(
        "case-1",
        "AssertionError: expected A",
        {"queue.py": "return queue[1]"},
    )
    assert "case-1" in prompt
    assert "AssertionError: expected A" in prompt
    assert "return queue[1]" in prompt
    assert "will not be applied automatically" in prompt


@pytest.mark.parametrize("path", ["../secret.py", r"..\secret.py", "C:\\secret.py"])
def test_rejects_unsafe_paths(path):
    with pytest.raises(ValueError, match="Unsafe"):
        model_adapter.build_repair_prompt(
            "case-1", "failure", {path: "secret"}
        )


def test_rejects_too_many_files():
    files = {f"file{i}.py": "x" for i in range(6)}
    with pytest.raises(ValueError, match="At most"):
        model_adapter.build_repair_prompt("case-1", "failure", files)


def test_proposal_records_response_without_applying_patch(monkeypatch):
    def fake_urlopen(request, timeout):
        body = json.loads(request.data.decode("utf-8"))
        assert request.full_url == "http://localhost:11434/api/chat"
        assert body["model"] == "gemma4:cloud"
        assert body["stream"] is False
        return io.BytesIO(
            json.dumps({
                "model": "gemma4:cloud",
                "created_at": "2026-10-20T00:00:00Z",
                "message": {
                    "role": "assistant",
                    "content": "Change queue[1] to queue[0].",
                },
                "prompt_eval_count": 100,
                "eval_count": 12,
            }).encode("utf-8")
        )

    monkeypatch.setattr(model_adapter.urllib.request, "urlopen", fake_urlopen)
    result = model_adapter.propose_repair(
        case_id="synthetic-1",
        failing_test_output="Expected A, got B",
        files={"queue.py": "return queue[1]"},
    )

    assert result["response"] == "Change queue[1] to queue[0]."
    assert result["model_invoked"] is True
    assert result["patch_applied"] is False
    assert result["commands_executed"] is False
    assert result["repair_verified"] is False
    assert len(result["prompt_sha256"]) == 64


def test_rejects_invalid_timeout():
    with pytest.raises(ValueError, match="timeout_seconds"):
        model_adapter.propose_repair(
            case_id="synthetic-1",
            failing_test_output="failure",
            files={"queue.py": "pass"},
            timeout_seconds=0,
        )


def test_rejects_empty_model_response(monkeypatch):
    def fake_urlopen(request, timeout):
        return io.BytesIO(
            json.dumps({"message": {"content": ""}}).encode("utf-8")
        )

    monkeypatch.setattr(model_adapter.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(RuntimeError, match="message.content"):
        model_adapter.propose_repair(
            case_id="synthetic-1",
            failing_test_output="failure",
            files={"queue.py": "pass"},
        )
