# ACT-Agent

**Research status: HOLD**

ACT-Agent studies tool-using agents in a stateful advertising-operations simulator. The goal is to evaluate task completion, process compliance, and safety separately, rather than treating a successful final action as sufficient evidence of reliability.

The environment uses public Criteo data to anchor observed advertising distributions. Campaign interventions, downstream outcomes, and mutable business state are synthetic. No production advertising accounts or APIs are connected.

## Study design

The implementation includes a transactional digital twin, deterministic process checks, baseline agent rollouts, a QLoRA supervised fine-tuning path, and exploratory preference-training comparisons. Research stages and evidence receipts are recorded in [STATUS.md](STATUS.md), with the study protocol in [protocols/act_v1_draft.md](protocols/act_v1_draft.md).

The current evidence base contains 16,468,027 public Criteo impression records across 675 campaigns. This is not evidence of live advertising-system performance.

## Results and current limitations

- The development B0 baseline completed 198 of 400 tasks with no critical process violations in that set.
- On 24 paired development tasks, B0 completed 14, while the two baseline challengers completed 8 and 7.
- A seed-11, 120-step QLoRA SFT candidate completed 8 of 24 development tasks with no critical process flags.
- Small scripted-pair preference-training pilots were exploratory. Their results do not establish improvement from the proposed ACT-specific mechanism.

**No protected final capability or safety claim is qualified.** The independent task-completion oracle and several preference-data requirements remain unresolved, so the scientific decision is HOLD. See the [technical report](reports/final_technical_report.md) for comparison conditions and experiment-level results.

## Installation and verification

Python 3.12 or later is required. The source package and development checks can be installed with:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python -m pytest -q
```

The full model experiments require separately obtained source data, qualified local CUDA/BF16 access, and the optional GPU dependencies. Large checkpoints and datasets are not part of the GitHub source tree.

```bash
act-agent run-all --protocol act-v1-20260920 --device cuda --resume
act-agent verify
```

The first command checks the recorded stage state and reports pending work. The final verification gate is expected to fail while mandatory stages remain incomplete. It should not be interpreted as evidence of a finished evaluation.

## Evidence

See [STATUS.md](STATUS.md), the [technical report](reports/final_technical_report.md), and the [claim ledger](reports/claim_ledger.md). Experiment receipts and manifests preserve the boundary between public data, synthetic interventions, development results, and protected evaluation.
