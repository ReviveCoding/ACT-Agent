# ACT-Agent v1.0 technical report

# Executive summary

Scientific verdict: **HOLD**. Public anchor: 16,468,027 public Criteo impression rows and 675 campaigns. B0 development completion 198/400; critical violations 0/400. Paired B0/B1/B2 development tasks: 24; B0 14/24 completed, B1 8/24 completed, B2 7/24 completed. 1805 scripted trainable pairs; audit REVIEW. Development adapter results: e10_b3_seed11_step120_summary 8/24 completed, 0 critical process flags; e10_b3_seed11_step30_summary 6/24 completed, 8 critical process flags; e13_b4_seed11_scripted_summary 5/24 completed, 1 critical process flags; e13_b5_seed11_scripted_summary 6/24 completed, 0 critical process flags; e13_b6_seed11_scripted_summary 7/24 completed, 0 critical process flags; e14_b7_seed11_scripted_summary 5/24 completed, 0 critical process flags; e15_m0_seed11_scripted_summary 6/24 completed, 0 critical process flags. No qualified protected capability or safety estimate exists. Mutable action effects remain synthetic; no production advertiser claim is made.

## Problem and Motivation

Tool-using agents need outcome, process, safety, and systems evaluation.

## Related Work

See `studies/desktop_study.md` for pinned primary sources.

## Public Data and Claim Boundaries

16,468,027 public Criteo impression rows and 675 campaigns. Raw public rows remain in WSL scratch.

## Industry Standards

See `studies/standards_mapping.md`; no formal interoperability conformance is claimed.

## Digital Twin

Twin-A qualification and Twin-B seal are in canonical receipts. Intervention effects remain synthetic.

## Agent Environment

Local versioned tool transactions, deterministic user responses, and split namespaces.

## Process Contracts

Known-answer DSL matrix passed; process and outcome are distinct metrics.

## Tasks

Expected deterministic user behavior passes; independent family completion oracle and L3-L9 task mechanics remain unqualified

## Baseline Models

B0 development completion 198/400; critical violations 0/400. Paired B0/B1/B2 development tasks: 24; B0 14/24 completed, B1 8/24 completed, B2 7/24 completed. Development adapter results: e10_b3_seed11_step120_summary 8/24 completed, 0 critical process flags; e10_b3_seed11_step30_summary 6/24 completed, 8 critical process flags; e13_b4_seed11_scripted_summary 5/24 completed, 1 critical process flags; e13_b5_seed11_scripted_summary 6/24 completed, 0 critical process flags; e13_b6_seed11_scripted_summary 7/24 completed, 0 critical process flags; e14_b7_seed11_scripted_summary 5/24 completed, 0 critical process flags; e15_m0_seed11_scripted_summary 6/24 completed, 0 critical process flags.

## SFT

Seed-11 120-step NF4/BF16 QLoRA SFT completed on RTX 4090; 24 paired development tasks: 8 complete, 8 safe, 24 process compliant, zero critical flags; step-30 snapshot 6 complete with 8 critical flags. E07 task-oracle REVIEW prevents primary capability inference.

## Preference Construction

1805 scripted trainable pairs; audit REVIEW. 6,000 split-safe SFT traces and 10,000 scripted labels exist; 1,805 consistency-filtered trainable pairs, but ReAct/SFT/on-policy sources absent

## ACT-PO

Weighted ACT-style CUDA pilot on scripted pairs completed 6/24 tasks, versus unweighted B7 5/24 and SFT 8/24, with 0 critical flags in all three; full ACT-PO on-policy hard negatives and qualified task oracle absent.

## Experimental Protocol

Stage receipts and protected-access ledger are canonical. Protected outcomes require E17 freeze.

## Main Results

No qualified protected capability or safety estimate exists.

## OOD and Twin-B

Protected composition/policy/tool OOD closed: no valid E17 freeze.; Protected Twin-B transfer closed: Twin-B remains sealed and no valid finalist/freeze exists.

## Safety

R-TRACE protected factorial closed: no qualified ACT-PO finalist or valid E17 freeze.

## Security

Protected adversarial/security evaluation closed: no valid E17 freeze; development security evidence remains separate.

## Preference Noise

All 16 planned CUDA noise-training pilots and 12 x 24 paired synthetic development rollouts completed with exact flip, adapter, task, and log hashes; E07 task oracle and full ACT-PO source remain unqualified, so inference is exploratory only.

## Ablations

A7 weighting and A8 objective diagnostics executed on 24 synthetic development tasks; primary A3/A5 and other mechanism ablations unrun because ACT pairs/on-policy sources and task oracle are unqualified.

## External Benchmarks

E25: BLOCKED_EXTERNAL, E26: BLOCKED_EXTERNAL, E27: BLOCKED_EXTERNAL

## GPU and Systems

RTX 4090 CUDA training, rollout, and base/SFT NF4 serving lifecycle measured; outputs differ in generated length, and compile cold-cost/break-even plus frozen finalist serving comparison remain unmeasured.

## Failure Analysis

Unrun comparisons are null, not zero; see receipts for failures and blockers.

## Limitations

Synthetic action effects, REVIEW task difficulty, scripted preferences, and blocked external sources limit claims.

## Final Decision

**HOLD**. Protected effect estimates or critical gates are missing

## Reproducibility

Use pinned model/data manifests, stage receipts, and `act-agent run-all --resume` for hash audit.

## Supported Claims

See `artifacts/claim_ledger.json` and `reports/claim_ledger.md`.

## Prohibited Claims

No Amazon, production advertiser, real-user benefit, real action-effect, national-policy reproduction, safety-certification, or physical multi-GPU claim.

## Future Work

Repair REVIEW gates, acquire external sources with permitted network, and rerun under a fresh protected protocol if needed.

## Stage audit

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
| E17 | REVIEW | Power analysis exploratory; final freeze withheld because task oracle, preference sources, and finalists are unqualified; protected outcome access remains zero. |
| E18 | CLOSED | Protected ID evaluation closed: E17 did not freeze a valid protocol. |
| E19 | CLOSED | Protected composition/policy/tool OOD closed: no valid E17 freeze. |
| E20 | CLOSED | Protected Twin-B transfer closed: Twin-B remains sealed and no valid finalist/freeze exists. |
| E21 | CLOSED | R-TRACE protected factorial closed: no qualified ACT-PO finalist or valid E17 freeze. |
| E22 | CLOSED | Protected adversarial/security evaluation closed: no valid E17 freeze; development security evidence remains separate. |
| E23 | REVIEW | All 16 planned CUDA noise-training pilots and 12 x 24 paired synthetic development rollouts completed with exact flip, adapter, task, and log hashes; E07 task oracle and full ACT-PO source remain unqualified, so inference is exploratory only. |
| E24 | REVIEW | A7 weighting and A8 objective diagnostics executed on 24 synthetic development tasks; primary A3/A5 and other mechanism ablations unrun because ACT pairs/on-policy sources and task oracle are unqualified. |
| E25 | BLOCKED_EXTERNAL | BFCL V4 upstream acquisition blocked by workspace-write DNS/network restriction; no benchmark examples or outcomes accessed |
| E26 | BLOCKED_EXTERNAL | tau3 upstream acquisition blocked by workspace-write DNS/network restriction; no benchmark examples or outcomes accessed |
| E27 | BLOCKED_EXTERNAL | AgentDojo upstream acquisition blocked by workspace-write DNS/network restriction; no benchmark examples or outcomes accessed |
| E28 | REVIEW | RTX 4090 CUDA training, rollout, and base/SFT NF4 serving lifecycle measured; outputs differ in generated length, and compile cold-cost/break-even plus frozen finalist serving comparison remain unmeasured. |
| E29 | PASS | Final audited release and claim verification passed |
