from __future__ import annotations

import argparse
import json
from pathlib import Path

from .benchmark import load_benchmark_cases
from .explorer import inspect_repository
from .workflow import run_trace


def main() -> None:
    parser = argparse.ArgumentParser(prog="trace-research")
    sub = parser.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect", help="rank repository files for a text query")
    inspect.add_argument("root", type=Path)
    inspect.add_argument("--query", required=True)
    inspect.add_argument("--limit", type=int, default=10)
    inspect.add_argument("--output", type=Path)

    trace = sub.add_parser(
        "trace",
        help="produce a bounded, inspect-only evidence trace for an issue",
    )
    trace.add_argument("root", type=Path)
    trace.add_argument("--issue", required=True)
    trace.add_argument("--budget", type=int, default=6)
    trace.add_argument("--limit", type=int, default=5)
    trace.add_argument("--output", type=Path)

    validate = sub.add_parser(
        "validate-benchmark",
        help="validate benchmark metadata without executing repository code",
    )
    validate.add_argument("path", type=Path)

    sub.add_parser("run-demo", help="run a small local demonstration and save explicitly labelled output")
    args = parser.parse_args()

    if args.command == "inspect":
        results = inspect_repository(args.root, args.query, limit=args.limit)
        payload = {
            "kind": "local_repository_inspection",
            "warning": "This is a lexical baseline demonstration, not a benchmark or Gemma 4 result.",
            "query": args.query,
            "results": [item.to_dict() for item in results],
        }
        output = json.dumps(payload, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output + "\n", encoding="utf-8")
        print(output)
    elif args.command == "validate-benchmark":
        try:
            cases = load_benchmark_cases(args.path)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        payload = {
            "kind": "benchmark_validation",
            "valid": True,
            "case_count": len(cases),
            "cases": [
                {
                    "case_id": case["case_id"],
                    "split": case["split"],
                    "synthetic": case["synthetic"],
                }
                for case in cases
            ],
            "note": "Metadata validation only; this does not verify repository access, test reproducibility, benchmark quality, or licensing.",
        }
        print(json.dumps(payload, indent=2))
    elif args.command == "trace":
        report = run_trace(
            args.root,
            args.issue,
            budget=args.budget,
            limit=args.limit,
        )
        output = json.dumps(report, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output + "\n", encoding="utf-8")
        print(output)
    elif args.command == "run-demo":
        root = Path.cwd()
        out = root / "results" / "local_demo.json"
        results = inspect_repository(root, "repository exploration evidence test", limit=10)
        payload = {
            "kind": "local_repository_inspection_demo",
            "not_a_benchmark": True,
            "note": "Do not cite these results as Gemma 4 or software issue resolution performance.",
            "results": [item.to_dict() for item in results],
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Saved local demo (not benchmark results): {out}")


if __name__ == "__main__":
    main()
