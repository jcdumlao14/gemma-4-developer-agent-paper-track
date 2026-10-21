# TRACE: Gemma 4 Developer Agent — Pilot Results

**Report type:** Consolidated pilot evaluation\
**Scope:** Four selected bug-repair cases\
**Purpose:** Summarize regression validation, candidate outcomes, and research limitations.

## 1. Executive summary

Four pilot cases have been investigated across SQLFluff and Marshmallow. The experiments show that candidate repairs can be evaluated using target regressions, selected control tests, broader test suites, and source-restoration checks.

The cases do not constitute a representative benchmark-wide evaluation. Results must be interpreted according to how each candidate was generated and what information was available to the model.

## 2. Case-level results

| Case | Candidate provenance | Validation evidence | Interpretation |
|---|---|---|---|
| SQLFluff-1733 | Successful candidate obtained through subsequent rule-isolation investigation; not Gemma's successful repair | Target 1/1; controls 3/3; `test/rules` 510 passed; original source restored and hash verified | Successful investigated repair; not a Gemma-attributed success |
| SQLFluff-1625 | Gemma candidate, guided by diagnostic information and expected diagnostic strings | Target passed; full CLI module 69 passed; source restored | Test-guided repair; not a blind or fully unprompted result |
| Marshmallow-1343 | Gemma candidate guided by traceback evidence | Target 1/1; control 1/1; full marshalling module 25 passed; full suite 780 passed; original source restored | Traceback-guided candidate validated on the recorded test scope |
| Marshmallow-1359 | Initial Gemma proposal rejected after two parent-relationship control failures; refined candidate then validated | Target 1/1; controls 5/5; `tests/test_fields.py` 77 passed; full suite 912 passed; original source hash restored | Refined traceback-guided repair validated; do not count the rejected initial proposal as a success |

## 3. Marshmallow-1359 final evidence

The refined candidate adjusts how `DateTime` retrieves schema options when it is bound through a `List` or `Tuple`. It preserves the container as the inner field's parent while looking up options through the container's parent when necessary.

Final full-suite result:

- 912 tests passed.
- Exit code: 0.
- Original source SHA-256 before and after: `5529e7074bebc094e09fcbc8efaf88397f8026d1f21605bf62fc9d99b8ae601f`.
- `source_restored`: true.
- `production_diff_paths`: empty.
- `candidate_left_applied`: false.

Full-suite log: `marshmallow_1359_final_full_suite.log`\
Full-suite record: `marshmallow_1359_final_full_suite.json`\
Candidate-level record: `marshmallow_1359_candidate3_validation.json`

## 4. Methodological safeguards

1. Evaluate the target regression and relevant controls, not only the target test.
2. Run a broader test suite where practical.
3. Record whether the repair came from the model, human investigation, or a refined combination.
4. Preserve failed candidate outcomes rather than silently replacing them with successful revisions.
5. Restore original production files and verify their hashes after temporary validation.
6. Keep prompts, candidate patches, test logs, model configuration, and validation records available for audit.
7. Report the tested scope and avoid implying that a passing repository test suite establishes correctness for every input or environment.

## 5. Limitations

- Four pilot cases are insufficient to establish benchmark-wide repair performance.
- Candidate provenance and prompt information differ across cases.
- The successful SQLFluff-1733 candidate was found through subsequent investigation, not a successful Gemma proposal.
- SQLFluff-1625 included diagnostic guidance in its prompt.
- The successful Marshmallow-1359 candidate was refined after the initial proposal failed controls.
- Passing tests do not independently prove that a repair is minimal, semantically complete, or free of untested regressions.
- Aggregate test counts across different repositories are not a meaningful single performance metric.

## 6. Recommended next steps

1. Verify all referenced evidence files exist and preserve their hashes.
2. Record exact model, prompt, candidate, and evaluation provenance from the experiment artifacts.
3. Add a reproducible methodology and a transparent case-selection explanation.
4. Draft the paper's Methods, Results, Limitations, and Threats to Validity sections.
5. Avoid adding more cases until the current four have a complete evidence trail.

## 7. Research conclusion

These pilots provide preliminary, case-specific evidence that a structured repair-validation workflow can distinguish successful candidates from proposals that pass a target test but regress related behavior. The findings support further systematic evaluation; they do not yet support a general claim about Gemma 4's overall software-repair success rate.
