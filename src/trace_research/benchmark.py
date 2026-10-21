from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ALLOWED_SPLITS = {"development", "validation", "test", "held_out"}
CASE_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
COMMIT_PATTERN = re.compile(r"^[0-9a-fA-F]{40}$")
ALLOWED_FIELDS = {
    "case_id",
    "repository_url",
    "base_commit",
    "issue",
    "split",
    "test_command",
    "expected_failing_tests",
    "relevant_files",
    "license",
    "provenance",
    "synthetic",
}


def validate_benchmark_payload(payload: Any) -> list[str]:
    errors: list[str] = []

    if not isinstance(payload, dict):
        return ["The benchmark document must be a JSON object."]

    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        return ["'cases' must be a non-empty list."]

    seen_ids: set[str] = set()

    for index, case in enumerate(cases):
        prefix = f"cases[{index}]"

        if not isinstance(case, dict):
            errors.append(f"{prefix} must be an object.")
            continue

        missing = sorted(ALLOWED_FIELDS - case.keys())
        unknown = sorted(case.keys() - ALLOWED_FIELDS)
        if unknown:
            errors.append(f"{prefix} has unknown fields: {', '.join(unknown)}")
        if missing:
            errors.append(f"{prefix} is missing fields: {', '.join(missing)}")

        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not CASE_ID_PATTERN.fullmatch(case_id):
            errors.append(f"{prefix}.case_id must be a lowercase hyphenated identifier.")
        elif case_id in seen_ids:
            errors.append(f"{prefix}.case_id duplicates '{case_id}'.")
        else:
            seen_ids.add(case_id)

        url = case.get("repository_url")
        valid_url = (
            isinstance(url, str)
            and url.startswith(("https://", "ssh://"))
            and bool(url.split("://", 1)[1].strip())
        )
        if not valid_url:
            errors.append(
                f"{prefix}.repository_url must use HTTPS or SSH and include a host."
            )

        commit = case.get("base_commit")
        if not isinstance(commit, str) or not COMMIT_PATTERN.fullmatch(commit):
            errors.append(f"{prefix}.base_commit must be a full 40-character Git commit hash.")

        issue = case.get("issue")
        if not isinstance(issue, str) or not issue.strip():
            errors.append(f"{prefix}.issue must be non-empty.")

        split = case.get("split")
        if not isinstance(split, str) or split not in ALLOWED_SPLITS:
            errors.append(
                f"{prefix}.split must be one of: {', '.join(sorted(ALLOWED_SPLITS))}."
            )

        for field in ("test_command", "expected_failing_tests", "relevant_files"):
            value = case.get(field)
            if (
                not isinstance(value, list)
                or not value
                or any(not isinstance(item, str) or not item.strip() for item in value)
            ):
                errors.append(f"{prefix}.{field} must be a non-empty list of strings.")

        for field in ("license", "provenance"):
            value = case.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{prefix}.{field} must be non-empty.")

        if not isinstance(case.get("synthetic"), bool):
            errors.append(f"{prefix}.synthetic must be true or false.")

    return errors


def load_benchmark_cases(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8-sig"))
    errors = validate_benchmark_payload(payload)

    if errors:
        raise ValueError("Invalid benchmark document:\n- " + "\n- ".join(errors))

    return payload["cases"]
