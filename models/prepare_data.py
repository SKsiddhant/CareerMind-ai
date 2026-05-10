import json
import os

def generate_synthetic_dataset():
    """
    Generates a high-quality synthetic dataset for fine-tuning the Interview Coach.
    Format: {"instruction": "...", "input": "...", "output": "..."}
    """
    dataset = [
        {
            "instruction": "Evaluate this interview answer for a Senior AI Engineer role. Score from 1-10 and provide feedback.",
            "input": "Question: How do you handle hallucinations in RAG systems?\nAnswer: I just increase the top-k and hope for the best.",
            "output": "Score: 2/10. Feedback: This answer shows a lack of technical depth. Increasing top-k often increases noise and can actually worsen hallucinations. Better methods include prompt engineering (Chain-of-Thought), adding a validation step with an NLI model, or using self-correction loops."
        },
        {
            "instruction": "Evaluate this interview answer for a Senior AI Engineer role. Score from 1-10 and provide feedback.",
            "input": "Question: How do you handle hallucinations in RAG systems?\nAnswer: I implement a multi-stage validation pipeline. First, I use Citations to ensure the model only answers based on provided context. Second, I use an NLI (Natural Language Inference) model to verify the 'entailment' between the context and the answer. Finally, I use self-critique prompts where the LLM reviews its own response for factual consistency.",
            "output": "Score: 9/10. Feedback: Excellent. This answer demonstrates a sophisticated understanding of RAG reliability. You've covered factual grounding, external verification, and agentic self-correction."
        },
        {
            "instruction": "Evaluate this interview answer for a Software Engineer role. Score from 1-10 and provide feedback.",
            "input": "Question: Explain the difference between a process and a thread.\nAnswer: They are basically the same thing but threads are smaller.",
            "output": "Score: 3/10. Feedback: Too vague. While threads are 'lighter', the critical difference is memory sharing. Processes have independent memory spaces, while threads within a process share the same memory heap. This is vital for concurrency and safety."
        },
        {
            "instruction": "Evaluate this interview answer for an AI Research role. Score from 1-10 and provide feedback.",
            "input": "Question: What is the core intuition behind LoRA fine-tuning?\nAnswer: LoRA assumes that the weight updates during fine-tuning have a low 'intrinsic rank'. Instead of updating the full weight matrix W, we represent the update as the product of two smaller, low-rank matrices A and B. This drastically reduces the number of trainable parameters.",
            "output": "Score: 10/10. Feedback: Perfect explanation of the 'Intrinsic Dimension' hypothesis and the mathematical implementation. Demonstrates deep theoretical knowledge."
        }
    ]

    # Add more diverse examples here...
    
    os.makedirs("data/training", exist_ok=True)
    with open("data/training/interview_dataset.json", "w") as f:
        json.dump(dataset, f, indent=4)
    print(f"Generated {len(dataset)} synthetic training examples at data/training/interview_dataset.json")

if __name__ == "__main__":
    generate_synthetic_dataset()
