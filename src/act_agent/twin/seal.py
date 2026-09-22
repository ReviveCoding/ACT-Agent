"""Pre-protected Twin-B source and mechanism seal."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from act_agent.data.pipeline import sha256

MECHANISM = {
    "auction_response": "logistic bid minus 1.3 times competition, slope 2.0",
    "opportunity": "0.75 plus 0.25 sin(timestamp/6)",
    "click_response": "0.85 plus 0.1 sin(timestamp/8)",
    "conversion_multiplier": 0.75,
    "noise": "same state-keyed PRNG namespace with variant B",
    "seed_namespace": "B",
}


def seal(source: Path, calibration: Path) -> dict[str, Any]:
    canonical = json.dumps(MECHANISM, sort_keys=True, separators=(",", ":")).encode()
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "protocol": "act-v1-20260920",
        "source_sha256": sha256(source),
        "calibration_sha256": sha256(calibration),
        "parameter_sha256": hashlib.sha256(canonical).hexdigest(),
        "seed_namespace": "B",
        "access_count": 0,
        "status": "SEALED_PRE_PROTECTED",
        "boundary": "No Twin-B model selection or protected transfer outcomes accessed.",
    }


if __name__ == "__main__":
    result = seal(Path("src/act_agent/twin/core.py"), Path("configs/twin_a_calibration.json"))
    Path("artifacts/twin_b_seal.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result)
