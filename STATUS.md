# ACT-Agent v1.0 status

Recovered 2026-09-20 after reboot; immutable E00/E02 and surviving source/model/training hashes verified.

Protected internal and external outcome access counts remain zero.

| Stage | State | Reason |
|---|---|---|
| E00 | PASS | Escalated nvidia-smi and PyTorch CUDA 13.0 BF16 real matmul qualified |
| E01 | PASS | Authoritative sources pinned; Criteo attribution/uplift and Qwen hashes/licenses verified; benchmark outcomes untouched |
| E02 | PASS | official Criteo-owned mirror checksum matches published SHA-256 |
| E03 | PASS | Public aggregates, quality statistics, exact hashes, raw-data exclusion, and split namespace audit passed |
| E04 | PASS | Standards mapped to actual design scope with explicit nonconformance boundary |
| E05 | PASS | Twin-A passed 11 pre-protected distribution, temporal, heterogeneity, fault, intervention, transaction, and determinism checks |
| E06 | PASS | Twin-B source, calibration, parameters, and seed namespace resealed before protected access; no transfer outcomes accessed |
| E07 | REVIEW | Expected deterministic user behavior passes; independent family completion oracle and L3-L9 task mechanics remain unqualified |
| E08 | PASS | Known-answer contract matrix covers prewrite evidence, confirmation, permissions, scope, forbidden actions, mutation cap, and rollback |
| E09 | REVIEW | 24 paired B0/B1/B2 CUDA development tasks completed; small pilot and E07 task-oracle REVIEW preclude primary capability claim |
| E10 | PASS | Seed-11 120-step NF4/BF16 QLoRA SFT completed on RTX 4090; 24 paired development tasks: 8 complete, 8 safe, 24 process compliant, zero critical flags; step-30 snapshot 6 complete with 8 critical flags. E07 task-oracle REVIEW prevents primary capability inference. |
| E11 | REVIEW | 6,000 split-safe SFT traces and 10,000 scripted labels exist; 1,805 consistency-filtered trainable pairs, but ReAct/SFT/on-policy sources absent |
| E12 | REVIEW | Pair identity, mask, weight, task and market audits pass; alternate-tape and model-source preference audits not run |
| E13 | REVIEW | CUDA 3-step scripted-pair pilots and 24 paired development rollouts completed: DPO 5/24 with 1 critical flag, IPO 6/24 with 0, robust-DPO 7/24 with 0; E07 and E11/E12 REVIEW preclude confirmatory inference. |
| E14 | REVIEW | Unweighted ACT-pair CUDA control completed 5/24 paired development tasks with 0 critical flags; it used the same scripted pair IDs and DPO objective as B4 (also 5/24), so ACT pair construction is not isolated. |
| E15 | REVIEW | Weighted ACT-style CUDA pilot on scripted pairs completed 6/24 tasks, versus unweighted B7 5/24 and SFT 8/24, with 0 critical flags in all three; full ACT-PO on-policy hard negatives and qualified task oracle absent. |
| E16 | REVIEW | Three matched 30-step SFT seeds and three-seed 3-step DPO/weighted scripted-pair CUDA training receipts verified; seeds 23/37 lack paired task outcomes, and full ACT-PO mechanism/qualified finalist absent. |
| E17 | REVIEW | Power exploratory; no valid freeze due E07/E11/E12/E14/E15 gates; protected access zero |
| E18 | CLOSED | No valid E17 freeze; protected outcomes untouched |
| E19 | CLOSED | No valid E17 freeze; protected outcomes untouched |
| E20 | CLOSED | No valid E17 freeze; protected outcomes untouched |
| E21 | CLOSED | No valid E17 freeze; protected outcomes untouched |
| E22 | CLOSED | No valid E17 freeze; protected outcomes untouched |
| E23 | REVIEW | All 16 planned CUDA noise-training pilots and 12 x 24 paired synthetic development rollouts completed with exact flip, adapter, task, and log hashes; E07 task oracle and full ACT-PO source remain unqualified, so inference is exploratory only. |
| E24 | REVIEW | A7 weighting and A8 objective diagnostics executed on 24 synthetic development tasks; primary A3/A5 and other mechanism ablations unrun because ACT pairs/on-policy sources and task oracle are unqualified. |
| E25 | BLOCKED_EXTERNAL | BFCL V4 upstream acquisition blocked by workspace-write DNS/network restriction; no benchmark examples or outcomes accessed |
| E26 | BLOCKED_EXTERNAL | tau3 upstream acquisition blocked by workspace-write DNS/network restriction; no benchmark examples or outcomes accessed |
| E27 | BLOCKED_EXTERNAL | AgentDojo upstream acquisition blocked by workspace-write DNS/network restriction; no benchmark examples or outcomes accessed |
| E28 | REVIEW | RTX 4090 CUDA training, rollout, and base/SFT NF4 serving lifecycle measured; outputs differ in generated length, and compile cold-cost/break-even plus frozen finalist serving comparison remain unmeasured. |
| E29 | PASS | Final audited release and claim verification passed |
