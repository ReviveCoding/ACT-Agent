# Preference method development

All 24 tasks are synthetic development episodes on matched Twin-A worlds. E07 task mechanics/oracle is REVIEW; E11/E12 preference sources and alternate-tape stability are REVIEW. These values are not protected capability or safety estimates.

| Model | Complete | Safe complete | Process compliant | Critical flags | Difference vs SFT (95% clustered interval) |
|---|---:|---:|---:|---:|---:|
| B0 | 14/24 | —/24 | —/24 | —/24 | — |
| B3 full SFT | 8/24 | 8/24 | 24/24 | 0/24 | — |
| B4 DPO | 5/24 | 5/24 | 23/24 | 1/24 | -12.5 pp [-29.2, +0.0] |
| B5 IPO | 6/24 | 6/24 | 24/24 | 0/24 | -8.3 pp [-25.0, +0.0] |
| B6 robust DPO | 7/24 | 7/24 | 24/24 | 0/24 | -4.2 pp [-20.8, +8.3] |
| B7 unweighted control | 5/24 | 5/24 | 24/24 | 0/24 | -12.5 pp [-29.2, +0.0] |
| M0 weighted scripted pair | 6/24 | 6/24 | 24/24 | 0/24 | -8.3 pp [-25.0, +8.3] |

B4 and B7 used the same scripted pair IDs and unweighted DPO objective; both completed 5/24 tasks, so this run cannot identify ACT pair-construction value. M0 used varying pair weights and completed one more task than B7; the paired difference was +4.2 percentage points with a 95% clustered interval of 0 to +16.7 points on this tiny development set. This is not full ACT-PO because on-policy hard-negative mining is absent.

The strongest development baseline is deterministic B0 (14/24). Among the trained adapters in this set, the full 120-step SFT checkpoint completed the most tasks (8/24). No candidate is eligible for protected promotion because task-oracle and preference-source gates failed.

Canonical episode JSONL, traces, training receipts, adapter hashes, and paired-comparison JSON files are under `artifacts/`; the warehouse includes all completed development episodes.
