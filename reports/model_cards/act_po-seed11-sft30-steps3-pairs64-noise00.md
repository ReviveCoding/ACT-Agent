# act_po-seed11-sft30-steps3-pairs64-noise00 model card

- Method: act_po; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': 'f0c229f6beeb847cbc0a76f2456cdce9f9822ea7160425e29d3bc1b1adeef8ce'}`.
- Adapter config SHA-256: `a91440458e5add808a8b96f808ca674167b2004ebdbecb90ee67a8c05d7d25e3`.
- Training receipt: `artifacts/training/act_po-seed11-sft30-steps3-pairs64-noise00.json`.
- First and final recorded losses: 0.606533, 0.056718.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.0.
- Frozen SFT reference cache hash: `430da0c08383b51af3befd0731d677c5750c277e520c8f997397ea7221ed10d6`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.35 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
