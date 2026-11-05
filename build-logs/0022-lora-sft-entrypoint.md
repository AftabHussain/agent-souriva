## LoRA and QLoRA SFT entry point

**Source commit:** [`19ed186`](https://github.com/AftabHussain/agent-souriva/commit/19ed186616d84164deea4f945ee72d6295a5fa31)

### Change

Added an optional supervised fine-tuning command for successful grounded traces, plus a validated example record.

The training entry point constructs a parameter-efficient LoRA adapter and passes it to `SFTTrainer` from Hugging Face’s Transformer Reinforcement Learning (TRL) library:

    lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05,
                      target_modules="all-linear")
    config = SFTConfig(output_dir=str(args.output),
                       dataset_text_field="text", num_train_epochs=1)
    trainer = SFTTrainer(model=model, args=config,
                         train_dataset=dataset, tokenizer=tokenizer,
                         peft_config=lora)
    trainer.train()

Only the LoRA parameters are trained over validated trace text, keeping adaptation separate from the serving-time runtime.

### Architecture

Training stays outside the runtime package. Trace formatting defines the integration contract between collected agent runs and TRL, while PEFT supplies a LoRA adapter over the configured base model.

### Design notes

The command trains LoRA by default and enables 4-bit QLoRA explicitly. Required trace fields preserve the question, retrieved context, chosen action, grounded answer, and citations. Imports are lazy so runtime users do not load training libraries.

### Verification

Compiled the entry point, checked the diff, and added unit coverage for formatted action/citation content and incomplete trace rejection. A full GPT-OSS-20B training run was not executed because it requires separate model weights and accelerator resources.

### Result

`python -m training.sft data.jsonl` provides a focused path from successful traces to a saved LoRA adapter.
