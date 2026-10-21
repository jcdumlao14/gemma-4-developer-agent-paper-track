from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from trace_research.runner import execute_case


def make_repo(path: Path) -> str:
    path.mkdir()
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(
        ["git", "-C", str(path), "config", "user.email", "trace-test@example.invalid"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(path), "config", "user.name", "TRACE Test"],
        check=True,
    )
    (path / "README.md").write_text("temporary runner fixture\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(path), "add", "README.md"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(path), "commit", "-qm", "fixture"],
        check=True,
    )
    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def case_for(commit: str, **overrides):
    case = {
        "case_id": "runner-unit-test",
        "split": "development",
        "synthetic": True,
        "base_commit": commit,
        "test_command": [
            sys.executable,
            "-c",
            "print('TRACE_RUNNER_OK')",
        ],
    }
    case.update(overrides)
    return case


def test_execution_requires_explicit_opt_in(tmp_path):
    repo = tmp_path / "repo"
    commit = make_repo(repo)
    with pytest.raises(ValueError, match="disabled"):
        execute_case(case_for(commit), repo, allow_synthetic=True)


def test_synthetic_case_requires_explicit_opt_in(tmp_path):
    repo = tmp_path / "repo"
    commit = make_repo(repo)
    with pytest.raises(ValueError, match="Synthetic case blocked"):
        execute_case(
            case_for(commit),
            repo,
            allow_command_execution=True,
        )


def test_commit_must_match_exactly(tmp_path):
    repo = tmp_path / "repo"
    commit = make_repo(repo)
    wrong = "0" * 40
    assert wrong != commit
    with pytest.raises(ValueError, match="Commit mismatch"):
        execute_case(
            case_for(wrong),
            repo,
            allow_command_execution=True,
            allow_synthetic=True,
        )


def test_clean_pinned_synthetic_case_runs_and_is_labeled(tmp_path):
    repo = tmp_path / "repo"
    commit = make_repo(repo)
    result = execute_case(
        case_for(commit),
        repo,
        allow_command_execution=True,
        allow_synthetic=True,
    )
    assert result["status"] == "passed"
    assert result["exit_code"] == 0
    assert "TRACE_RUNNER_OK" in result["stdout"]
    assert result["base_commit"] == commit
    assert result["synthetic"] is True
    assert result["patch_applied"] is False
    assert result["model_invoked"] is False
    assert result["repair_attempted"] is False


def test_dirty_worktree_is_rejected(tmp_path):
    repo = tmp_path / "repo"
    commit = make_repo(repo)
    (repo / "README.md").write_text("modified\n", encoding="utf-8")
    with pytest.raises(ValueError, match="not clean"):
        execute_case(
            case_for(commit),
            repo,
            allow_command_execution=True,
            allow_synthetic=True,
        )


@pytest.mark.parametrize("split", ["validation", "test", "held_out"])
def test_non_development_splits_require_explicit_opt_in(tmp_path, split):
    repo = tmp_path / "repo"
    commit = make_repo(repo)
    case = case_for(commit, split=split, synthetic=False)
    with pytest.raises(ValueError, match="Evaluation-split execution is blocked"):
        execute_case(
            case,
            repo,
            allow_command_execution=True,
        )


def test_unsupported_evaluation_split_label_is_rejected(tmp_path):
    repo = tmp_path / "repo"
    commit = make_repo(repo)
    case = case_for(commit, split="evaluation", synthetic=False)
    with pytest.raises(ValueError, match="Unsupported split"):
        execute_case(
            case,
            repo,
            allow_command_execution=True,
        )


def test_failed_test_command_is_recorded_not_raised(tmp_path):
    repo = tmp_path / "repo"
    commit = make_repo(repo)
    case = case_for(
        commit,
        test_command=[sys.executable, "-c", "raise SystemExit(7)"],
    )
    result = execute_case(
        case,
        repo,
        allow_command_execution=True,
        allow_synthetic=True,
    )
    assert result["status"] == "failed"
    assert result["exit_code"] == 7

@pytest.mark.parametrize("split", ["validation", "test", "held_out"])
def test_non_development_splits_allow_explicit_opt_in(tmp_path, split):
    repo = tmp_path / "repo"
    commit = make_repo(repo)
    case = case_for(
        commit,
        split=split,
        synthetic=False,
        test_command=[
            sys.executable,
            "-c",
            "print('TRACE_EXPLICIT_OPT_IN_OK')",
        ],
    )
    result = execute_case(
        case,
        repo,
        allow_command_execution=True,
        allow_evaluation_split=True,
    )
    assert result["status"] == "passed"
    assert result["exit_code"] == 0
    assert result["split"] == split
