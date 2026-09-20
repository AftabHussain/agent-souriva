# LoRA and QLoRA SFT entry point

## Change

Added an optional supervised fine-tuning command for successful grounded traces, plus a validated example record.

## Architecture

Training stays outside the runtime package. Trace formatting defines the integration contract between collected agent runs and TRL, while PEFT supplies a LoRA adapter over the configured base model.

## Design notes

The command trains LoRA by default and enables 4-bit QLoRA explicitly. Required trace fields preserve the question, retrieved context, chosen action, grounded answer, and citations. Imports are lazy so runtime users do not load training libraries.

## Verification

Compiled the entry point, checked the diff, and added unit coverage for formatted action/citation content and incomplete trace rejection. A full GPT-OSS-20B training run was not executed because it requires separate model weights and accelerator resources.

## Result

`python -m training.sft data.jsonl` provides a focused path from successful traces to a saved LoRA adapter.
