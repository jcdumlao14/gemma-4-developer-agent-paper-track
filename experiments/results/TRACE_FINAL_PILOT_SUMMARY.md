# TRACE — Final Pilot Summary

## Scope
Four selected software issue cases across SQLFluff and Marshmallow.

## Outcomes
- SQLFluff-1733: successful candidate from subsequent rule-isolation investigation; not a successful Gemma proposal. Target 1/1, controls 3/3, `test/rules` 510 passed.
- SQLFluff-1625: Gemma candidate with diagnostic guidance; target passed and full CLI module 69 passed.
- Marshmallow-1343: traceback-guided Gemma candidate; target/control passed, marshalling module 25 passed, full suite 780 passed.
- Marshmallow-1359: initial proposal rejected after parent-relationship control failures; refined traceback-guided candidate passed target, 5 controls, 77 field tests, and 912 full-suite tests.

## Integrity
Case reports document temporary candidate validation and source restoration. The Marshmallow-1359 full-suite report records matching source hashes before and after validation, no production diff, and no candidate left applied.

## Conclusions
The pilot supports careful case-level validation and provenance tracking. It does not establish a benchmark-wide repair rate or prove that TRACE outperforms matched-budget baselines. The current evidence is preliminary and should be reported as a four-case pilot study.
