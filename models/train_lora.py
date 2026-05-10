import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    pipeline
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

def train_lora_coach():
    """
    Main script for fine-tuning Mistral-7B using LoRA for interview evaluation.
    Note: Requires significant GPU VRAM (12GB+ for 4-bit, or use Colab/HuggingFace Spaces).
    """
    model_id = "mistralai/Mistral-7B-v0.1" # Using v0.1 as a base
    
    # 1. Loading tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # 2. 4-bit Quantization Config (to fit on standard GPUs)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )

    # 3. Load Base Model
    print(f"Loading base model: {model_id}...")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto"
    )
    model = prepare_model_for_kbit_training(model)

    # 4. LoRA Config
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"], # Fine-tune attention layers
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, peft_config)

    # 5. Load Dataset
    dataset = load_dataset("json", data_files="data/training/interview_dataset_structured.json", split="train")

    def formatting_prompts_func(example):
        output_texts = []
        for i in range(len(example['instruction'])):
            # Convert the structured JSON output back to a string for training
            structured_output = json.dumps(example['output'][i], indent=2)
            text = f"### Instruction: {example['instruction'][i]}\n### Input: {example['input'][i]}\n### Response: {structured_output}"
            output_texts.append(text)
        return output_texts

    # 6. Training Arguments
    training_args = TrainingArguments(
        output_dir="./models/interview-coach-lora",
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        logging_steps=10,
        max_steps=100, # Small test run
        fp16=True,
        save_total_limit=3,
        report_to="none"
    )

    # 7. Trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        max_seq_length=512,
        tokenizer=tokenizer,
        args=training_args,
        formatting_func=formatting_prompts_func,
    )

    print("Starting Training...")
    trainer.train()

    # 8. Save
    model.save_pretrained("./models/interview-coach-lora-final")
    print("Fine-tuning complete. Model saved to ./models/interview-coach-lora-final")

if __name__ == "__main__":
    # This script is a template for the actual training process.
    # In a local dev environment without a heavy GPU, it's recommended to run this on Google Colab.
    print("Initializing LoRA Fine-Tuning Pipeline...")
    # train_lora_coach() # Commented out to avoid crashing local environments without GPU
