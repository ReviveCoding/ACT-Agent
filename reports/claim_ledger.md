# Claim audit

- SUPPORTED: Criteo attribution file checksum verified and profiled
- SUPPORTED: Criteo uplift v2.1 file integrity and exact row count verified
- SUPPORTED: RTX 4090 CUDA BF16 and real matmul qualified through escalated access
- SUPPORTED_WITH_QUALIFIER: Twin-A synthetic calibration and internal known-answer checks passed
- SUPPORTED_WITH_QUALIFIER: B0 completed synthetic development tasks
- SUPPORTED_WITH_QUALIFIER: B0, B1, and B2 completed a 24-task paired synthetic CUDA development pilot
- SUPPORTED_WITH_QUALIFIER: SFT and weighted ACT-style scripted-pair pilots completed paired synthetic development rollouts
- SUPPORTED_WITH_QUALIFIER: Sixteen scripted-pair CUDA noise pilots and twelve paired synthetic development rollouts completed
- UNSUPPORTED: ACT-PO improves protected long-horizon capability without safety regression
- PROHIBITED: Synthetic interventions cause real advertiser lift
- PROHIBITED: Amazon proprietary data, Ads API integration, or production account control
- PROHIBITED: Production advertiser outcomes or production agent-safety certification
- PROHIBITED: Real-user benefit or real campaign-action causal effects
- PROHIBITED: Formal reproduction of national advertising policy
- PROHIBITED: Physical multi-GPU scaling
