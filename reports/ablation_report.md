# Ablation report

E24 is a partial synthetic development diagnostic. E07 task mechanics and E11/E12 preference sources remain under REVIEW; protected outcomes were not accessed.

## Executed diagnostics

- A7 weighting control: B7 5/24 versus weighted M0 6/24; paired difference +4.2 percentage points, 95% family-clustered interval [+0.0, +16.7]. Both had zero critical flags. This does not isolate full ACT-PO because hard-negative mining is absent.
- A8 method objective: DPO 5/24, IPO 6/24, Robust-DPO 7/24 on the same scripted-pair source. These exploratory counts do not support promotion.

## Unrun ablations

- A1_A2_A4_A6: ACT pair-construction mechanism not qualified.
- A3: lexicographic-vs-scalar pair construction not implemented on qualified candidates.
- A5: on-policy hard negatives absent.
- A9: protected R-TRACE factorial closed without E17 freeze.
- A10_A11: task oracle under REVIEW, so policy/confirmation removal would not support capability mechanism claim.
- A12: uncalibrated twin comparator not constructed.
- A13: Twin-B protected and no valid finalist/freeze.
- A14: SFT initialization ablation not run; no valid finalist.

Canonical evidence: `artifacts/e24_ablation_diagnostics.json`, `artifacts/e15_m0_vs_b7_seed11_paired_comparison.json`, and E13/E14/E15 receipts. Unrun ablations are null, not zero.
