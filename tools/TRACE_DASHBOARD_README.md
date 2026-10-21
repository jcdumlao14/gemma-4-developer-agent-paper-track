# TRACE Dashboard - Methodology and User Guide

## 1. Purpose

The TRACE Evidence Command Center is a local dashboard for exploring
available research reports and implementation evidence associated with
the TRACE four-case pilot study.

It helps users locate evidence, inspect report summaries, and distinguish
proposal artifacts from validation records. It is an evidence-navigation
tool, not an independent benchmark runner.

## 2. Launching the dashboard

From the repository root, activate the project's virtual environment if
needed, then run:

```powershell
python tools/trace_dashboard.py
```

Open the local address in a browser:

http://127.0.0.1:8765

Keep the terminal running while using the dashboard. Use the dashboard's
Refresh control to request updated report inventory data. Use Ctrl+F5 in
the browser if you need to reload the page assets.

To stop the local server, return to its terminal and press Ctrl+C.

## 3. Summary cards

The dashboard displays four summary cards:

- **Unique pilot issues** ? the number of distinct issue identifiers
  recognized in the discovered report inventory.
- **Evidence JSON files** ? the number of report files included in the
  current inventory.
- **Proposal artifacts** ? the number of inventory records classified as
  proposal or smoke-related artifacts by the dashboard's current rules.
- **Baseline comparison** ? a manually recorded research-status indicator.
  It is not a calculated model score or proof of benchmark completion.

These counts describe discovered local files and their metadata. They
must not be interpreted as performance scores or proof that every report
has been independently reproduced.

## 4. Finding evidence

Use the search field to search available report paths, names, previews,
and recognized case identifiers. Use the evidence-type selector to narrow
the list to pilot/validation, model proposal/smoke, or audit/finalization
records. Refresh the inventory after adding or updating report files.

A displayed preview is a convenience for locating relevant evidence.
Consult the underlying report for the complete record and its context.

## 5. Classification and interpretation

The dashboard uses report metadata, filenames, and selected report fields
to classify records. Classification is intended to help navigate the
inventory; it is not a substitute for manually reviewing the evidence.

Keep these distinctions explicit:

- A **model proposal** is not an applied patch.
- An **applied patch** is not necessarily a correct repair.
- A **recorded test pass** is not necessarily an independently reproduced
  benchmark result.
- A **local software test** checks the implementation's behavior; it does
  not establish research-wide effectiveness.
- Missing evidence must remain missing rather than being inferred.

## 6. Research scope and limitations

TRACE is a four-case pilot study. The controlled baseline comparison is
not complete. Do not use this dashboard alone to claim benchmark-wide
effectiveness, model superiority, generalization, causality, or efficiency.

Historical case outcomes must retain their documented provenance. In
particular, do not describe all four cases as autonomous Gemma-generated
repairs. A candidate may have been guided by diagnostic information,
refined through investigation, or rejected before a later candidate was
validated.

The dashboard's inventory is not a replacement for the manuscript,
case-level reports, source audits, test logs, or the finalization report.

## 7. Safety and reproducibility

- Keep the dashboard local unless an explicitly reviewed deployment plan
  establishes appropriate access controls.
- Treat report files as evidence; do not silently rewrite their contents
  to make dashboard labels or counts look better.
- Do not run tests or apply patches in historical target repositories
  merely by browsing the dashboard.
- Preserve candidate patches, source hashes, validation reports, and
  backup files.
- Review `git status --short` before staging or committing. Do not
  indiscriminately add every untracked file.
- Re-run the relevant project quality checks after changes to dashboard
  code.

## 8. Project quality checks

From the repository root:

```powershell
python -m py_compile tools/trace_dashboard.py
python -m ruff check src/trace_research tests
python -m pytest -q tests
git diff --check
```

These checks verify syntax, lint, project tests, and patch whitespace.
They do not independently reproduce the historical benchmark results.

## 9. Related artifacts

Start with:

- `paper/manuscript.md` ? research manuscript.
- `experiments/results/` ? available case reports, audits, and proposal
  artifacts.
- `src/trace_research/` ? TRACE implementation.
- `tests/` ? software tests for the implementation.
- `tools/trace_dashboard.py` ? local dashboard implementation.

Read the current files and report contents before making claims about
specific experimental results.
