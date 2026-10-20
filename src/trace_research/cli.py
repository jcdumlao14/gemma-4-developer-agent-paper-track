from __future__ import annotations

import argparse
import json
from pathlib import Path

from .explorer import inspect_repository


def main() -> None:
    parser = argparse.ArgumentParser(prog="trace-research")
    sub = parser.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect", help="rank repository files for a text query")
    inspect.add_argument("root", type=Path)
    inspect.add_argument("--query", required=True)
    inspect.add_argument("--limit", type=int, default=10)
    inspect.add_argument("--output", type=Path)

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
