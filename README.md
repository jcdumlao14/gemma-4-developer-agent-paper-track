# TRACE: Test-Guided Repository Exploration and Evidence-Grounded Repair

Research scaffold for the Google – The Gemma 4 Developer Agent Paper Track.

## Research question
Does structured, evidence-based repository exploration improve localization and verification efficiency for software-engineering agents under a fixed tool/context budget?

## Status
**Prototype scaffold.** The included repository explorer and tests are local software tests, not a Gemma 4 benchmark. No benchmark success rates or performance claims should be reported until experiments are run and recorded.

## Quick start (Python 3.11+ recommended)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"
pytest
python -m trace_research.cli inspect . --query "repository exploration"
python -m trace_research.cli run-demo
```

## Structure
- `src/trace_research/`: prototype repository inspection and evidence ranking.
- `tests/`: unit tests for deterministic behavior.
- `experiments/configs/`: experiment protocol configuration.
- `experiments/scripts/`: repeatable experiment entry point.
- `results/`: generated local-demo outputs (not benchmark results).
- `paper/`: manuscript scaffold and reference checklist.
- `docs/`: experiment protocol and data provenance notes.

## Research integrity
- Never label demo results as benchmark results.
- Record model/version, task IDs, commit hashes, environment, budgets, failures, and raw outputs.
- Do not use hidden test labels or benchmark solutions for tuning.
- Confirm dataset/model licenses and competition rules before public release.
- The proposed TRACE method is a hypothesis to test, not an established improvement.
