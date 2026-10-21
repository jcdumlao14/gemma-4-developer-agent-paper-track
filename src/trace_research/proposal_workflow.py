"""Evidence-guided repair proposal workflow; never applies patches or runs tests."""
from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from .model_adapter import MAX_FILE_CHARS, MAX_FILES, propose_repair
from .workflow import run_trace

DEFAULT_MAX_FILES = 3


def run_trace_proposal(
    root: str | Path,
    issue: str,
    failing_test_output: str,
    *,
    case_id: str,
    budget: int = 6,
    limit: int = 5,
    max_files: int = DEFAULT_MAX_FILES,
    model: str | None = None,
    base_url: str | None = None,
    timeout_seconds: int = 120,
) -> dict[str, Any]:
    """Run TRACE and request a proposal using safe, bounded candidate files."""
    repository = Path(root).resolve()
    if not isinstance(max_files, int) or not 1 <= max_files <= MAX_FILES:
        raise ValueError(f"max_files must be between 1 and {MAX_FILES}.")
    if not isinstance(failing_test_output, str) or not failing_test_output.strip():
        raise ValueError("failing_test_output must be a non-empty string.")
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError("case_id must be a non-empty string.")

    trace = run_trace(repository, issue, budget=budget, limit=limit)
    files: dict[str, str] = {}
    records: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []

    for candidate in trace.get("candidates", []):
        if len(files) >= max_files:
            break
        relative = candidate.get("path")
        if not isinstance(relative, str) or not relative.strip():
            skipped.append({"path": str(relative), "reason": "invalid path"})
            continue

        posix = PurePosixPath(relative.replace("\\", "/"))
        windows = PureWindowsPath(relative)
        if posix.is_absolute() or windows.is_absolute() or windows.drive or ".." in posix.parts:
            skipped.append({"path": relative, "reason": "unsafe path"})
            continue

        target = (repository / Path(*posix.parts)).resolve()
        try:
            target.relative_to(repository)
        except ValueError:
            skipped.append({"path": relative, "reason": "path escapes repository"})
            continue
        if not target.is_file():
            skipped.append({"path": relative, "reason": "not a regular file"})
            continue
        try:
            if target.stat().st_size > 200_000:
                skipped.append({"path": relative, "reason": "file exceeds 200000-byte limit"})
                continue
            raw_bytes = target.read_bytes()
            content = raw_bytes.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
        except OSError:
            skipped.append({"path": relative, "reason": "read failed"})
            continue
        if len(content) > MAX_FILE_CHARS:
            skipped.append({"path": relative, "reason": "file exceeds adapter character limit"})
            continue

        files[relative] = content
        records.append({
            "path": relative,
            "sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "characters": len(content),
        })

    if not files:
        raise ValueError(
            "TRACE found no readable, bounded candidate files suitable for a proposal."
        )

    proposal = propose_repair(
        case_id=case_id,
        failing_test_output=failing_test_output,
        files=files,
        model=model,
        base_url=base_url,
        timeout_seconds=timeout_seconds,
    )
    return {
        "kind": "trace_model_proposal_report",
        "case_id": case_id,
        "repository": str(repository),
        "issue": issue,
        "trace_report": trace,
        "supplied_files": records,
        "skipped_files": skipped,
        "proposal": proposal,
        "model_invoked": proposal["model_invoked"],
        "patch_applied": False,
        "commands_executed": False,
        "tests_executed": False,
        "repair_verified": False,
        "not_a_benchmark": True,
        "note": (
            "Model proposal only. No patch was applied, no repository commands "
            "were executed, and no repair verification was performed."
        ),
    }