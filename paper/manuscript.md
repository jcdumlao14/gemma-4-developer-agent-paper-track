# TRACE: Test-Guided Repository Exploration and Evidence-Grounded Repair for Small Language Model Coding Agents

**Subtitle:** An Empirical Study of Adaptive Code Localization, Verification, and Resource-Efficient Software Issue Resolution

**Author:** Jocelyn C. Dumlao

**Affiliation:** Independent Researcher, Data Science and Machine Learning, Philippines

## Abstract

Repository-level software engineering agents must identify relevant code, diagnose defects, implement changes, and verify repairs across codebases whose structure and behavior may be only partially understood. Inefficient exploration can consume context and tool budgets without improving repair quality. This project investigates TRACE, a proposed framework that coordinates repository evidence, test-informed diagnosis, and bounded patch verification.

The central research question is whether adaptive evidence selection improves verified issue resolution and resource efficiency compared with lexical retrieval, graph-guided retrieval, and test-guided baselines under matched budgets. The evaluation will measure validation-test success, localization quality, model and tool usage, runtime, and failure modes. Ablation experiments will examine the contributions of structural evidence, adaptive selection, and verification feedback. This manuscript is a research plan and prototype description until controlled benchmark experiments are completed; no empirical improvement is claimed at this stage.

## 1. Introduction

A plausible patch is not necessarily a correct patch. Repository-level repair requires locating relevant code, reasoning about dependencies, understanding expected behavior, and testing proposed changes. Small or locally deployed models make these tasks especially sensitive to context limits, latency, and tool-use budgets.

TRACE proposes an explicit evidence-selection loop: gather issue-specific evidence, identify likely code regions, inspect relevant tests, attempt a bounded repair, and use observed verification outcomes to decide whether further investigation is warranted. The intended contribution is not the mere combination of retrieval and testing, but a measured policy for allocating exploration effort.

### Research hypotheses

- H1: TRACE improves verified issue resolution over a basic agent and lexical-retrieval baseline under matched budgets.
- H2: structural repository evidence improves localization beyond lexical retrieval alone.
- H3: verification feedback and adaptive exploration improve the trade-off between repair success and resource cost.

These are hypotheses, not findings.

## 2. Method

### 2.1 Prototype

The initial code implements a deterministic lexical repository inspection baseline with lightweight Python AST extraction for imports and function/class symbols. It ranks candidate files using transparent path and content overlap. This prototype makes the baseline inspectable and testable; it is not yet the complete adaptive TRACE agent and does not itself repair issues.

### 2.2 Planned TRACE loop

1. Parse the issue description and gather initial candidate files.
2. Rank candidate code regions using lexical and structural evidence.
3. Inspect relevant tests and available failure traces.
4. Choose the next permitted exploration action based on evidence and remaining budget.
5. Produce a patch only when the configured repair-readiness condition is met.
6. Run the designated tests, record outcomes, and revise or stop within a fixed attempt budget.

The final paper must define the actual scoring function, stop rule, tools, and implementation used in experiments.

### 2.3 Baselines and controls

Compare a basic agent, lexical retrieval, graph-guided retrieval, test-guided investigation, and full TRACE. Keep the base model, issue set, tool permissions, environment, and budget matched wherever possible. Document any differences.

### 2.4 Metrics

Primary metric: fraction of eligible issues whose patch passes the designated validation tests. Report numerator and denominator.

Secondary metrics: localization quality, model calls, token usage, tool calls, wall-clock time, test executions, patch application failures, regressions, timeouts, and repeated-run variability. Report uncertainty estimates and paired comparisons where appropriate.

### 2.5 Ablations

Remove structural evidence, adaptive selection, and verification feedback one at a time. Preserve unsuccessful runs and record whether the component changes success, cost, or failure patterns.

## 3. Results

**Pending experiments.** Populate this section only after the benchmark is run. Include benchmark/version, task identifiers, repository commits, model and runtime configuration, hardware, budget, number of runs, verified-fix counts, confidence intervals, resource usage, and failure analysis. Local unit tests are software checks and must not be presented as benchmark issue-resolution results.

## 4. Limitations and threats to validity

Benchmark issues may not represent all real-world maintenance tasks. Passing tests does not prove the absence of regressions or establish semantic correctness beyond the validation protocol. Results may vary with model sampling, repository language, test quality, environment reliability, and tool configuration. Generalization must be tested on held-out repositories or issue families.

## 5. Conclusion

TRACE is a proposed research framework for adaptive repository exploration and evidence-grounded repair. Whether it improves software issue resolution or efficiency remains an empirical question. The final contribution will depend on controlled comparisons, ablation studies, transparent reporting, and reproducible artifacts.

## References to verify

- Yang, J. et al. (2024). *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering*. NeurIPS 2024. https://arxiv.org/abs/2405.15793
- Xia, C. S. et al. (2024). *Agentless: Demystifying LLM-based Software Engineering Agents*. https://arxiv.org/abs/2407.01489
- Add and verify directly relevant repository-exploration, code-graph, and Gemma 4 competition references before submission.

**Literature review note:** verify bibliographic details, publication status, and novelty against primary sources before asserting a research gap.
