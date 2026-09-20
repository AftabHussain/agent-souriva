import argparse
import json
from pathlib import Path


REQUIRED_FIELDS = {"question", "retrieved_context", "desired_action", "grounded_answer", "citations"}


def format_trace(trace: dict) -> str:
    missing = REQUIRED_FIELDS - trace.keys()
    if missing:
        raise ValueError(f"Training trace missing fields: {', '.join(sorted(missing))}")
    context = trace["retrieved_context"]
    if isinstance(context, list):
        context = "\n\n".join(context)
    citations = " ".join(f"[{item}]" for item in trace["citations"])
    return (
        "<|user|>\n"
        f"Question: {trace['question']}\nEvidence:\n{context}\n"
        "<|assistant|>\n"
        f"Action: {trace['desired_action']}\n{trace['grounded_answer']} {citations}".strip()
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="LoRA/QLoRA SFT over grounded agent traces")
    parser.add_argument("data", type=Path, help="JSONL file containing successful grounded traces")
    parser.add_argument("--model", default="openai/gpt-oss-20b")
    parser.add_argument("--output", type=Path, default=Path("artifacts/sft-v1"))
    parser.add_argument("--qlora", action="store_true", help="load the base model in 4-bit mode")
    args = parser.parse_args()

    from datasets import Dataset
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from trl import SFTConfig, SFTTrainer

    records = [json.loads(line) for line in args.data.read_text(encoding="utf-8").splitlines() if line]
    dataset = Dataset.from_dict({"text": [format_trace(record) for record in records]})
    quantization = BitsAndBytesConfig(load_in_4bit=True) if args.qlora else None
    model = AutoModelForCausalLM.from_pretrained(args.model, quantization_config=quantization)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, target_modules="all-linear")
    config = SFTConfig(output_dir=str(args.output), dataset_text_field="text", num_train_epochs=1)
    trainer = SFTTrainer(model=model, args=config, train_dataset=dataset, tokenizer=tokenizer, peft_config=lora)
    trainer.train()
    trainer.save_model()


if __name__ == "__main__":
    main()

