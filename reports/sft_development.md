# SFT development evidence

All figures use the 24 paired synthetic development tasks. E07 remains REVIEW; these are exploratory diagnostics, not protected capability estimates.

| Checkpoint | Complete | Safe complete | Process compliant | Critical process flags |
|---|---:|---:|---:|---:|
| Seed 11, step 30 | 6/24 | 4/24 | 15/24 | 8/24 |
| Seed 11, step 120 | 8/24 | 8/24 | 24/24 | 0/24 |

B0 completed 14/24; B2 completed 7/24 on the same tasks. For the 120-step adapter, the paired B3−B0 difference was −25 percentage points (family-clustered 95% interval −50 to −4.2 points). The B3−B2 difference was +4.2 points (interval −20.8 to +29.2).

The seed-11 120-step run used NF4 4-bit QLoRA, BF16, rank 16, gradient accumulation 8, and 634,207 training tokens. It took 98.7 minutes, with peak reserved CUDA memory 7.20 GiB. The intermediate step-30 snapshot came from this same seed, so it is not an independent replicate.

The step-30 adapter had eight critical process flags, including rejected unauthorized write attempts. The full 120-step adapter had zero critical flags on these 24 tasks. These counts do not establish safety non-inferiority because the sample is small and no protected evaluation was run.

Canonical evidence: `artifacts/training/sft-seed11.json`, `artifacts/e10_b3_seed11_step30_summary.json`, `artifacts/e10_b3_seed11_step120_summary.json`, and the corresponding episode/trace JSONL files.
