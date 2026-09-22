#!/usr/bin/env bash
set -euo pipefail

# Run only with authorized host CUDA device access. Each Python runner also
# verifies nvidia-smi, CUDA/BF16, and a real CUDA matmul before inference.
python_bin=/home/bjw-0/.cache/act-agent-v1/venv/bin/python
checkpoint_root=/home/bjw-0/.cache/act-agent-v1/checkpoints

for rate in 05 10 20; do
  for method in dpo ipo robust_dpo act_po; do
    case "$method" in
      dpo) model=B4 ;;
      ipo) model=B5 ;;
      robust_dpo) model=B6 ;;
      act_po) model=M0 ;;
    esac
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader
    "$python_bin" -m act_agent.evaluation.model_rollout \
      --adapter-path "$checkpoint_root/${method}-seed11-steps3-pairs64-noise${rate}" \
      --model-label "$model" \
      --run-id "noise${rate}-${method}" \
      --count 24
  done
done
