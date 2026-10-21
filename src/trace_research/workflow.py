from __future__ import annotations

from pathlib import Path

from .bm25 import rank_repository_bm25
from .explorer import inspect_repository

MAX_INSPECTED_BYTES = 200_000


def _is_test_path(path: str) -> bool:
    parts = path.lower().split("/")
    name = parts[-1]
    return (
        any(part in {"test", "tests", "__tests__"} for part in parts[:-1])
        or name.startswith("test_")
        or name.endswith(("_test.py", ".spec.ts", ".spec.tsx", ".test.ts", ".test.tsx"))
    )


def _excerpt(path: Path, terms: set[str], max_lines: int = 4) -> list[str]:
    """Return a few relevant lines, bounded by file size."""
    try:
        if path.stat().st_size > MAX_INSPECTED_BYTES:
            return ["[Excerpt omitted: file exceeds inspection size limit.]"]
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ["[Excerpt unavailable: file could not be read.]"]

    matching = [
        f"{number}: {line[:300]}"
        for number, line in enumerate(lines, start=1)
        if any(term in line.lower() for term in terms) and line.strip()
    ]
    if matching:
        return matching[:max_lines]

    return [
        f"{number}: {line[:300]}"
        for number, line in enumerate(lines[:max_lines], start=1)
    ]


def run_trace(
    root: str | Path,
    issue: str,
    *,
    budget: int = 6,
    limit: int = 5,
) -> dict:
    """Produce a bounded evidence trace; does not generate or verify repairs."""
    repository = Path(root).resolve()
    if not repository.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {repository}")
    if not isinstance(issue, str) or not issue.strip():
        raise ValueError("issue must be a nonempty string")
    if budget < 1:
        raise ValueError("budget must be >= 1")
    if limit < 1:
        raise ValueError("limit must be >= 1")

    steps: list[dict] = []
    lexical: list[str] = []
    bm25: list[str] = []

    lexical_evidence = inspect_repository(
        repository, issue, limit=max(limit * 3, 10)
    )
    lexical = [item.path for item in lexical_evidence]
    steps.append({
        "action": "lexical_retrieval",
        "reason": "Establish an explainable path/content-overlap baseline.",
        "candidate_count": len(lexical),
    })

    if len(steps) < budget:
        bm25_results = rank_repository_bm25(
            repository, issue, limit=max(limit * 3, 10)
        )
        bm25 = [path for path, _score in bm25_results]
        steps.append({
            "action": "bm25_retrieval",
            "reason": "Add a term-frequency and document-length-normalized ranking.",
            "candidate_count": len(bm25),
        })

    # Reciprocal-rank fusion combines rankings without comparing incompatible scores.
    fused: dict[str, float] = {}
    for ranking in (lexical, bm25):
        for rank, path in enumerate(ranking, start=1):
            fused[path] = fused.get(path, 0.0) + 1.0 / (60 + rank)

    ranked_paths = sorted(fused, key=lambda path: (-fused[path], path))
    inspected: list[dict] = []
    inspected_paths: set[str] = set()
    issue_terms = {
        part.lower()
        for part in issue.replace("_", " ").split()
        if len(part) >= 3
    }

    while len(steps) < budget and len(inspected) < limit:
        remaining = [path for path in ranked_paths if path not in inspected_paths]
        if not remaining:
            steps.append({
                "action": "stop",
                "reason": "No uninspected candidates remain in the retrieval results.",
            })
            break

        # If the issue mentions tests or failures, prioritize an uninspected test file.
        test_language = any(
            word in issue.lower()
            for word in ("test", "tests", "assert", "failure", "failing", "pytest")
        )
        test_candidates = [path for path in remaining if _is_test_path(path)]
        if test_language and test_candidates:
            selected = test_candidates[0]
            selection_reason = (
                "The issue mentions testing or failure, so an available test file "
                "is inspected before the next ordinary candidate."
            )
        else:
            selected = remaining[0]
            selection_reason = (
                "Selected the highest reciprocal-rank-fusion candidate not yet inspected."
            )

        inspected_paths.add(selected)
        excerpts = _excerpt(repository / selected, issue_terms)
        inspected.append({
            "path": selected,
            "fusion_score": round(fused[selected], 8),
            "lexical_rank": lexical.index(selected) + 1 if selected in lexical else None,
            "bm25_rank": bm25.index(selected) + 1 if selected in bm25 else None,
            "is_test_candidate": _is_test_path(selected),
            "excerpts": excerpts,
        })
        steps.append({
            "action": "inspect_candidate",
            "path": selected,
            "reason": selection_reason,
        })

    test_candidates = [
        item["path"] for item in inspected if item["is_test_candidate"]
    ]
    return {
        "kind": "trace_bounded_evidence_report",
        "not_a_benchmark": True,
        "not_a_gemma_4_result": True,
        "repair_attempted": False,
        "tests_executed": False,
        "issue": issue,
        "repository": str(repository),
        "budget": {"max_actions": budget, "actions_used": len(steps)},
        "stop_reason": (
            "action_budget_exhausted"
            if len(steps) >= budget
            else "no_more_candidates_or_inspection_limit_reached"
        ),
        "method": (
            "Lexical retrieval plus BM25 reciprocal-rank fusion, followed by "
            "bounded candidate inspection."
        ),
        "steps": steps,
        "candidates": inspected,
        "inspected_test_candidates": test_candidates,
        "limitations": [
            "This workflow does not call a language model.",
            "Retrieved file excerpts are evidence for inspection, not proof of a defect.",
            "Test files are identified by path naming heuristics.",
            "No patch is generated, applied, or validated.",
            "This report is not a benchmark result.",
        ],
    }
