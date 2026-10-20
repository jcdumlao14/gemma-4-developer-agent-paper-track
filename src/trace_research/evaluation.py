from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean

from .bm25 import rank_repository_bm25
from .explorer import inspect_repository

EVALUATION_EXCLUSIONS = (
    'tests/test_evaluation.py',
    'experiments/fixtures/retrieval_cases.json',
    'src/trace_research/evaluation.py',
    'results/retrieval_fixture_eval.json',
    'setup_trace_evaluation.py',
    'setup_trace_project.py',
    'fix_trace_evaluation_leakage.py',
    'src/trace_research/bm25.py',
    'tests/test_bm25.py',
    'add_trace_bm25.py',
    'results/retrieval_fixture_eval_lexical.json',
    'results/retrieval_fixture_eval_bm25.json',
)


def recall_at_k(ranked_paths: list[str], relevant_paths: set[str], k: int) -> float:
    """Return the fraction of relevant files retrieved in the first k results."""
    if k < 1:
        raise ValueError("k must be >= 1")
    if not relevant_paths:
        raise ValueError("relevant_paths must not be empty")
    found = set(ranked_paths[:k]) & relevant_paths
    return len(found) / len(relevant_paths)


def reciprocal_rank(ranked_paths: list[str], relevant_paths: set[str]) -> float:
    """Return the reciprocal rank of the first relevant result, or zero."""
    if not relevant_paths:
        raise ValueError("relevant_paths must not be empty")
    for rank, path in enumerate(ranked_paths, start=1):
        if path in relevant_paths:
            return 1.0 / rank
    return 0.0


def evaluate_cases(
    root: str | Path,
    cases: list[dict],
    *,
    ks: tuple[int, ...] = (1, 3, 5),
    limit: int = 10,
    method: str = "lexical",
) -> dict:
    """Evaluate retrieval against explicitly labelled development cases."""
    root = Path(root).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")
    if not cases:
        raise ValueError("At least one evaluation case is required")
    if not ks or any(k < 1 for k in ks):
        raise ValueError("ks must contain positive integers")
    if limit < 1:
        raise ValueError("limit must be >= 1")
    if method not in {"lexical", "bm25"}:
        raise ValueError("method must be lexical or bm25")

    rows = []
    seen_ids = set()

    for case in cases:
        case_id = case.get("id")
        query = case.get("query")
        relevant = case.get("relevant_paths")

        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError("Every case needs a nonempty string id")
        if case_id in seen_ids:
            raise ValueError(f"Duplicate case id: {case_id}")
        seen_ids.add(case_id)

        if not isinstance(query, str) or not query.strip():
            raise ValueError(f"{case_id}: query must be a nonempty string")
        if not isinstance(relevant, list) or not relevant:
            raise ValueError(f"{case_id}: relevant_paths must be a nonempty list")
        if len(relevant) != len(set(relevant)):
            raise ValueError(f"{case_id}: duplicate relevant paths")

        for rel_path in relevant:
            candidate = (root / rel_path).resolve()
            if not candidate.is_relative_to(root) or not candidate.is_file():
                raise ValueError(
                    f"{case_id}: labelled file does not exist inside repository: "
                    f"{rel_path}"
                )

        if method == "lexical":
            ranked = [
                item.path
                for item in inspect_repository(
                    root,
                    query,
                    limit=limit,
                    exclude_paths=EVALUATION_EXCLUSIONS,
                )
            ]
        else:
            ranked = [
                path
                for path, _score in rank_repository_bm25(
                    root,
                    query,
                    limit=limit,
                    exclude_paths=EVALUATION_EXCLUSIONS,
                )
            ]
        relevant_set = set(relevant)
        ranks = [
            index
            for index, path in enumerate(ranked, start=1)
            if path in relevant_set
        ]

        row = {
            "id": case_id,
            "query": query,
            "relevant_paths": relevant,
            "ranked_paths": ranked,
            "first_relevant_rank": min(ranks) if ranks else None,
            "reciprocal_rank": reciprocal_rank(ranked, relevant_set),
            "recall_at_k": {
                str(k): recall_at_k(ranked, relevant_set, k)
                for k in ks
            },
        }
        rows.append(row)

    summary = {
        "case_count": len(rows),
        "mean_reciprocal_rank": mean(row["reciprocal_rank"] for row in rows),
        "mean_recall_at_k": {
            str(k): mean(row["recall_at_k"][str(k)] for row in rows)
            for k in ks
        },
    }

    return {
        "kind": "local_retrieval_fixture_evaluation",
        "not_a_benchmark": True,
        "not_a_gemma_4_result": True,
        "method": ("deterministic lexical-overlap repository retrieval" if method == "lexical" else "BM25 lexical retrieval"),
        "label_scope": "local development fixtures only",
        "metric_definitions": {
            "recall_at_k": "Relevant files in top k divided by all labelled relevant files.",
            "reciprocal_rank": "1 divided by the rank of the first relevant file; zero if absent.",
            "mean_reciprocal_rank": "Mean reciprocal rank across evaluation cases.",
        },
        "ks": list(ks),
        "limit": limit,
        "summary": summary,
        "cases": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate TRACE lexical retrieval on local development fixtures."
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--cases",
        type=Path,
        default=Path("experiments/fixtures/retrieval_cases.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/retrieval_fixture_eval.json"),
    )
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--method", choices=("lexical", "bm25"), default="lexical")
    args = parser.parse_args()

    root = args.root.resolve()
    cases_file = args.cases
    if not cases_file.is_absolute():
        cases_file = root / cases_file

    fixture_data = json.loads(cases_file.read_text(encoding="utf-8"))
    report = evaluate_cases(
        root, fixture_data["cases"], limit=args.limit, method=args.method
    )

    output_path = args.output
    if not output_path.is_absolute():
        output_path = root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Evaluation report saved: {output_path}")
    print("Scope: local development fixtures only; not a benchmark.")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
