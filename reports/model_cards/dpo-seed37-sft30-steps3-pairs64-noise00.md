# dpo-seed37-sft30-steps3-pairs64-noise00 model card

- Method: dpo; seed: 37; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': 'cab48fade8499a3612bc9fc3ac7f8b8fbd8cc02c4c21f7e404852e8356e5b287'}`.
- Adapter config SHA-256: `1762b95061a066f8bd2f2fbda742ca46d4189aa8c75ab969b073ee81e58c964b`.
- Training receipt: `artifacts/training/dpo-seed37-sft30-steps3-pairs64-noise00.json`.
- First and final recorded losses: 0.688837, 0.294223.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.0.
- Frozen SFT reference cache hash: `30084859d0022e60a9f9ce56135e66575586866d76c1f5dc6c1fad2c06bfce36`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.59 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
