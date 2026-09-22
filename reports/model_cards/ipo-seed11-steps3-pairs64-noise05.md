# ipo-seed11-steps3-pairs64-noise05 model card

- Method: ipo; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': 'a22efe9cc574c0d43a32749af5db463934cb124e4c9a0319b9b225f717baa9b4'}`.
- Adapter config SHA-256: `5ed31c23f6f931138a8b5cefedd34a2436fa5679dd8bfd3eb1a93647516a236a`.
- Training receipt: `artifacts/training/ipo-seed11-steps3-pairs64-noise05.json`.
- First and final recorded losses: 24.994955, 23.898638.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.05.
- Frozen SFT reference cache hash: `8152661bcba7f520ef65d0e4dc1273006bd77145d3f2c11d85513f397f1d55e6`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.35 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
