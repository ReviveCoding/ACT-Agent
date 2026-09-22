# dpo-seed11-steps3-pairs64-noise20 model card

- Method: dpo; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': 'db42e7f544907d6d3bdea3f0c528db608ee84f73fa81338e12895aef5368a6cb'}`.
- Adapter config SHA-256: `9307023decc3ea355eb9b0c6f3316a90440c1fefeaadfb09deb12f10de0c6118`.
- Training receipt: `artifacts/training/dpo-seed11-steps3-pairs64-noise20.json`.
- First and final recorded losses: 0.690150, 0.224908.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.2.
- Frozen SFT reference cache hash: `a362aeda7f48dc303834e2274f8e1a3b29319d0fb58f38d3af9a9ba30346d444`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.16 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
