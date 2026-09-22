# ACT-Agent v1.0

Adaptive Constrained Trajectory Optimization for Tool-Using Agents is a local
research program for stateful advertising-operations agents. Public Criteo
files anchor observed distributions; all mutable campaign-action effects are
synthetic. No advertiser account or production API is connected.

## Repository and scratch

The canonical repository is `/mnt/c/Users/bjw-0/Downloads/ACT-Agent`. Large
downloads, model weights, temporary Parquet, and checkpoints live in
`/home/bjw-0/.cache/act-agent-v1`. Validated compact receipts, aggregate marts,
reports, and hashes live in the repository. Set `ACT_AGENT_SCRATCH` to the
scratch directory for compatible commands.

## Resume and verification

`STATUS.md` and `artifacts/run_state.json` are the stage ledger. `act-agent
run-all --protocol act-v1-20260920 --device cuda --resume` verifies completed
immutable receipts and reports the earliest pending stage. Stage-specific
commands execute work; the ledger command does not manufacture outcomes or
repeat immutable stages.

The current CUDA environment is
`/home/bjw-0/.cache/act-agent-v1/venv`. GPU-dependent commands must be launched
with authorized host device access because the ordinary workspace sandbox
hides `/dev/dxg`. Each training and rollout runner checks `nvidia-smi`, PyTorch
CUDA/BF16, VRAM, and a real CUDA matmul, and fails rather than using CPU.
Only one heavy GPU job may run at a time.

Examples:

```bash
/home/bjw-0/.cache/act-agent-v1/venv/bin/python -m act_agent.twin.qualify
/home/bjw-0/.cache/act-agent-v1/venv/bin/python -m act_agent.evaluation.model_rollout --count 24 --max-turns 8
/home/bjw-0/.cache/act-agent-v1/venv/bin/python -m act_agent.evaluation.analyze_baselines
/home/bjw-0/.cache/act-agent-v1/venv/bin/python -m act_agent.evidence.warehouse_update
/home/bjw-0/.cache/act-agent-v1/venv/bin/python -m act_agent.training.sft --seed 11 --steps 120 --accumulation 8 --rank 16 --run-id sft-seed11
/home/bjw-0/.cache/act-agent-v1/venv/bin/python -m act_agent.evaluation.model_rollout --adapter-path /home/bjw-0/.cache/act-agent-v1/checkpoints/sft-seed11 --model-label B3 --count 24
/home/bjw-0/.cache/act-agent-v1/venv/bin/python -m act_agent.evaluation.analyze_adapter --model-label B3 --episodes /home/bjw-0/.cache/act-agent-v1/rollouts/b3-sft-seed11/episodes.jsonl --run-id e10_b3_seed11
/home/bjw-0/.cache/act-agent-v1/venv/bin/python -m act_agent.training.pairwise --mode dpo --seed 11 --steps 3 --pair-limit 64 --sft-run-id sft-seed11
```

Run GPU commands outside the device-hiding workspace sandbox via the authorized
escalated execution path. Do not run the CUDA programs on CPU. SFT stores
validated step checkpoints in scratch and resumes from the latest complete
checkpoint. Rollout writes each completed development episode to scratch and
skips it on resume. Protected split execution requires an E17 freeze; do not
use protected examples or outcomes for selection or tuning.

## Quality gates

```bash
/home/bjw-0/.cache/act-agent-v1/venv/bin/ruff format --check .
/home/bjw-0/.cache/act-agent-v1/venv/bin/ruff check .
/home/bjw-0/.cache/act-agent-v1/venv/bin/mypy src
/home/bjw-0/.cache/act-agent-v1/venv/bin/pytest -q --cov=act_agent
uv build --offline --out-dir /home/bjw-0/.cache/act-agent-v1/dist
/home/bjw-0/.cache/act-agent-v1/venv/bin/act-agent verify
```

`act-agent verify` is the final release gate and will fail while mandatory
stages are pending. The scientific verdict is generated only after all
mandatory stages have terminal receipts. See `MASTER_PROMPT.md`, `AGENTS.md`,
and `protocols/act_v1_draft.md` for the protocol and claim boundaries.
