# Experiment protocol (draft)

## Before running
1. Select a benchmark permitted by the competition rules and record its exact version.
2. Define inclusion/exclusion rules before examining final results.
3. Pin repository commits and preserve issue IDs.
4. Fix the base model, sampling settings, tool permissions, time/token budgets, and test protocol.
5. Separate development issues from held-out evaluation issues.

## Required record per issue/run
- benchmark and task ID
- repository URL and base commit
- method/baseline and config hash
- model identifier and inference settings
- start/end time and termination reason
- input/output tokens and model/tool calls, when available
- patch generated and patch-application result
- test commands, exit codes, and summarized output
- verified pass/fail status
- error classification
- random seed and run index

## Reporting
Report counts and denominators, not percentages alone. Include failures and exclusions with reasons. Use paired comparisons for methods evaluated on the same issues. Select statistical tests appropriate to the outcome and sample size. Avoid claims of generalization beyond the tested population.

## Data and licensing
Review benchmark terms, model terms, repository licenses, and personal/security information before publishing traces or derived artifacts. Never publish secrets, hidden tests, private source code, or restricted evaluation material.
