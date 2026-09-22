# sft-seed37-steps30 model card

- Method: SFT; seed: 37; optimizer steps: 30.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': 'e11d9c297672d50dce5209bb7df70087649e175f359fad67804dd3a0a4b16a73'}`.
- Adapter config SHA-256: `357a0c836ff599f736c941277eefa39e3fa969087ac399e6076dfdf81aab9f99`.
- Training receipt: `artifacts/training/sft-seed37-steps30.json`.
- First and final recorded losses: 2.862683, 0.023841.
- SFT token source hash: `5a47e17e093218d671d8c04d0141f55036be2df969b83e359c809d10064f407e`.
- Gradient accumulation: 8; LoRA rank: 16.
- Observed training throughput: 124.76 input tokens per optimizer-step time second.
- Peak reserved VRAM: 7.18 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
