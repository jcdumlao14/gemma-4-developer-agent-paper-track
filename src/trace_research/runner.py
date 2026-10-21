"""Explicitly authorized, commit-pinned baseline test runner.

This runner executes declared test commands only after an explicit opt-in.
It does not clone repositories, invoke an LLM, apply patches, or repair code.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

MAX_CAPTURE_CHARS = 20_000


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def git_output(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=15,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(
            f"Git command failed ({' '.join(args)}): "
            f"{result.stderr.strip()}"
        )
    return result.stdout.strip()


def normalize_command(value: Any) -> list[str]:
    """Accept either an argv array or a one-element shell-like command string."""
    if not isinstance(value, list) or not value:
        raise ValueError("test_command must be a non-empty list of strings.")
    if not all(isinstance(part, str) and part.strip() for part in value):
        raise ValueError("test_command must contain only non-empty strings.")

    # A one-item command is split without invoking a shell.
    if len(value) == 1:
        try:
            parts = shlex.split(value[0], posix=(sys.platform != "win32"))
        except ValueError as exc:
            raise ValueError(f"Cannot parse test_command: {exc}") from exc
        if not parts:
            raise ValueError("test_command resolved to an empty command.")
        return parts

    return value


def execute_case(
    case: dict[str, Any],
    repo_root: str | Path,
    *,
    timeout_seconds: int = 120,
    allow_command_execution: bool = False,
    allow_synthetic: bool = False,
    allow_evaluation_split: bool = False,
) -> dict[str, Any]:
    """Execute one declared test command in a clean, exact-commit checkout."""
    if not allow_command_execution:
        raise ValueError(
            "Command execution is disabled. Pass --allow-command-execution "
            "only after reviewing the case and repository."
        )

    if not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= 3600:
        raise ValueError("timeout_seconds must be an integer from 1 to 3600.")

    case_id = case.get("case_id")
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError("Case is missing a valid case_id.")

    if case.get("synthetic") is True and not allow_synthetic:
        raise ValueError(
            "Synthetic case blocked. Pass --allow-synthetic for a local demo."
        )

    split = case.get("split")
    allowed_splits = {"development", "validation", "test", "held_out"}
    if split not in allowed_splits:
        raise ValueError(f"Unsupported split: {split!r}")
    if split != "development" and not allow_evaluation_split:
        raise ValueError(
            f"Evaluation-split execution is blocked for {split!r} by default. "
            "Use a development case, or explicitly pass "
            "--allow-evaluation-split after freezing your method."
        )

    expected_commit = case.get("base_commit")
    if not isinstance(expected_commit, str) or not re.fullmatch(
        r"[0-9a-fA-F]{40}", expected_commit
    ):
        raise ValueError("base_commit must be a full 40-character Git hash.")

    command = normalize_command(case.get("test_command"))
    repo = Path(repo_root).expanduser().resolve()
    if not repo.is_dir():
        raise ValueError(f"Repository directory does not exist: {repo}")

    actual_commit = git_output(repo, "rev-parse", "HEAD")
    if actual_commit.lower() != expected_commit.lower():
        raise ValueError(
            f"Commit mismatch: expected {expected_commit}, got {actual_commit}"
        )

    dirty = git_output(repo, "status", "--porcelain")
    if dirty:
        raise ValueError(
            "Repository working tree is not clean. Commit or safely stash "
            "changes before running this case."
        )

    started_at = utc_now()
    start = time.monotonic()
    timed_out = False
    exit_code: int | None = None
    stdout = ""
    stderr = ""

    try:
        completed = subprocess.run(
            command,
            cwd=repo,
            shell=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
        status = "passed" if exit_code == 0 else "failed"
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        status = "timeout"
        stdout = (
            exc.stdout.decode("utf-8", errors="replace")
            if isinstance(exc.stdout, bytes)
            else (exc.stdout or "")
        )
        stderr = (
            exc.stderr.decode("utf-8", errors="replace")
            if isinstance(exc.stderr, bytes)
            else (exc.stderr or "")
        )
    except OSError as exc:
        status = "launch_error"
        stderr = str(exc)

    elapsed = round(time.monotonic() - start, 4)

    return {
        "kind": "baseline_test_run",
        "case_id": case_id,
        "split": split,
        "synthetic": case.get("synthetic") is True,
        "repository_path": str(repo),
        "base_commit": actual_commit,
        "command": command,
        "started_at_utc": started_at,
        "finished_at_utc": utc_now(),
        "duration_seconds": elapsed,
        "timeout_seconds": timeout_seconds,
        "timed_out": timed_out,
        "exit_code": exit_code,
        "status": status,
        "stdout": stdout[:MAX_CAPTURE_CHARS],
        "stderr": stderr[:MAX_CAPTURE_CHARS],
        "stdout_truncated": len(stdout) > MAX_CAPTURE_CHARS,
        "stderr_truncated": len(stderr) > MAX_CAPTURE_CHARS,
        "patch_applied": False,
        "model_invoked": False,
        "repair_attempted": False,
        "note": (
            "This is a baseline test-command run, not evidence of a repaired "
            "issue or a Gemma 4 result. Review command, repository, licensing, "
            "and captured output before reporting."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run one declared test command in a pinned local checkout."
    )
    parser.add_argument("--benchmark-file", required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument(
        "--allow-command-execution",
        action="store_true",
        help="Required opt-in: execute the declared test command.",
    )
    parser.add_argument(
        "--allow-synthetic",
        action="store_true",
        help="Allow a case explicitly labeled synthetic.",
    )
    parser.add_argument(
        "--allow-evaluation-split",
        action="store_true",
        help="Allow validation/test/held-out execution after freezing your method.",
    )
    args = parser.parse_args(argv)

    try:
        # Reuse the repository's existing benchmark metadata validator.
        from trace_research.benchmark import load_benchmark_cases

        cases = load_benchmark_cases(args.benchmark_file)
        matches = [case for case in cases if case.get("case_id") == args.case_id]
        if len(matches) != 1:
            raise ValueError(
                f"Expected exactly one case for {args.case_id!r}; "
                f"found {len(matches)}."
            )

        report = execute_case(
            matches[0],
            args.repo_root,
            timeout_seconds=args.timeout_seconds,
            allow_command_execution=args.allow_command_execution,
            allow_synthetic=args.allow_synthetic,
            allow_evaluation_split=args.allow_evaluation_split,
        )

        output = Path(args.output).expanduser().resolve()
        if output.exists():
            raise ValueError(
                f"Refusing to overwrite existing result: {output}"
            )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"\nSaved result: {output}")
        return 0

    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
