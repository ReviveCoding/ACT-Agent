"""Run only with authorized GPU access; record a real CUDA computation."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import torch


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=Path("artifacts/e00_environment/cuda_probe.json")
    )
    args = parser.parse_args()
    probe = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,memory.free,driver_version,temperature.gpu,utilization.gpu",
            "--format=csv,noheader",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; no CPU fallback allowed")
    x = torch.randn((1024, 1024), device="cuda", dtype=torch.float32)
    y = x @ x
    torch.cuda.synchronize()
    result = {
        "timestamp": datetime.now(UTC).isoformat(),
        "device": torch.cuda.get_device_name(0),
        "nvidia_smi": probe.stdout.strip(),
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "cuda_available": True,
        "bf16_supported": torch.cuda.is_bf16_supported(),
        "vram_bytes": torch.cuda.get_device_properties(0).total_memory,
        "matmul_checksum": float(y.sum().item()),
        "compute_dtype": "float32",
    }
    path = args.output
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
