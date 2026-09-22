# Preference-noise development study

Sixteen CUDA training pilots used the same 64 scripted pairs with exact predeclared label flips. Twelve noisy adapters were evaluated on the same 24 synthetic development tasks as their 0% counterparts.

Zero-flip completion reference: dpo 5/24, ipo 6/24, robust_dpo 7/24, ACT weighted pilot 6/24.

| Method | Flip rate | Complete | Safe complete | Process compliant | Critical flags | Difference vs 0% (95% clustered interval) |
|---|---:|---:|---:|---:|---:|---:|
| dpo | 5% | 5/24 | 5/24 | 23/24 | 1/24 | +0.0 pp [+0.0, +0.0] |
| ipo | 5% | 6/24 | 6/24 | 24/24 | 0/24 | +0.0 pp [+0.0, +0.0] |
| robust_dpo | 5% | 6/24 | 6/24 | 23/24 | 1/24 | -4.2 pp [-16.7, +0.0] |
| ACT weighted pilot | 5% | 6/24 | 6/24 | 24/24 | 0/24 | +0.0 pp [-12.5, +16.7] |
| dpo | 10% | 6/24 | 6/24 | 24/24 | 0/24 | +4.2 pp [+0.0, +16.7] |
| ipo | 10% | 6/24 | 6/24 | 24/24 | 0/24 | +0.0 pp [+0.0, +0.0] |
| robust_dpo | 10% | 6/24 | 6/24 | 24/24 | 0/24 | -4.2 pp [-16.7, +0.0] |
| ACT weighted pilot | 10% | 5/24 | 5/24 | 24/24 | 0/24 | -4.2 pp [-16.7, +0.0] |
| dpo | 20% | 6/24 | 6/24 | 24/24 | 0/24 | +4.2 pp [+0.0, +16.7] |
| ipo | 20% | 6/24 | 6/24 | 24/24 | 0/24 | +0.0 pp [+0.0, +0.0] |
| robust_dpo | 20% | 6/24 | 6/24 | 24/24 | 0/24 | -4.2 pp [-16.7, +0.0] |
| ACT weighted pilot | 20% | 5/24 | 5/24 | 24/24 | 0/24 | -4.2 pp [-16.7, +0.0] |

These are exploratory synthetic diagnostics. The task oracle and ACT-PO hard-negative source are unqualified; small differences and zero observed critical flags in some runs do not establish method robustness or safety non-inferiority.

Canonical inputs, exact flips, training receipts, adapter hashes, episode logs, and paired results are in `artifacts/`. No protected outcomes were accessed.
