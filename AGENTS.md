# ACT-Agent Repository Instructions

This repository is ACT-Agent:
Adaptive Constrained Trajectory Optimization for Tool-Using Agents.

The user will start the project by instructing Codex to read MASTER_PROMPT.md.

## Core execution policy

Work end-to-end rather than notebook-only.

Prefer:
- executable packages
- typed code
- tests
- configurations
- immutable experiment receipts
- canonical evidence
- statistical analysis
- reproducible reports
- resumable workflows

Negative and null results are valid scientific outcomes.

Never manipulate experiments so ACT-PO wins.

Do not stop at planning, scaffolding, a smoke test, EDA, one training run,
or an interim report.

## GPU-FIRST COMPUTE

This machine provides a local NVIDIA CUDA GPU through WSL.

For computationally material workloads with a valid CUDA implementation,
prefer CUDA.

GPU-preferred workloads include:

- PyTorch training
- QLoRA
- SFT
- DPO
- IPO
- Robust-DPO
- ACT-PO
- batched LLM rollout
- Transformer inference
- embedding generation when material
- GPU-capable XGBoost
- GPU serving experiments

Before every material GPU experiment:

1. verify nvidia-smi;
2. verify torch.cuda.is_available();
3. record GPU identity;
4. record CUDA/PyTorch versions;
5. record VRAM;
6. run a real CUDA computation.

An intended GPU-heavy experiment MUST NOT silently fall back to CPU.

If unexpected CPU fallback occurs:
- classify it as an execution problem;
- diagnose it;
- repair the CUDA path;
- do not accept the CPU result as equivalent evidence.

## SINGLE-GPU COMPUTE POLICY

Assume one physical GPU unless hardware qualification proves otherwise.

For one physical GPU:

- maximum concurrent heavy GPU jobs = 1;
- use GPU batching/vectorization;
- use efficient dataloaders;
- do not run SFT/DPO/etc. concurrently;
- CPU preprocessing, simulation, statistics, and reporting may run concurrently;
- producer/consumer pipelines are encouraged when safe.

Do not claim multi-GPU scaling without physical multi-GPU evidence.

## WSL STORAGE POLICY

Canonical repository:

C:\Users\bjw-0\Downloads\ACT-Agent

WSL path:

/mnt/c/Users/bjw-0/Downloads/ACT-Agent

Linux processes working directly on /mnt/c can incur substantial filesystem overhead.

Use $ACT_AGENT_SCRATCH on native WSL storage for high-I/O temporary work:

- Hugging Face cache
- uv environment
- pip cache
- model cache
- temporary checkpoints
- temporary Parquet
- rollout batches
- Triton / Inductor cache
- temporary benchmark data

Scratch is not canonical evidence.

Validated:
- source code
- configs
- manifests
- compact evidence
- reports
- claim ledgers

must be written back to the Windows repository.

## Resource-conscious ML

Prefer where justified:

- BF16
- 4-bit QLoRA
- gradient checkpointing
- dynamic padding
- bounded sequence lengths
- gradient accumulation
- precomputed reference log-probabilities for preference training

Do not enable torch.compile without a measured cold-cost/break-even study.

Track:
- VRAM
- GPU utilization
- temperature
- training throughput
- wall time

## Network

Shell network may be used for legitimate project requirements:

- authoritative research/documentation
- package installation
- model downloads
- public dataset downloads
- benchmark source acquisition

Prefer authoritative upstream sources.

## Scientific boundaries

Never claim without evidence:

- Amazon proprietary data
- Amazon Ads API integration
- real advertiser account control
- production advertiser outcomes
- production revenue lift
- production agent-safety certification
- real campaign-action causal effects
- real-user benefit
- real national advertising-policy reproduction
- physical multi-GPU scaling

Public advertising data may anchor observed distributions.

Mutable advertising actions and their effects remain synthetic digital-twin
evidence unless independently identified.

## Protected benchmarks

Final external benchmarks must not be used for:

- training
- SFT examples
- preference generation
- prompt selection
- thresholds
- hyperparameter tuning
- model selection

Record access/version ledgers.

## Repository safety

- Do not modify unrelated sibling repositories.
- Existing external datasets may be reused read-only after identity verification.
- Do not push to GitHub unless explicitly asked.
- Do not create paid cloud resources.
- Avoid sudo for routine project work.
- Keep raw data, checkpoints, large caches, and large generated artifacts out of Git.

## Resumability

Maintain:

STATUS.md
artifacts/run_state.json

Long experiments must be resumable.

A scientific change after protected-outcome access requires a new experiment or
protocol identity.

## Required final quality gates

Run as applicable:

- Ruff format/check
- mypy
- pytest
- coverage
- package build
- clean-wheel import
- CLI smoke
- CPU smoke
- CUDA smoke
- evidence verifier
- hash/manifest verifier
- claim verifier
- report regeneration
