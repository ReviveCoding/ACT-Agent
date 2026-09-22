# Frozen Qwen model card

Base: `Qwen/Qwen3-4B-Instruct-2507`, revision
`cdbee75f17c01a7cc42f958dc650907174af0554`, Apache-2.0. The exact
local snapshot and seven file hashes are in
`artifacts/model_source_manifest.json`. Selection occurred before protected
outcome access after the default hybrid snapshot could not be downloaded
reliably; no benchmark outcome influenced selection.

`artifacts/model_qualification.json` records a CUDA NF4/BF16 tool-call pilot
on the RTX 4090. The model produced a valid `get_campaign` call. The pilot
loaded in 23.10 seconds and used about 4.12 GB peak PyTorch reserved VRAM.
This is a local execution qualification, not task success, safety, or external
benchmark evidence. Adapter cards will be generated from training receipts
after those stages complete.
