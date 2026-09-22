# ACT-Agent v1.0 draft protocol (unfrozen)

Identity: `act-v1-20260920`. No protected internal or external outcome has been accessed. This document is a draft; `artifacts/freeze_manifest.json` must be created only after development pilots and candidate model hashes exist.

## Scientific question

H1: ACT-PO improves paired protected long-horizon task completion over SFT. H2: ACT-PO critical-violation rate is non-inferior to SFT. Promotion requires both gates plus data integrity, simulator validity, process evaluator validity, protocol integrity, no catastrophic Twin-B failure, and no unacceptable security regression. The capability threshold and safety margin must be set from pilot/power evidence before protected outcomes.

## Split governance

Training, calibration, development, pilot, ID, composition, policy, tool, Twin-B, and security tasks use disjoint SHA-256 seed namespaces. Final BFCL V4, tau3, and AgentDojo content is final-only. No external benchmark example may become an SFT or preference item, prompt selection input, or tuning signal.

## Pairing and statistics

Candidate agents receive the same task ID, state, policy pack, hidden fault, world seed, and exogenous tape. Primary inference is a task-family clustered paired bootstrap. McNemar is a paired binary sensitivity check; Wilson intervals characterize rare safety events. Training seed uncertainty and world uncertainty must be reported separately.

## Currently qualified scope

Criteo attribution and uplift source hashes, aggregate marts, Twin-A known-answer checks, and process-contract checks are qualified. B0 has 400 synthetic development episodes. B0/B1/B2 have a corrected 24-task paired CUDA development pilot with separate completion, process, and attempted-violation counts. E07 remains REVIEW because numeric L3–L9 labels lack distinct mechanics and an independent completion oracle. The paired pilot is diagnostic only. Scripted preference perturbations are development-only and do not replace ReAct, SFT, or on-policy candidate rollouts.

## Freeze prerequisites

Before E17: exact Qwen model revision and tokenizer, trained adapter hashes for each finalist seed, tool and prompt hashes, frozen task generator/simulator, data role manifest, sample sizes and statistical gates from pilot/power results, and explicit access ledger. Twin-B hidden parameters must be isolated from training and tuning. Any scientific change after protected access creates a new protocol identity.
