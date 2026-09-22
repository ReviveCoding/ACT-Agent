# sft-seed23-steps30 model card

- Method: SFT; seed: 23; optimizer steps: 30.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': 'cace370fdb03aa8301da5ad2d81c6aa22eaa2696bd4ba5ca81afbd3a20a8659e'}`.
- Adapter config SHA-256: `acba503784df6ab6fa37e38a9e2bd069e30460f2c925817d357d30b81a8a3ad4`.
- Training receipt: `artifacts/training/sft-seed23-steps30.json`.
- First and final recorded losses: 2.854064, 0.039094.
- SFT token source hash: `5a47e17e093218d671d8c04d0141f55036be2df969b83e359c809d10064f407e`.
- Gradient accumulation: 8; LoRA rank: 16.
- Observed training throughput: 130.92 input tokens per optimizer-step time second.
- Peak reserved VRAM: 7.14 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
