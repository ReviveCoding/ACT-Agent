"""CUDA-only bounded HF inference latency and lifecycle benchmark."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import statistics
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from act_agent.data.pipeline import sha256
from act_agent.tasks.generator import agent_observation, make_task
from act_agent.training.sft import preflight


def _timed_generate(model: Any, tokenizer: Any, inputs: Any, tokens: int) -> tuple[float, int, str]:
    import torch

    torch.cuda.synchronize()
    begin = time.monotonic()
    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    torch.cuda.synchronize()
    new = output[0][inputs["input_ids"].shape[-1] :]
    return (
        time.monotonic() - begin,
        int(new.numel()),
        hashlib.sha256(new.cpu().numpy().tobytes()).hexdigest(),
    )


def benchmark(model_manifest: Path, adapter: Path | None, repeats: int = 3) -> dict[str, Any]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    if repeats < 2:
        raise ValueError("at least two steady repeats required")
    proof = preflight()
    manifest = json.loads(model_manifest.read_text())
    started = time.monotonic()
    tokenizer = AutoTokenizer.from_pretrained(manifest["local_snapshot"], local_files_only=True)
    quantization = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        manifest["local_snapshot"],
        local_files_only=True,
        dtype=torch.bfloat16,
        quantization_config=quantization,
        device_map={"": 0},
    )
    if not getattr(model, "is_loaded_in_4bit", False):
        raise RuntimeError("CUDA NF4 model load failed")
    adapter_hashes = None
    if adapter is not None:
        from peft import PeftModel

        adapter_hashes = {path.name: sha256(path) for path in adapter.glob("*.safetensors")}
        if not adapter_hashes:
            raise FileNotFoundError("adapter weights missing")
        model = PeftModel.from_pretrained(model, adapter, is_trainable=False)
    model.eval()
    torch.cuda.synchronize()
    startup_seconds = time.monotonic() - started
    prompt = [
        {"role": "system", "content": "Answer a local synthetic campaign question concisely."},
        {"role": "user", "content": json.dumps(agent_observation(make_task("development", 0)))},
    ]
    rendered = tokenizer.apply_chat_template(prompt, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(rendered, return_tensors="pt").to("cuda")
    prompt_tokens = int(inputs["input_ids"].numel())
    torch.cuda.reset_peak_memory_stats()
    cold_first_token = _timed_generate(model, tokenizer, inputs, 1)
    steady_first_token = [_timed_generate(model, tokenizer, inputs, 1) for _ in range(repeats)]
    full = [_timed_generate(model, tokenizer, inputs, 64) for _ in range(repeats)]
    gpu_active = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=memory.used,utilization.gpu,temperature.gpu",
            "--format=csv,noheader",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    total_tokens = sum(item[1] for item in full)
    total_seconds = sum(item[0] for item in full)
    peak_allocated = torch.cuda.max_memory_allocated()
    peak_reserved = torch.cuda.max_memory_reserved()
    shutdown_started = time.monotonic()
    del model, inputs
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.synchronize()
    shutdown_seconds = time.monotonic() - shutdown_started
    gpu_after_shutdown = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=memory.used,utilization.gpu,temperature.gpu",
            "--format=csv,noheader",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "status": "PASS",
        "backend": "HF Transformers NF4 BF16",
        "model_hash": manifest["model_hash"],
        "benchmark_source_sha256": sha256(Path(__file__)),
        "adapter_path": str(adapter) if adapter is not None else None,
        "adapter_files_sha256": adapter_hashes,
        "prompt_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
        "prompt_tokens": prompt_tokens,
        "startup_seconds": startup_seconds,
        "cold_first_token_seconds": cold_first_token[0],
        "steady_first_token_seconds": [item[0] for item in steady_first_token],
        "steady_first_token_median_seconds": statistics.median(
            item[0] for item in steady_first_token
        ),
        "full_generation_seconds": [item[0] for item in full],
        "full_generation_tokens": [item[1] for item in full],
        "full_generation_token_hashes": [item[2] for item in full],
        "generated_tokens_per_second": total_tokens / total_seconds,
        "single_prompt_tasks_per_second": repeats / total_seconds,
        "peak_allocated_vram_bytes": peak_allocated,
        "peak_reserved_vram_bytes": peak_reserved,
        "nvidia_smi_active": gpu_active.stdout.strip(),
        "shutdown_seconds": shutdown_seconds,
        "nvidia_smi_after_shutdown": gpu_after_shutdown.stdout.strip(),
        "preflight": proof,
        "torch_compile": False,
        "protected_outcome_access": 0,
        "scope": "single synthetic prompt, no concurrency or production serving claim",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", type=Path)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--run-id", default="qwen-base")
    args = parser.parse_args()
    result = benchmark(Path("artifacts/model_source_manifest.json"), args.adapter, args.repeats)
    target = Path("artifacts") / f"systems_serving_{args.run_id}.json"
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(target, result["generated_tokens_per_second"])


if __name__ == "__main__":
    main()
