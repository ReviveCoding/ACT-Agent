"""Derive local adapter cards from completed, hash-verified training receipts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from act_agent.data.pipeline import sha256


def generate(root: Path, run_id: str) -> Path:
    receipt_path = root / "artifacts/training" / f"{run_id}.json"
    receipt: dict[str, Any] = json.loads(receipt_path.read_text())
    if receipt.get("status") != "PASS":
        raise ValueError("model card requires a completed training receipt")
    adapter_path = Path(receipt["adapter_path"])
    hashes = receipt["adapter_files_sha256"]
    if not hashes or any(
        not (adapter_path / name).is_file() or sha256(adapter_path / name) != digest
        for name, digest in hashes.items()
    ):
        raise ValueError("adapter hash mismatch")
    config_path = adapter_path / "adapter_config.json"
    if not config_path.is_file():
        raise ValueError("adapter config missing")
    config_hash = sha256(config_path)
    if receipt.get("adapter_config_sha256", config_hash) != config_hash:
        raise ValueError("adapter config hash mismatch")
    losses = receipt["losses"]
    model = receipt.get("mode", "SFT")
    steps = receipt.get("max_steps", receipt.get("steps"))
    lines = [
        f"# {run_id} model card",
        "",
        f"- Method: {model}; seed: {receipt['seed']}; optimizer steps: {steps}.",
        f"- Base model hash: `{receipt.get('model_hash', receipt.get('base_model_hash'))}`.",
        f"- Adapter file SHA-256: `{hashes}`.",
        f"- Adapter config SHA-256: `{config_hash}`.",
        f"- Training receipt: `artifacts/training/{run_id}.json`.",
        f"- First and final recorded losses: {losses[0]:.6f}, {losses[-1]:.6f}.",
    ]
    if "mode" in receipt:
        lines += [
            f"- Preference source hash: `{receipt['preference_tokens_sha256']}`.",
            f"- Pairs: {receipt['pair_limit']}; beta: {receipt['beta']}; label-flip rate: {receipt.get('noise_rate', 0.0)}.",
            f"- Frozen SFT reference cache hash: `{receipt['reference_sha256']}`.",
            "- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.",
        ]
    else:
        lines += [
            f"- SFT token source hash: `{receipt['tokens_sha256']}`.",
            f"- Gradient accumulation: {receipt['gradient_accumulation']}; LoRA rank: {receipt['lora_rank']}.",
            f"- Observed training throughput: {receipt['tokens_per_second']:.2f} input tokens per optimizer-step time second.",
        ]
    lines += [
        f"- Peak reserved VRAM: {receipt['peak_reserved_vram_bytes'] / 2**30:.2f} GiB.",
        "",
        "This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.",
        "",
    ]
    target = root / "reports/model_cards" / f"{run_id}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines))
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    args = parser.parse_args()
    print(generate(Path.cwd(), args.run_id))


if __name__ == "__main__":
    main()
