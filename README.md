# TRACE: Test-Guided Repository Exploration and Evidence-Grounded Repair

Research scaffold for the Google – The Gemma 4 Developer Agent Paper Track.

## Research question
Does structured, evidence-based repository exploration improve localization and verification efficiency for software-engineering agents under a fixed tool/context budget?

## Status
**Research prototype.** The workflow combines lexical and BM25 retrieval with bounded evidence inspection. The optional `propose` command can invoke a configured model (including Gemma 4 through Ollama) to produce a repair proposal from bounded repository evidence. It does not automatically apply the proposed patch or execute tests in the target repository. Local unit tests verify implementation behavior only; they are not benchmark results. The four-case pilot is limited, the controlled baseline comparison remains incomplete, and no benchmark-wide effectiveness claim is established.

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

## TRACE Evidence Dashboard

TRACE includes a local, read-only dashboard for navigating available
research reports and implementation evidence.

- **Methodology and usage:** [TRACE Dashboard Methodology and User Guide](tools/TRACE_DASHBOARD_README.md)
- **Dashboard implementation:** `tools/trace_dashboard.py`
- **Run locally:** `python tools/trace_dashboard.py`
- **Local address:** `http://127.0.0.1:8765`

The dashboard organizes available evidence; it does not independently
reproduce historical benchmark results. A model proposal is not proof of
a successful repair, and recorded test outcomes should not be presented
as independently reproduced results. The four-case pilot remains limited,
the controlled baseline comparison is incomplete, and no benchmark-wide
effectiveness claim is established.
