"""Assistant-only Qwen SFT tokenization with explicit loss masks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
from transformers import AutoTokenizer

from act_agent.data.pipeline import sha256


def tokenize_trace(
    tokenizer: Any, messages: list[dict[str, Any]], max_length: int
) -> tuple[list[int], list[int]]:
    full: list[int] = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=False
    )
    if len(full) > max_length:
        raise ValueError(f"trace length {len(full)} exceeds frozen cap {max_length}")
    labels = [-100] * len(full)
    previous: list[int] = []
    for index, message in enumerate(messages):
        prefix: list[int] = tokenizer.apply_chat_template(
            messages[: index + 1], tokenize=True, add_generation_prompt=False
        )
        if prefix[: len(previous)] != previous or full[: len(prefix)] != prefix:
            raise ValueError("chat template prefixes are not stable")
        if message["role"] == "assistant":
            labels[len(previous) : len(prefix)] = full[len(previous) : len(prefix)]
        previous = prefix
    if not any(label != -100 for label in labels):
        raise ValueError("no assistant target tokens")
    return full, labels


def preprocess(
    source: Path, destination: Path, model_manifest: Path, max_length: int = 1536
) -> dict[str, Any]:
    manifest = json.loads(model_manifest.read_text())
    tokenizer = AutoTokenizer.from_pretrained(manifest["local_snapshot"], local_files_only=True)
    rows = []
    with source.open() as stream:
        for line in stream:
            trace = json.loads(line)
            if trace["split"] != "train":
                raise ValueError("nontraining trace in SFT data")
            ids, labels = tokenize_trace(tokenizer, trace["messages"], max_length)
            rows.append(
                {
                    "task_id": trace["task_id"],
                    "trajectory_variant": trace["trajectory_variant"],
                    "input_ids": ids,
                    "labels": labels,
                    "length": len(ids),
                    "assistant_tokens": sum(label != -100 for label in labels),
                }
            )
    destination.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), destination)  # type: ignore[no-untyped-call]
    return {
        "source_sha256": sha256(source),
        "output_sha256": sha256(destination),
        "model_hash": manifest["model_hash"],
        "tokenizer_sha256": manifest["files_sha256"]["tokenizer.json"],
        "rows": len(rows),
        "min_length": min(r["length"] for r in rows),
        "max_length": max(r["length"] for r in rows),
        "assistant_token_total": sum(r["assistant_tokens"] for r in rows),
        "max_length_cap": max_length,
        "loss_mask": "assistant turns only",
        "split": "train",
    }


if __name__ == "__main__":
    source = Path("/home/bjw-0/.cache/act-agent-v1/data/sft_train.jsonl")
    destination = Path("/home/bjw-0/.cache/act-agent-v1/data/sft_tokens.parquet")
    result = preprocess(source, destination, Path("artifacts/model_source_manifest.json"))
    Path("artifacts/sft_token_manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result)
