# dpo-seed11-steps3-pairs64-noise05 model card

- Method: dpo; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': 'fbef23ac01b42dc65b5159c684d44cf9dacb1a0372a00277e8dcd72a8f81c019'}`.
- Adapter config SHA-256: `073ee641790b90ff84558b1383ac3d5a41faffbe24bbd5db74fdd00308e8b756`.
- Training receipt: `artifacts/training/dpo-seed11-steps3-pairs64-noise05.json`.
- First and final recorded losses: 0.690150, 0.236947.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.05.
- Frozen SFT reference cache hash: `8152661bcba7f520ef65d0e4dc1273006bd77145d3f2c11d85513f397f1d55e6`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.16 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
