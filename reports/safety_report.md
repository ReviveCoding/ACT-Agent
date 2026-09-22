# Safety report

The corrected 24-task paired synthetic development pilot recorded critical **attempted** process violations in 0/24 B0, 0/24 B1, and 3/24 B2 episodes. The B2 95% Wilson interval is approximately 4.3%–31.0%; the zero-event upper Wilson bound for B0/B1 is approximately 13.8%. These intervals are wide, and E07 task qualification remains REVIEW. Source counts and intervals are in `artifacts/e09_baseline_summary.json`; trace evidence is in `artifacts/e09_traces.jsonl`.

All three B2 unsafe calls identified in the failure gallery were rejected by the local tools. A rejected attempt is still a process failure, but it is not evidence of an actual unauthorized campaign mutation. No protected ACT-PO versus SFT critical-safety noninferiority test has been run. The planning 1 percentage point margin has not been frozen or justified by this small pilot. E21 R-TRACE factorial evidence is pending a valid frozen finalist set.

## Post-training development safety diagnostics

All values below are attempted critical process-violation flags on 24 synthetic development tasks, not a protected safety non-inferiority test. The local tool surface rejected unauthorized writes in the inspected traces.

| Adapter | Critical flags | Process compliant | Safe completion |
|---|---:|---:|---:|
| SFT step 30 | 8/24 | 15/24 | 4/24 |
| SFT step 120 | 0/24 | 24/24 | 8/24 |
| DPO | 1/24 | 23/24 | 5/24 |
| IPO | 0/24 | 24/24 | 6/24 |
| Robust DPO | 0/24 | 24/24 | 7/24 |
| Unweighted ACT-pair control | 0/24 | 24/24 | 5/24 |
| Weighted scripted-pair diagnostic | 0/24 | 24/24 | 6/24 |

The Wilson upper bound for zero events in 24 tasks remains material; zero observed flags does not establish safety non-inferiority or production safety. Canonical counts and intervals are in the E10/E13/E14/E15 adapter summaries.
