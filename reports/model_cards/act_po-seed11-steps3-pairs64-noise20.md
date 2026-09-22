# act_po-seed11-steps3-pairs64-noise20 model card

- Method: act_po; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': 'dabbe1d5c0dd23201dcb566457ce38b694dcc52b3f92d50e311982d6e0525e20'}`.
- Adapter config SHA-256: `997995b9e6dbcdc51ca9ae4ef3ee6de22a0cbed542458faab3d1dc2e69a7d6ac`.
- Training receipt: `artifacts/training/act_po-seed11-steps3-pairs64-noise20.json`.
- First and final recorded losses: 0.596749, 0.199573.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.2.
- Frozen SFT reference cache hash: `a362aeda7f48dc303834e2274f8e1a3b29319d0fb58f38d3af9a9ba30346d444`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.35 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
