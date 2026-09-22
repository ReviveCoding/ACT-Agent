# Multi-seed development audit

Three independent SFT seeds were trained to a matched 30-step NF4/BF16 QLoRA budget. Each then initialized three-step DPO and weighted scripted-pair runs on 64 deterministic seed-selected preferences. All jobs executed on the single RTX 4090 with real CUDA preflights and sealed adapter/reference hashes.

| Seed | SFT step-30 loss | DPO final loss | Weighted final loss |
|---:|---:|---:|---:|
| 11 | 0.0238 | 0.0647 | 0.0567 |
| 23 | 0.0391 | 0.0015 | 0.0010 |
| 37 | 0.0238 | 0.2942 | 0.2543 |

The SFT step-30 loss mean was 0.0289 with sample standard deviation 0.0088. This is training-loss variation, not a task-performance uncertainty interval. Only seed 11 has the complete 24-task adapter development rollout; seeds 23 and 37 have no matched evaluation-world outcomes.

Pair sampling varies by seed. The weighted runs use scripted preferences without on-policy hard-negative mining. E16 is REVIEW and does not qualify a finalist. Full identities, hashes, loss vectors, and CUDA VRAM figures are in `artifacts/e16_training_seed_audit.json`.
