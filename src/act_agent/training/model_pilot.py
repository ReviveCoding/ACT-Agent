"""CUDA-only Qwen3 model and QLoRA memory qualification pilot."""

from __future__ import annotations

import json
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def run(model_manifest: Path, output: Path) -> dict[str, Any]:
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
    )

    nvidia = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,memory.free,driver_version,temperature.gpu",
            "--format=csv,noheader",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    if not torch.cuda.is_available():
        raise RuntimeError("GPU-intended model pilot cannot run on CPU")
    x = torch.randn((256, 256), device="cuda")
    torch.cuda.synchronize()
    checksum = float((x @ x).sum().item())
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("BF16 unavailable; revise configuration before running")
    manifest = json.loads(model_manifest.read_text())
    snapshot = manifest["local_snapshot"]
    tokenizer = AutoTokenizer.from_pretrained(snapshot, local_files_only=True)
    prompt = tokenizer.apply_chat_template(
        [
            {"role": "system", "content": "You are a local advertising operations assistant."},
            {"role": "user", "content": "Read campaign C1 using the available tools."},
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "get_campaign",
                    "description": "Read a local campaign",
                    "parameters": {
                        "type": "object",
                        "properties": {"campaign_id": {"type": "string"}},
                        "required": ["campaign_id"],
                    },
                },
            }
        ],
        tokenize=False,
        add_generation_prompt=True,
    )
    configuration = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    started = time.monotonic()
    model = AutoModelForCausalLM.from_pretrained(
        snapshot,
        local_files_only=True,
        torch_dtype=torch.bfloat16,
        quantization_config=configuration,
        device_map={"": 0},
    )
    model.eval()
    load_seconds = time.monotonic() - started
    torch.cuda.reset_peak_memory_stats()
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    generation_started = time.monotonic()
    with torch.inference_mode():
        output_ids = model.generate(**inputs, max_new_tokens=48, do_sample=False)
    torch.cuda.synchronize()
    generation_seconds = time.monotonic() - generation_started
    elapsed = time.monotonic() - started
    after = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=memory.used,utilization.gpu,temperature.gpu",
            "--format=csv,noheader",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    generated = tokenizer.decode(
        output_ids[0][inputs["input_ids"].shape[-1] :], skip_special_tokens=False
    )
    evidence = {
        "timestamp": datetime.now(UTC).isoformat(),
        "model_id": manifest["model_id"],
        "revision": manifest["revision"],
        "model_hash": manifest["model_hash"],
        "device": torch.cuda.get_device_name(0),
        "nvidia_smi": nvidia.stdout.strip(),
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "bf16_supported": True,
        "preflight_matmul_checksum": checksum,
        "quantization": "NF4 4-bit double quantization, BF16 compute",
        "tokenizer_class": type(tokenizer).__name__,
        "chat_template_sha256": __import__("hashlib")
        .sha256(str(tokenizer.chat_template).encode())
        .hexdigest(),
        "prompt_tokens": int(inputs["input_ids"].shape[-1]),
        "generated_tokens": int(output_ids.shape[-1] - inputs["input_ids"].shape[-1]),
        "generated_text": generated,
        "elapsed_seconds_including_load": elapsed,
        "load_seconds": load_seconds,
        "generation_seconds": generation_seconds,
        "peak_vram_bytes": torch.cuda.max_memory_allocated(),
        "peak_reserved_vram_bytes": torch.cuda.max_memory_reserved(),
        "nvidia_smi_after": after.stdout.strip(),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2) + "\n")
    return evidence


if __name__ == "__main__":
    print(
        run(
            Path("artifacts/model_source_manifest.json"), Path("artifacts/model_qualification.json")
        )
    )
