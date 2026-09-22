"""CUDA-only assistant-masked QLoRA SFT with resumable checkpoints."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from act_agent.data.pipeline import sha256


def preflight() -> dict[str, Any]:
    import torch

    status = subprocess.run(
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
        raise RuntimeError("GPU-intended SFT cannot run on CPU")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("BF16 unavailable; configuration requires revision")
    x = torch.randn((256, 256), device="cuda")
    torch.cuda.synchronize()
    checksum = float((x @ x).sum().item())
    return {
        "nvidia_smi": status.stdout.strip(),
        "device": torch.cuda.get_device_name(0),
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "vram_bytes": torch.cuda.get_device_properties(0).total_memory,
        "bf16_supported": True,
        "matmul_checksum": checksum,
    }


def train(
    *,
    seed: int,
    max_steps: int,
    accumulation: int,
    rank: int,
    tokens_path: Path,
    model_manifest: Path,
    output_dir: Path,
    receipt_path: Path,
    checkpoint_interval: int = 10,
) -> dict[str, Any]:
    import torch
    from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig

    if max_steps < 1 or accumulation < 1 or rank < 1 or checkpoint_interval < 1:
        raise ValueError("positive training settings required")
    if receipt_path.exists():
        prior: dict[str, Any] = json.loads(receipt_path.read_text())
        if prior.get("status") == "PASS":
            if (
                prior.get("seed") != seed
                or prior.get("max_steps") != max_steps
                or prior.get("gradient_accumulation") != accumulation
                or prior.get("lora_rank") != rank
            ):
                raise ValueError("completed run identity differs")
            return prior
    proof = preflight()
    model_info = json.loads(model_manifest.read_text())
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    quantization = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_info["local_snapshot"],
        local_files_only=True,
        dtype=torch.bfloat16,
        quantization_config=quantization,
        device_map={"": 0},
    )
    if not getattr(model, "is_loaded_in_4bit", False):
        raise RuntimeError("QLoRA base did not load in 4-bit")
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    lora = LoraConfig(
        r=rank,
        lora_alpha=2 * rank,
        lora_dropout=0.05,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        bias="none",
        task_type="CAUSAL_LM",
    )
    resumable = sorted(
        (
            p
            for p in output_dir.glob("step-*")
            if p.is_dir()
            and (p / "optimizer_resume.pt").is_file()
            and (p / "adapter_model.safetensors").is_file()
            and (p / "complete.json").is_file()
        ),
        key=lambda p: int(p.name.split("-")[-1]),
    )
    resume_dir = resumable[-1] if resumable else None
    model = (
        PeftModel.from_pretrained(model, resume_dir, is_trainable=True)
        if resume_dir
        else get_peft_model(model, lora)
    )
    model.train()
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    if trainable <= 0:
        raise RuntimeError("no trainable LoRA parameters")
    dataset = pq.read_table(  # type: ignore[no-untyped-call]
        tokens_path, columns=["input_ids", "labels"]
    ).to_pylist()
    if not dataset:
        raise ValueError("empty token dataset")
    order = list(range(len(dataset)))
    random.Random(seed).shuffle(order)
    optimizer = torch.optim.AdamW(
        (p for p in model.parameters() if p.requires_grad), lr=2e-4, weight_decay=0.0
    )
    losses: list[float] = []
    step_seconds: list[float] = []
    tokens_seen = 0
    start_step = 0
    elapsed_prior = 0.0
    if resume_dir is not None:
        completion = json.loads((resume_dir / "complete.json").read_text())
        if any(
            sha256(resume_dir / name) != expected
            for name, expected in completion["files_sha256"].items()
        ):
            raise ValueError("resume checkpoint hash mismatch")
        saved = torch.load(
            resume_dir / "optimizer_resume.pt", map_location="cpu", weights_only=False
        )
        if (
            saved["seed"] != seed
            or saved["rank"] != rank
            or saved["accumulation"] != accumulation
            or saved["order"] != order
            or saved["tokens_sha256"] != sha256(tokens_path)
        ):
            raise ValueError("resume checkpoint identity mismatch")
        optimizer.load_state_dict(saved["optimizer"])
        torch.set_rng_state(saved["torch_rng"])
        torch.cuda.set_rng_state(saved["cuda_rng"])
        start_step = int(saved["step"])
        if start_step >= max_steps:
            raise ValueError("resume checkpoint exceeds requested training steps")
        losses = list(saved["losses"])
        step_seconds = list(saved["step_seconds"])
        tokens_seen = int(saved["tokens_seen"])
        elapsed_prior = float(saved["elapsed_seconds"])
        print(f"resuming SFT from step={start_step}", flush=True)
    started = time.monotonic()
    torch.cuda.reset_peak_memory_stats()
    for step in range(start_step, max_steps):
        optimizer.zero_grad(set_to_none=True)
        step_started = time.monotonic()
        micro_losses = []
        for micro in range(accumulation):
            row = dataset[order[(step * accumulation + micro) % len(order)]]
            ids = torch.tensor([row["input_ids"]], dtype=torch.long, device="cuda")
            labels = torch.tensor([row["labels"]], dtype=torch.long, device="cuda")
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                loss = model(input_ids=ids, labels=labels, use_cache=False).loss
            if not torch.isfinite(loss):
                raise RuntimeError("non-finite SFT loss")
            (loss / accumulation).backward()
            micro_losses.append(float(loss.detach().item()))
            tokens_seen += int(ids.numel())
        torch.nn.utils.clip_grad_norm_((p for p in model.parameters() if p.requires_grad), 1.0)
        optimizer.step()
        torch.cuda.synchronize()
        losses.append(sum(micro_losses) / len(micro_losses))
        step_seconds.append(time.monotonic() - step_started)
        print(
            f"step={step + 1}/{max_steps} loss={losses[-1]:.4f} seconds={step_seconds[-1]:.2f}",
            flush=True,
        )
        if (step + 1) % checkpoint_interval == 0 and step + 1 < max_steps:
            path = output_dir / f"step-{step + 1:05d}"
            path.mkdir(parents=True, exist_ok=True)
            model.save_pretrained(path)
            torch.save(
                {
                    "optimizer": optimizer.state_dict(),
                    "step": step + 1,
                    "seed": seed,
                    "rank": rank,
                    "accumulation": accumulation,
                    "order": order,
                    "tokens_sha256": sha256(tokens_path),
                    "torch_rng": torch.get_rng_state(),
                    "cuda_rng": torch.cuda.get_rng_state(),
                    "losses": losses,
                    "step_seconds": step_seconds,
                    "tokens_seen": tokens_seen,
                    "elapsed_seconds": elapsed_prior + time.monotonic() - started,
                },
                path / "optimizer_resume.pt",
            )
            (path / "complete.json").write_text(
                json.dumps(
                    {
                        "step": step + 1,
                        "files_sha256": {
                            "adapter_model.safetensors": sha256(path / "adapter_model.safetensors"),
                            "optimizer_resume.pt": sha256(path / "optimizer_resume.pt"),
                        },
                    },
                    indent=2,
                )
                + "\n"
            )
            old = sorted(output_dir.glob("step-*"))[:-2]
            for previous in old:
                shutil.rmtree(previous)
    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_dir)
    checkpoint = {
        "optimizer": optimizer.state_dict(),
        "step": max_steps,
        "seed": seed,
        "order": order,
        "torch_rng": torch.get_rng_state(),
        "cuda_rng": torch.cuda.get_rng_state(),
        "rank": rank,
        "accumulation": accumulation,
        "tokens_sha256": sha256(tokens_path),
        "losses": losses,
        "step_seconds": step_seconds,
        "tokens_seen": tokens_seen,
        "elapsed_seconds": elapsed_prior + time.monotonic() - started,
    }
    torch.save(checkpoint, output_dir / "optimizer_resume.pt")
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
    adapter_files = {p.name: sha256(p) for p in output_dir.glob("*.safetensors")}
    if not adapter_files:
        raise RuntimeError("adapter checkpoint missing")
    result = {
        "timestamp": datetime.now(UTC).isoformat(),
        "status": "PASS",
        "protocol": "act-v1-20260920",
        "seed": seed,
        "max_steps": max_steps,
        "gradient_accumulation": accumulation,
        "microbatch": 1,
        "lora_rank": rank,
        "quantization": "NF4 4-bit BF16 double quantization",
        "model_hash": model_info["model_hash"],
        "tokens_sha256": sha256(tokens_path),
        "adapter_files_sha256": adapter_files,
        "adapter_hash": hashlib.sha256(
            json.dumps(adapter_files, sort_keys=True).encode()
        ).hexdigest(),
        "adapter_path": str(output_dir),
        "trainable_parameters": trainable,
        "losses": losses,
        "wall_seconds": elapsed_prior + time.monotonic() - started,
        "resumed_from_step": start_step,
        "checkpoint_interval": checkpoint_interval,
        "tokens_seen": tokens_seen,
        "tokens_per_second": tokens_seen / max(sum(step_seconds), 1e-9),
        "peak_allocated_vram_bytes": torch.cuda.max_memory_allocated(),
        "peak_reserved_vram_bytes": torch.cuda.max_memory_reserved(),
        "nvidia_smi_after": after.stdout.strip(),
        "preflight": proof,
        "torch_compile": False,
        "dataset_role": "training",
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--accumulation", type=int, default=8)
    parser.add_argument("--rank", type=int, default=16)
    parser.add_argument("--checkpoint-interval", type=int, default=10)
    parser.add_argument("--run-id", default="sft-pilot-seed11")
    args = parser.parse_args()
    scratch = Path("/home/bjw-0/.cache/act-agent-v1")
    result = train(
        seed=args.seed,
        max_steps=args.steps,
        accumulation=args.accumulation,
        rank=args.rank,
        tokens_path=scratch / "data/sft_tokens.parquet",
        model_manifest=Path("artifacts/model_source_manifest.json"),
        output_dir=scratch / "checkpoints" / args.run_id,
        receipt_path=Path("artifacts/training") / f"{args.run_id}.json",
        checkpoint_interval=args.checkpoint_interval,
    )
    print(json.dumps({k: v for k, v in result.items() if k not in {"losses"}}, indent=2))


if __name__ == "__main__":
    main()
