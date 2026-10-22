# TRACE: Evidence-Grounded Repair for Small Language Model Coding Agents 

**Subtitle:** A Four-Case Pilot Study of Repository Exploration, Candidate Repair, and Regression Validation

**Author:** Jocelyn C. Dumlao

**Affiliation:** Independent Researcher, Data Science and Machine Learning, Davao City, Philippines

## Abstract

Repository-level software repair requires an agent to localize relevant code, interpret failures, propose a change, and verify that the change does not break related behavior. This paper documents a pilot investigation associated with TRACE, a proposed framework for test-guided repository exploration and evidence-grounded repair. Four software issue cases from SQLFluff and Marshmallow were examined using target regressions, selected control tests, broader test suites, and source-restoration checks. The cases provide concrete evidence about candidate validation and the importance of recording repair provenance. Outcomes were heterogeneous: the successful SQLFluff-1733 candidate was found through subsequent rule-isolation investigation rather than a successful Gemma proposal; the SQLFluff-1625 candidate was test-guided; the Marshmallow-1343 candidate was traceback-guided; and the final Marshmallow-1359 candidate was refined after the initial proposal failed parent-relationship controls. The validated candidates passed their recorded test scopes, including full-suite runs of 780 and 912 tests for Marshmallow-1343 and Marshmallow-1359, respectively. These four cases are a preliminary pilot, not a controlled comparison of TRACE against competing agents. They do not establish benchmark-wide repair performance, causal benefits from adaptive exploration, or a general Gemma 4 success rate.

## 1. Introduction

A plausible patch is not necessarily a correct patch. Repository-level software repair requires locating relevant code, reasoning about dependencies, understanding expected behavior, and testing proposed changes. Small or locally deployed models make these tasks especially sensitive to context limits, latency, and tool-use budgets.

Prior work has explored repository interaction through purpose-built agent–computer interfaces for software engineering (Yang et al., 2024) and structured, agentless workflows for issue localization, repair, and patch validation (Xia et al., 2024). TRACE investigates a related but narrower workflow in a four-case pilot: organizing repository evidence, using diagnostic and test feedback to guide candidate repair, and explicitly checking regression behavior. This study is intended to assess workflow feasibility and document case-level outcomes, not to establish superiority over existing systems or demonstrate improved repair effectiveness or resource efficiency. Comparing adaptive evidence selection with simpler retrieval and test-guided baselines under matched budgets remains a question for future evaluation.

TRACE is intended to coordinate repository evidence, test-informed diagnosis, bounded candidate generation, and explicit verification. The long-term research question is whether adaptive evidence selection can improve verified issue resolution and resource efficiency compared with simpler retrieval and test-guided baselines under matched budgets.

The current pilot addresses a narrower question: can a disciplined validation workflow distinguish candidates that pass a target regression from candidates that also preserve related behavior, and can it retain sufficient evidence to reproduce the evaluation? The four cases below provide initial case-level observations. They are not sufficient to establish the broader hypotheses.

### Research questions

- **RQ1:** Can candidate repairs be evaluated with target tests, control tests, and broader regression suites while preserving the original source state?
- **RQ2:** How do model-proposed candidates compare with candidates that require subsequent human-guided refinement?
- **RQ3:** What reporting safeguards are needed to avoid overstating repair success from a small number of selected cases?

The broader hypotheses about adaptive retrieval, structural evidence, and resource efficiency remain untested by this pilot.

## Related Work

Research on repository-level coding agents has explored different ways to connect language models with software projects and repair workflows. SWE-agent investigates how an agent–computer interface can support automated software engineering by structuring interaction with the repository environment (Yang et al., 2024). Agentless examines a structured approach to issue localization, patch generation, and validation without requiring the same continuously acting agent-interface design (Xia et al., 2024).

TRACE addresses a related problem but has a narrower purpose in this paper. It organizes repository evidence and test feedback while recording how candidate repairs were obtained and validated. The four cases distinguish target regressions, selected control tests, broader test suites, and source-restoration checks. This emphasis on provenance matters because a passing candidate may result from model generation, diagnostic guidance, subsequent investigation, or human-guided refinement.

The present study is not a head-to-head evaluation of SWE-agent, Agentless, and TRACE. Its four heterogeneous cases do not use matched budgets or a common comparative benchmark, so they cannot establish that TRACE is more effective or efficient. Instead, the pilot documents a test-guided workflow and the evidence needed to interpret case-level repair outcomes. A controlled comparison remains future work.
## 2. Method

### 2.1 Pilot design

Four issue cases were investigated across two Python projects: SQLFluff and Marshmallow. Each case used an issue-specific baseline, a target regression test, and relevant control tests where available. Broader tests were run for the recorded cases. Candidate changes were evaluated temporarily; the original production source was restored afterward and checked using source hashes or source-control diffs.

The cases were selected as engineering pilots, not sampled randomly from a benchmark. Consequently, the observed outcomes must not be interpreted as unbiased estimates of general repair performance.

### 2.2 Candidate provenance

Repair provenance is central to interpreting the results:

1. **SQLFluff-1733:** Gemma's initial proposal did not solve the issue. A successful candidate was subsequently identified through rule-isolation investigation. It must not be counted as a successful Gemma-generated repair.
2. **SQLFluff-1625:** Gemma proposed a diagnostic-text repair with diagnostic information available in the prompt. The candidate passed the recorded target and full CLI-module tests. This is test-guided evidence, not a blind repair result.
3. **Marshmallow-1343:** Gemma proposed a change based on the failure traceback and focused source excerpts. The candidate passed the target, control, module, and full-suite validations.
4. **Marshmallow-1359:** The initial Gemma proposal changed how nested fields were bound and passed the target regression but failed parent-relationship controls. A refined candidate preserved container-parent relationships and adjusted the schema-option lookup. The refined candidate passed the target, controls, field module, and full test suite. The refined result must be distinguished from the rejected initial proposal.

These differences mean the cases cannot be treated as interchangeable trials of a single, fixed model-only procedure.

### 2.3 Verification protocol

The recorded validation workflow used the following sequence:

1. Confirm the target case and baseline failure.
2. Identify relevant control tests.
3. Generate or investigate a candidate patch without treating model output as trusted execution instructions.
4. Check the candidate against the target regression and relevant controls.
5. Run a broader test scope when practical.
6. Restore the original source and verify source integrity.
7. Preserve patch artifacts, logs, hashes, and case-level reports.

Passing tests indicates success under the recorded test protocol. It does not prove correctness for every input, full semantic equivalence, or absence of untested regressions.

### 2.4 TRACE implementation status

The broader TRACE concept proposes lexical and structural evidence retrieval, test-guided diagnosis, adaptive exploration, bounded patch generation, and verification feedback. These pilot results do not establish that every part of this complete loop was implemented or experimentally evaluated.

In particular, this study does not provide a matched-budget comparison among a basic agent, BM25-only retrieval, graph-guided retrieval, test-guided investigation, and full TRACE. Nor does it report controlled ablations of structural evidence, adaptive selection, or verification feedback.

### 2.5 Metrics and reporting

For each case, the study records target-test outcome, control-test outcome where available, broader test scope, candidate provenance, and source-restoration evidence. Test counts from different repositories are not combined into a single success metric. Resource usage, repeated-run variability, confidence intervals, and matched-budget comparisons are not reported here because a standardized multi-condition experiment has not been completed.

## 3. Results

### 3.1 Case-level validation

| Case | Candidate provenance | Recorded validation | Interpretation |
|---|---|---|---|
| SQLFluff-1733 | Successful candidate found through subsequent rule-isolation investigation; initial Gemma proposal unsuccessful | Target 1/1; controls 3/3; `test/rules` suite: 510 passed | Successful investigated candidate, not a Gemma-attributed repair |
| SQLFluff-1625 | Gemma candidate using diagnostic guidance | Target passed; full CLI module: 69 passed | Test-guided candidate passed its recorded scope |
| Marshmallow-1343 | Gemma candidate guided by traceback | Target 1/1; control 1/1; marshalling module: 25 passed; full suite: 780 passed | Traceback-guided candidate passed the recorded suite |
| Marshmallow-1359 | Initial Gemma proposal rejected after control failures; refined candidate validated | Target 1/1; controls 5/5; field module: 77 passed; full suite: 912 passed | Refined candidate passed the recorded suite |

### 3.2 Source integrity

The recorded validation artifacts report that temporary candidate changes were removed after testing. For Marshmallow-1343, the original source hash before and after validation matched, with no remaining production-source diff. For Marshmallow-1359, the final full-suite report records the same source hash before and after, an empty production diff, and `candidate_left_applied=false`.

The SQLFluff case records likewise document source restoration. These safeguards improve the auditability of the experiments but do not independently establish that the candidate patch is the only correct repair.

### 3.3 Interpretation

The pilot demonstrates the value of separating target-test success from broader regression evidence. Marshmallow-1359 is especially informative: a candidate that passed the target test was rejected because it broke parent-relationship controls, while a refined candidate subsequently passed the broader recorded suite.

The cases also demonstrate why candidate provenance must be reported explicitly. A successful candidate found after human-guided investigation is not equivalent to a successful initial model proposal. Likewise, a candidate produced with diagnostic information in the prompt should not be described as a blind repair.

No overall Gemma 4 success rate is calculated. The four cases were not a standardized, independent, representative sample, and their candidate-generation procedures differed.

## 4. Discussion

This four-case pilot illustrates how repository-level repair should be evaluated as a sequence of evidence-producing steps rather than by target-test success alone. The Marshmallow-1359 case provides a concrete example: the initial proposal failed parent-relationship controls, so it was not accepted; a refined candidate passed the recorded target, control, and broader test checks. This supports the practical value of regression-aware validation within the tested scope, but it does not establish that the workflow will produce the same outcome on other tasks.

The cases also show that the provenance of a candidate is essential to interpreting results. The SQLFluff-1733 candidate emerged from subsequent rule-isolation investigation and must not be attributed to a successful initial Gemma proposal. Other candidates used diagnostic guidance or traceback information, and the Marshmallow-1359 candidate required refinement after control failures. These distinctions matter when evaluating a coding agent: model-generated suggestions, human-guided refinement, and independently discovered repairs represent different forms of evidence and should be recorded separately.

Source restoration and recorded hashes add an auditability safeguard by helping establish that temporary candidate changes were not left in the production source after validation. However, source integrity is distinct from repair correctness. A clean working tree or matching source hash does not prove that a proposed repair is uniquely correct, complete, or free of defects outside the tests that were run.

Taken together, these observations motivate TRACE as a structured process for recording candidate provenance, target-test outcomes, regression controls, and source-restoration evidence. The present results are feasibility evidence for that reporting and validation approach, not a comparative effectiveness result. Because this pilot lacks a controlled baseline, standardized candidate-generation budgets, repeated trials, and resource measurements, it cannot isolate the causal contribution of TRACE or establish superiority over other repair methods.

A next evaluation should use a preregistered or otherwise fixed task set, define candidate-provenance and success-counting rules in advance, and compare TRACE with relevant baselines under matched budgets. It should report initial and refined candidates separately, retain failures as well as successes, and measure runtime, model and tool calls, token use, and cost where available. Larger samples and repeated runs would also help characterize variability and generalization. These are requirements for a future evaluation, not findings of the current pilot.

## 5. Limitations and threats to validity

**Small, selected sample.** Four cases cannot establish benchmark-wide effectiveness or generalization to other repositories, languages, issue types, or model configurations.

**Unequal candidate provenance.** Some outcomes came from model proposals, while others required subsequent investigation or refinement. A pooled success rate would obscure these differences.

**Prompt information.** Diagnostic information was available in some model-guided cases. Results cannot be interpreted as unprompted issue discovery.

**Test coverage.** Passing tests establishes conformance only to the tested cases and environment. Hidden defects and semantic regressions may remain.

**No controlled baseline comparison.** This pilot does not provide matched-budget comparisons with lexical, graph-guided, test-guided, or other software-repair agents. The effect of TRACE itself is therefore unknown.

**No standardized resource evaluation.** The results do not establish improvements in tokens, latency, model calls, tool calls, or cost. Repeated-run variance and confidence intervals are also unavailable.

**Environment and reproducibility.** Test results depend on repository commits, Python environments, dependencies, and test configurations. Those details and their artifacts should be retained when results are reproduced.

**Model attribution.** The SQLFluff-1733 candidate is not a Gemma success, and the final Marshmallow-1359 candidate is a refinement after the initial proposal failed controls. Any future quantitative evaluation must predefine how such cases are counted.

## 6. Conclusion

This four-case pilot provides preliminary, case-specific evidence that a structured validation workflow can distinguish target-test success from broader regression safety and that source restoration and explicit provenance improve auditability. It also shows why a model's initial proposal, a refined proposal, and a repair found through subsequent investigation must be reported separately.

The study does not yet demonstrate that TRACE improves repair success or resource efficiency over alternative methods. Establishing that claim requires a larger, reproducible benchmark evaluation with fixed task selection, matched budgets, predefined outcome rules, relevant baselines, ablations, and transparent reporting of failures as well as successes.

## References

1. Yang, J., Jimenez, C. E., Wettig, A., Lieret, K., Yao, S., Narasimhan, K., & Press, O. (2024). *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering*. Advances in Neural Information Processing Systems 37 (NeurIPS 2024). https://doi.org/10.52202/079017-1601

2. Xia, C. S., Deng, Y., Dunn, S., & Zhang, L. (2024). *Agentless: Demystifying LLM-based Software Engineering Agents*. arXiv preprint arXiv:2407.01489. https://doi.org/10.48550/arXiv.2407.01489
