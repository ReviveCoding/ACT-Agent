"""CUDA-only QLoRA pairwise pilots with frozen SFT reference log probabilities.

This is a bounded development implementation of DPO, IPO, robust DPO, and
weighted ACT-style DPO. It does not by itself qualify ACT-PO hard-negative mining.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from act_agent.data.pipeline import sha256
from act_agent.training.sft import preflight

MODES = {"dpo", "ipo", "robust_dpo", "act_pair", "act_po"}


def flip_preference_labels(
    pairs: list[dict[str, Any]], rate: float, seed: int
) -> tuple[list[dict[str, Any]], list[str]]:
    """Deterministically invert a fixed fraction of development pair labels."""
    if not 0 <= rate <= 1:
        raise ValueError("noise rate must lie in [0, 1]")
    if len({pair["pair_id"] for pair in pairs}) != len(pairs):
        raise ValueError("duplicate pair IDs in noise study")
    chosen = sorted(
        pairs,
        key=lambda pair: hashlib.sha256(f"noise:{seed}:{pair['pair_id']}".encode()).digest(),
    )[: round(rate * len(pairs))]
    flipped_ids = {pair["pair_id"] for pair in chosen}
    out = []
    for pair in pairs:
        row = dict(pair)
        if row["pair_id"] in flipped_ids:
            for suffix in ("ids", "labels", "assistant_tokens"):
                row[f"chosen_{suffix}"], row[f"rejected_{suffix}"] = (
                    row[f"rejected_{suffix}"],
                    row[f"chosen_{suffix}"],
                )
        out.append(row)
    return out, sorted(flipped_ids)


def pairwise_objective(mode: str, advantage: Any, beta: float, weight: float = 1.0) -> Any:
    """DPO-style method mapping; advantage is policy minus reference log-ratio."""
    import torch.nn.functional as F

    if mode not in MODES or beta <= 0:
        raise ValueError("invalid pairwise objective")
    scaled = beta * advantage
    if mode == "ipo":
        objective = (advantage - 1 / (2 * beta)).square()
    elif mode == "robust_dpo":
        objective = (-0.9 * F.logsigmoid(scaled) + 0.1 * F.logsigmoid(-scaled)) / 0.8
    else:
        objective = -F.logsigmoid(scaled)
    return (weight if mode == "act_po" else 1.0) * objective


def sequence_logprob(model: Any, ids: list[int], labels: list[int]) -> Any:
    import torch
    import torch.nn.functional as F

    tokens = torch.tensor([ids], dtype=torch.long, device="cuda")
    targets = torch.tensor([labels], dtype=torch.long, device="cuda")
    with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
        logits = model(input_ids=tokens, use_cache=False).logits
    shifted_logits = logits[:, :-1, :].float()
    shifted_targets = targets[:, 1:]
    losses = F.cross_entropy(
        shifted_logits.transpose(1, 2), shifted_targets, reduction="none", ignore_index=-100
    )
    return -losses.sum()


def train(
    *,
    mode: str,
    seed: int,
    max_steps: int,
    pair_limit: int,
    accumulation: int,
    sft_adapter: Path,
    pairs_path: Path,
    model_manifest: Path,
    output_dir: Path,
    receipt_path: Path,
    beta: float = 0.1,
    noise_rate: float = 0.0,
) -> dict[str, Any]:
    import torch
    from peft import PeftModel, prepare_model_for_kbit_training
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig

    if (
        mode not in MODES
        or min(max_steps, pair_limit, accumulation) < 1
        or beta <= 0
        or not 0 <= noise_rate <= 1
    ):
        raise ValueError("invalid pairwise training configuration")
    if receipt_path.exists():
        prior: dict[str, Any] = json.loads(receipt_path.read_text())
        if prior.get("status") == "PASS":
            identity = (
                prior.get("mode") == mode
                and prior.get("seed") == seed
                and prior.get("steps") == max_steps
                and prior.get("accumulation") == accumulation
                and prior.get("pair_limit") == pair_limit
                and prior.get("beta") == beta
                and prior.get("noise_rate", 0.0) == noise_rate
                and prior.get("base_model_hash")
                == json.loads(model_manifest.read_text()).get("model_hash")
                and prior.get("preference_tokens_sha256") == sha256(pairs_path)
                and prior.get("sft_adapter_sha256")
                == {path.name: sha256(path) for path in sft_adapter.glob("*.safetensors")}
            )
            adapter_intact = all(
                (output_dir / name).is_file() and sha256(output_dir / name) == expected
                for name, expected in prior.get("adapter_files_sha256", {}).items()
            )
            if prior.get("adapter_config_sha256"):
                config_path = output_dir / "adapter_config.json"
                adapter_intact = (
                    adapter_intact
                    and config_path.is_file()
                    and sha256(config_path) == prior["adapter_config_sha256"]
                )
            if not identity or not adapter_intact:
                raise ValueError("completed pairwise run identity or adapter hash differs")
            return prior
    proof = preflight()
    manifest = json.loads(model_manifest.read_text())
    table = pq.read_table(pairs_path).to_pylist()  # type: ignore[no-untyped-call]
    if not table:
        raise ValueError("empty preference table")
    order = sorted(
        range(len(table)),
        key=lambda i: hashlib.sha256(f"{seed}:{table[i]['pair_id']}".encode()).digest(),
    )[:pair_limit]
    pairs, flipped_pair_ids = flip_preference_labels([table[i] for i in order], noise_rate, seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    quantization = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    base = AutoModelForCausalLM.from_pretrained(
        manifest["local_snapshot"],
        local_files_only=True,
        dtype=torch.bfloat16,
        quantization_config=quantization,
        device_map={"": 0},
    )
    if not getattr(base, "is_loaded_in_4bit", False):
        raise RuntimeError("pairwise base did not load in 4-bit on CUDA")
    base.config.use_cache = False
    base = prepare_model_for_kbit_training(base, use_gradient_checkpointing=True)
    model = PeftModel.from_pretrained(base, sft_adapter, is_trainable=True)
    trainable_parameters = sum(p.numel() for p in model.parameters() if p.requires_grad)
    if trainable_parameters <= 0:
        raise RuntimeError("no trainable preference adapter parameters")
    model.eval()
    started = time.monotonic()
    output_dir.mkdir(parents=True, exist_ok=True)
    reference_meta = {
        "reference_code_sha256": sha256(Path(__file__)),
        "model_hash": manifest["model_hash"],
        "sft_adapter_sha256": {p.name: sha256(p) for p in sft_adapter.glob("*.safetensors")},
        "preference_tokens_sha256": sha256(pairs_path),
        "pair_ids": [p["pair_id"] for p in pairs],
        "noise_rate": noise_rate,
        "flipped_pair_ids": flipped_pair_ids,
    }
    cache_key = hashlib.sha256(json.dumps(reference_meta, sort_keys=True).encode()).hexdigest()
    reference_dir = output_dir.parent / "reference_cache" / cache_key
    reference_dir.mkdir(parents=True, exist_ok=True)
    reference_path = reference_dir / "reference_logprobs.jsonl"
    reference_meta_path = reference_dir / "reference_meta.json"
    if reference_meta_path.exists():
        if json.loads(reference_meta_path.read_text()) != reference_meta:
            raise ValueError("cached reference log probabilities have mismatched identity")
    else:
        reference_meta_path.write_text(json.dumps(reference_meta, indent=2) + "\n")
    reference: list[tuple[float, float]] = []
    if reference_path.exists():
        cached_text = reference_path.read_text()
        if cached_text and not cached_text.endswith("\n"):
            cached_text = cached_text.rsplit("\n", 1)[0] + "\n" if "\n" in cached_text else ""
            reference_path.write_text(cached_text)
        for index, line in enumerate(cached_text.splitlines()):
            item = json.loads(line)
            if (
                index >= len(pairs)
                or item["index"] != index
                or item["pair_id"] != pairs[index]["pair_id"]
            ):
                raise ValueError("reference cache order mismatch")
            reference.append((float(item["chosen"]), float(item["rejected"])))
    with reference_path.open("a") as stream, torch.inference_mode():
        for index in range(len(reference), len(pairs)):
            pair = pairs[index]
            chosen = float(
                sequence_logprob(model, pair["chosen_ids"], pair["chosen_labels"]).item()
            )
            rejected = float(
                sequence_logprob(model, pair["rejected_ids"], pair["rejected_labels"]).item()
            )
            reference.append((chosen, rejected))
            stream.write(
                json.dumps(
                    {
                        "index": index,
                        "pair_id": pair["pair_id"],
                        "chosen": chosen,
                        "rejected": rejected,
                    }
                )
                + "\n"
            )
            stream.flush()
            if (index + 1) % 50 == 0:
                print(f"reference={index + 1}/{len(pairs)}", flush=True)
    reference_seconds = time.monotonic() - started
    model.train()
    optimizer = torch.optim.AdamW(
        (p for p in model.parameters() if p.requires_grad), lr=5e-5, weight_decay=0.0
    )
    losses: list[float] = []
    train_started = time.monotonic()
    torch.cuda.reset_peak_memory_stats()
    rng = random.Random(seed)
    schedule = list(range(len(pairs)))
    rng.shuffle(schedule)
    for step in range(max_steps):
        optimizer.zero_grad(set_to_none=True)
        micro_losses = []
        for micro in range(accumulation):
            index = schedule[(step * accumulation + micro) % len(schedule)]
            pair = pairs[index]
            chosen_lp = sequence_logprob(model, pair["chosen_ids"], pair["chosen_labels"])
            rejected_lp = sequence_logprob(model, pair["rejected_ids"], pair["rejected_labels"])
            if mode == "ipo":
                chosen_tokens = max(1, int(pair["chosen_assistant_tokens"]))
                rejected_tokens = max(1, int(pair["rejected_assistant_tokens"]))
                advantage = (chosen_lp - reference[index][0]) / chosen_tokens - (
                    rejected_lp - reference[index][1]
                ) / rejected_tokens
            else:
                reference_delta = reference[index][0] - reference[index][1]
                advantage = chosen_lp - rejected_lp - reference_delta
            weight = float(pair["weight"]) if mode == "act_po" else 1.0
            loss = pairwise_objective(mode, advantage, beta, weight)
            if not torch.isfinite(loss):
                raise RuntimeError("nonfinite pairwise loss")
            (loss / accumulation).backward()
            micro_losses.append(float(loss.detach().item()))
        torch.nn.utils.clip_grad_norm_((p for p in model.parameters() if p.requires_grad), 1.0)
        optimizer.step()
        losses.append(sum(micro_losses) / len(micro_losses))
        print(f"mode={mode} step={step + 1}/{max_steps} loss={losses[-1]:.4f}", flush=True)
    model.save_pretrained(output_dir)
    adapter_files = {p.name: sha256(p) for p in output_dir.glob("*.safetensors")}
    if not adapter_files:
        raise RuntimeError("pairwise adapter checkpoint missing")
    adapter_config_path = output_dir / "adapter_config.json"
    if not adapter_config_path.is_file():
        raise RuntimeError("pairwise adapter config missing")
    receipt = {
        "timestamp": datetime.now(UTC).isoformat(),
        "status": "PASS",
        "protocol": "act-v1-20260920",
        "mode": mode,
        "seed": seed,
        "steps": max_steps,
        "accumulation": accumulation,
        "pair_limit": len(pairs),
        "beta": beta,
        "noise_rate": noise_rate,
        "flipped_pair_ids": flipped_pair_ids,
        "base_model_hash": manifest["model_hash"],
        "sft_adapter_path": str(sft_adapter),
        "sft_adapter_sha256": {p.name: sha256(p) for p in sft_adapter.glob("*.safetensors")},
        "preference_tokens_sha256": sha256(pairs_path),
        "adapter_path": str(output_dir),
        "adapter_files_sha256": adapter_files,
        "adapter_config_sha256": sha256(adapter_config_path),
        "trainable_parameters": trainable_parameters,
        "reference_precomputed": True,
        "reference_sha256": sha256(reference_path),
        "reference_path": str(reference_path),
        "reference_cache_key": cache_key,
        "reference_seconds": reference_seconds,
        "train_seconds": time.monotonic() - train_started,
        "peak_allocated_vram_bytes": torch.cuda.max_memory_allocated(),
        "peak_reserved_vram_bytes": torch.cuda.max_memory_reserved(),
        "losses": losses,
        "preflight": proof,
        "candidate_source": "scripted development pairs only",
        "method_mapping": "DPO/IPO/robust formulas aligned to installed TRL DPOTrainer; IPO uses assistant-token average log probabilities; robust epsilon=0.1",
        "protected_outcome_access": 0,
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=sorted(MODES), required=True)
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--steps", type=int, default=3)
    parser.add_argument("--pair-limit", type=int, default=64)
    parser.add_argument("--accumulation", type=int, default=1)
    parser.add_argument("--sft-run-id", default="sft-seed11")
    parser.add_argument("--run-id")
    parser.add_argument("--noise-rate", type=float, default=0.0)
    args = parser.parse_args()
    scratch = Path("/home/bjw-0/.cache/act-agent-v1")
    run_id = args.run_id or (
        f"{args.mode}-seed{args.seed}-steps{args.steps}-pairs{args.pair_limit}"
        f"-noise{round(args.noise_rate * 100):02d}"
    )
    receipt = train(
        mode=args.mode,
        seed=args.seed,
        max_steps=args.steps,
        pair_limit=args.pair_limit,
        accumulation=args.accumulation,
        sft_adapter=scratch / "checkpoints" / args.sft_run_id,
        pairs_path=scratch / "data/preference_tokens.parquet",
        model_manifest=Path("artifacts/model_source_manifest.json"),
        output_dir=scratch / "checkpoints" / run_id,
        receipt_path=Path("artifacts/training") / f"{run_id}.json",
        noise_rate=args.noise_rate,
    )
    print(json.dumps({k: v for k, v in receipt.items() if k != "losses"}, indent=2))


if __name__ == "__main__":
    main()
