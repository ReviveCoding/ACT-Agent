# ipo-seed11-steps3-pairs64-noise00 model card

- Method: ipo; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': '5cbc204097fd1962bbce22f8ed0f0511cea3a84538981221b76116150bcb3e6f'}`.
- Adapter config SHA-256: `f087e5bda66be46814af96d998cce224ef3f42f88b908d5094c661d26d7df6e3`.
- Training receipt: `artifacts/training/ipo-seed11-steps3-pairs64-noise00.json`.
- First and final recorded losses: 24.994955, 23.874367.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.0.
- Frozen SFT reference cache hash: `61f346683f3cd1054b1974e258d7cc3065814833f226da41f1f810bc099458f6`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.35 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
