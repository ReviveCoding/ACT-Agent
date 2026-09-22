"""Verify public aggregate marts and split boundaries before model evaluation."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from act_agent.data.pipeline import sha256
from act_agent.tasks.generator import seed_for


def audit(root: Path) -> dict[str, Any]:
    profile = json.loads((root / "data/processed/profile.json").read_text())
    marts = {
        name: {
            "expected": item["sha256"],
            "actual": sha256(root / "data/processed" / f"{name}.parquet"),
        }
        for name, item in profile["marts"].items()
    }
    split_sizes = {
        "train": 3000,
        "calibration": 300,
        "development": 400,
        "pilot": 300,
        "id": 300,
        "composition": 250,
        "policy": 200,
        "tool": 200,
        "twin_b": 300,
        "security": 200,
    }
    seeds = {
        split: {seed_for(split, index) for index in range(size)}
        for split, size in split_sizes.items()
    }
    all_seeds = [seed for values in seeds.values() for seed in values]
    checks = {
        "mart_hashes_match": all(v["expected"] == v["actual"] for v in marts.values()),
        "seed_namespaces_disjoint": len(all_seeds) == len(set(all_seeds)),
        "raw_attribution_excluded_from_repository": not (
            root / "data/raw/criteo_attribution_dataset.tsv.gz"
        ).exists(),
        "raw_uplift_excluded_from_repository": not (
            root / "data/raw/criteo-research-uplift-v2.1.csv.gz"
        ).exists(),
    }
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "mart_hashes": marts,
        "split_sizes": split_sizes,
        "data_role": "public aggregate calibration; no public row-level model training",
        "protected_outcome_access": 0,
    }


if __name__ == "__main__":
    root = Path.cwd()
    result = audit(root)
    (root / "artifacts/data_leakage_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"], result["checks"])
    if result["status"] != "PASS":
        raise SystemExit(1)
