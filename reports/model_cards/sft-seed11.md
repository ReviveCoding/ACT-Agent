# sft-seed11 model card

- Method: SFT; seed: 11; optimizer steps: 120.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': '8d8fb9d7b95d3b4281834f9f349d6e54c13bf773e4d10cc5841ce660261183c7'}`.
- Adapter config SHA-256: `b2df95ec209a76448d717f4f1b915fa1f4b80bd90d8ee055ef77651ea587c961`.
- Training receipt: `artifacts/training/sft-seed11.json`.
- First and final recorded losses: 2.945455, 0.006391.
- SFT token source hash: `5a47e17e093218d671d8c04d0141f55036be2df969b83e359c809d10064f407e`.
- Gradient accumulation: 8; LoRA rank: 16.
- Observed training throughput: 107.82 input tokens per optimizer-step time second.
- Peak reserved VRAM: 7.20 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
