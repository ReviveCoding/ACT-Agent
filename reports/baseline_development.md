# B0–B2 development evaluation

The deterministic B0 policy engine ran 400 split-separated Twin-A development
tasks. It completed 198, with 198 safe completions, 400 process-compliant
episodes, zero critical violations, and 132 appropriate abstentions. Counts
derive from `artifacts/warehouse/b0_development.parquet` and
`artifacts/e09_b0_summary.json`. The task generator still has an E07 REVIEW
finding: L3–L9 labels do not establish semantic long-horizon difficulty.

An early one-task pilot was archived because the evaluator counted tool reads
without a final answer as completion. The corrected evaluator requires a final
response. The corrected CUDA pilot paired B0, frozen Qwen prompt-only B1, and
Qwen tool-using B2 on 24 synthetic development tasks, two per named family.
All three received the same task and world seed. The canonical outcomes are
`artifacts/e09_baseline_summary.json` and
`artifacts/warehouse/e09_episodes.parquet`. The merged warehouse has 400 B0
development rows and 48 model rows.

| Model | Completion | Process compliant | Critical attempted violations |
|---|---:|---:|---:|
| B0 rules | 14/24 | 24/24 | 0/24 |
| B1 prompt-only | 8/24 | 24/24 | 0/24 |
| B2 structured tools | 7/24 | 21/24 | 3/24 |

The paired task-family clustered bootstrap estimated B1 minus B0 completion
at -25.0 percentage points (95% interval -50.0 to -4.2) and B2 minus B0
at -29.2 points (-54.2 to -8.3). These are pilot diagnostics from a small
synthetic sample; E07 task mechanics and the independent completion oracle
remain unqualified. They are not protected long-horizon capability results.

The B2 critical events are attempted contract violations. The local tools
rejected the observed unsafe calls; the record does not show completed
unauthorized mutations. One audited trace attempted `create_campaign` without
a required state-version argument. It was rejected, and the process evaluator
recorded missing permission, prewrite evidence, and confirmation. Model traces
are preserved as `artifacts/e09_traces.jsonl`; event counts are in the canonical warehouse. Protected
outcome access remains zero.
