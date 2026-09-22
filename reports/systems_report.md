# Systems report

Escalated host-device execution qualified the NVIDIA GeForce RTX 4090 Laptop GPU (16,376 MiB) with PyTorch 2.14.0+cu130, BF16 support, and a real CUDA matmul. The original E00 receipt is immutable; a post-reboot qualification is in `artifacts/e00_environment/post_reboot_cuda_probe.json`.

The isolated frozen Qwen NF4/BF16 model pilot loaded in 23.10 seconds and generated 22 tokens in 8.08 seconds. A three-step QLoRA SFT pilot processed 4,087 tokens at 154.38 tokens per optimizer-step time second, with 7.31 GB peak reserved VRAM. The archived B1/B2 one-task pilot saw concurrent GPU contention and generated 85 tokens in 119.42 seconds and 118 tokens in 205.47 seconds, respectively. The B2 completion result from that archived pilot is invalid because it lacked a final answer; the evaluator has been corrected.

`artifacts/systems_development.json` contains the exact receipts. `torch.compile` remains disabled because cold cost and break-even have not been measured. The local serving lifecycle benchmark has now run, but no frozen finalist serving comparison or measured `torch.compile` break-even exists. E28 remains REVIEW.

The corrected 24-task B1/B2 rollout ran on the escalated RTX 4090 with BF16 and NF4. Its receipt, `artifacts/e09_baseline_manifest.json`, records 1,599.80 seconds of wall time, 4.16 GB peak reserved VRAM, and a real CUDA preflight. B1 generated 1,866 tokens in 439.37 generation seconds; B2 generated 4,188 tokens in 1,158.97 generation seconds. These totals include different task/turn behavior, so they are not a controlled serving-speed comparison. A four-step QLoRA SFT pilot peaked at 7.31 GB reserved VRAM. A copied step-three checkpoint resumed to the same final loss with relative adapter L2 difference 8.4×10⁻⁵; bitwise identity is not claimed. See `artifacts/training/sft_resume_validation.json`.

## CUDA serving lifecycle diagnostics

- Qwen base: startup 25.33 s; cold first token 1.83 s; median steady first token 0.232 s; 6.68 generated tokens/s; 3.83 GiB peak reserved VRAM; shutdown 0.408 s.
- SFT seed 11, step 120: startup 22.95 s; cold first token 1.70 s; median steady first token 0.469 s; 3.16 generated tokens/s; 4.05 GiB peak reserved VRAM; shutdown 0.523 s.

The base generated 64 tokens in each full repeat; the SFT adapter generated 16 before EOS. Different output lengths prevent a controlled throughput ranking. Both measurements used one local synthetic prompt, no concurrency, and NF4/BF16 on the same RTX 4090. Receipts: `artifacts/systems_serving_qwen-base.json` and `artifacts/systems_serving_sft-seed11-step120.json`. No production serving claim follows.
