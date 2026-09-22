"""Materialize valid scripted pair continuations for development preference pilots.

Only perturbations with directly observable effects are retained. These are
scripted negatives, not independent model rollouts or on-policy hard negatives.
"""

from __future__ import annotations

import json
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
from transformers import AutoTokenizer

from act_agent.data.pipeline import sha256
from act_agent.training.preprocess import tokenize_trace

SUPPORTED = {"missing_confirmation", "inefficient_success", "unsafe_success", "wrong_argument"}


def _action_index(messages: list[dict[str, Any]]) -> int | None:
    for index, message in enumerate(messages):
        if message.get("role") != "assistant" or not message.get("tool_calls"):
            continue
        name = message["tool_calls"][0]["function"]["name"]
        if name in {"change_bid", "change_budget", "change_targeting", "pause_campaign"}:
            return index
    return None


def perturb(messages: list[dict[str, Any]], kind: str) -> list[dict[str, Any]] | None:
    if kind not in SUPPORTED:
        return None
    out = deepcopy(messages)
    index = _action_index(out)
    if kind == "missing_confirmation":
        if index is None or out[index]["tool_calls"][0]["function"]["name"] != "change_budget":
            return None
        out = [
            message
            for message in out
            if message.get("content")
            not in {
                "Please confirm a local budget increase of 10 units.",
                "I confirm the local budget increase.",
            }
        ]
    elif kind == "inefficient_success":
        # The copied read result is only state-consistent if no mutation occurred.
        if index is not None:
            return None
        read = next(
            (
                i
                for i, message in enumerate(out)
                if message.get("role") == "assistant"
                and message.get("tool_calls")
                and message["tool_calls"][0]["function"]["name"] == "get_campaign"
            ),
            None,
        )
        if read is None:
            return None
        out[-1:-1] = deepcopy(out[read : read + 2])
    elif kind == "wrong_argument":
        if index is None:
            return None
        function = out[index]["tool_calls"][0]["function"]
        name = function["name"]
        if name == "pause_campaign":
            return None
        arguments = json.loads(function["arguments"])
        arguments["value"] = "invalid" if name == "change_targeting" else -10.0
        function["arguments"] = json.dumps(arguments, sort_keys=True)
        out[index + 1]["content"] = json.dumps({"error": "invalid_argument"})
        out[-1]["content"] = (
            "The requested local change failed validation. I made no claim of completion."
        )
    elif kind == "unsafe_success":
        if index is None:
            return None
        function = out[index]["tool_calls"][0]["function"]
        arguments = json.loads(function["arguments"])
        arguments["advertiser_id"] = "OTHER-ADVERTISER"
        out[-1:-1] = [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": function["name"],
                            "arguments": json.dumps(arguments, sort_keys=True),
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "name": function["name"],
                "content": json.dumps({"error": "advertiser scope violation"}),
            },
        ]
    return out


def materialize(
    pairs_path: Path,
    traces_path: Path,
    model_manifest: Path,
    output_path: Path,
    max_length: int = 1536,
) -> dict[str, Any]:
    pairs = pq.read_table(pairs_path).to_pylist()  # type: ignore[no-untyped-call]
    wanted = {row["task_id"] for row in pairs if row["negative_type"] in SUPPORTED}
    traces: dict[str, list[dict[str, Any]]] = {}
    with traces_path.open() as stream:
        for line in stream:
            trace = json.loads(line)
            if trace["task_id"] in wanted and trace["trajectory_variant"] == 0:
                traces[trace["task_id"]] = trace["messages"]
    manifest = json.loads(model_manifest.read_text())
    tokenizer = AutoTokenizer.from_pretrained(manifest["local_snapshot"], local_files_only=True)
    rows: list[dict[str, Any]] = []
    drop_reasons: Counter[str] = Counter()
    chosen_cache: dict[str, tuple[list[int], list[int]]] = {}
    for pair in pairs:
        kind = pair["negative_type"]
        if kind not in SUPPORTED:
            drop_reasons["unsupported_perturbation"] += 1
            continue
        chosen = traces.get(pair["task_id"])
        if chosen is None:
            drop_reasons["missing_trace"] += 1
            continue
        rejected = perturb(chosen, kind)
        if rejected is None:
            drop_reasons["inapplicable_perturbation"] += 1
            continue
        try:
            if pair["task_id"] not in chosen_cache:
                chosen_cache[pair["task_id"]] = tokenize_trace(tokenizer, chosen, max_length)
            chosen_ids, chosen_labels = chosen_cache[pair["task_id"]]
            rejected_ids, rejected_labels = tokenize_trace(tokenizer, rejected, max_length)
        except ValueError:
            drop_reasons["tokenization_or_length"] += 1
            continue
        rows.append(
            {
                "pair_id": pair["pair_id"],
                "task_id": pair["task_id"],
                "task_family": pair["task_family"],
                "negative_type": kind,
                "weight": pair["weight"],
                "margin": pair["margin"],
                "world_seed": pair["world_seed"],
                "chosen_ids": chosen_ids,
                "chosen_labels": chosen_labels,
                "rejected_ids": rejected_ids,
                "rejected_labels": rejected_labels,
                "chosen_assistant_tokens": sum(x != -100 for x in chosen_labels),
                "rejected_assistant_tokens": sum(x != -100 for x in rejected_labels),
            }
        )
    if not rows:
        raise ValueError("no materialized pairs")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), output_path)  # type: ignore[no-untyped-call]
    return {
        "source_pairs_sha256": sha256(pairs_path),
        "traces_sha256": sha256(traces_path),
        "output_sha256": sha256(output_path),
        "rows": len(rows),
        "drops": dict(drop_reasons),
        "negative_types": dict(Counter(r["negative_type"] for r in rows)),
        "max_length": max_length,
        "loss_mask": "assistant turns only",
        "status": "scripted development pairs; model/on-policy sources absent",
    }


if __name__ == "__main__":
    scratch = Path("/home/bjw-0/.cache/act-agent-v1/data")
    result = materialize(
        Path("artifacts/warehouse/preference_pairs.parquet"),
        scratch / "sft_train.jsonl",
        Path("artifacts/model_source_manifest.json"),
        scratch / "preference_tokens.parquet",
    )
    Path("artifacts/preference_token_manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
