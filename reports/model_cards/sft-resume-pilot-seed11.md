# sft-resume-pilot-seed11 model card

- Method: SFT; seed: 11; optimizer steps: 4.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': 'fd7a895e953b8e93ac7b41da4d0158a9e6e72c5fd1a1a503f06614f32cca9977'}`.
- Adapter config SHA-256: `a28a98d67f00e62811e1c0d76cb7a1b9c13183cc4c35f36cf8904587f9b95b0e`.
- Training receipt: `artifacts/training/sft-resume-pilot-seed11.json`.
- First and final recorded losses: 3.077254, 1.116136.
- SFT token source hash: `5a47e17e093218d671d8c04d0141f55036be2df969b83e359c809d10064f407e`.
- Gradient accumulation: 2; LoRA rank: 16.
- Observed training throughput: 122.22 input tokens per optimizer-step time second.
- Peak reserved VRAM: 6.81 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
