# act_po-seed11-steps3-pairs64-noise10 model card

- Method: act_po; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': 'c6453c3a096f29ece54570c9b841334e1c002928ced7dcc8cdbac327ef772ea7'}`.
- Adapter config SHA-256: `c87a71ef7d69f7bf9f7813ce89786eda8c4b98b2fc2bff7f3bf8108a4a6927fc`.
- Training receipt: `artifacts/training/act_po-seed11-steps3-pairs64-noise10.json`.
- First and final recorded losses: 0.596749, 0.202511.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.1.
- Frozen SFT reference cache hash: `01fb9a0d5142d1ac60669d1ece5196764f77b3af519e0222ba9a118bfb3fae29`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.35 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
