import os
import json
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class DatasetGenerator:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-flash-latest')
        self.topics = [
            "RAG Pipelines & Vector DBs",
            "LLM Fine-tuning (LoRA, PEFT)",
            "Distributed Systems & Microservices",
            "System Design & Scalability",
            "Python Concurrency (Asyncio, Multiprocessing)",
            "Cloud Infrastructure (AWS/GCP/Azure)",
            "MLOps & Model Deployment",
            "Data Engineering & ETL Pipelines",
            "Security & AI Safety",
            "Frontend for AI (React, Streamlit)"
        ]
        self.seniority_levels = ["Junior", "Mid-level", "Senior", "Principal"]

    async def generate_example(self):
        topic = os.urandom(1).hex() # Random seed for variety
        prompt = f"""
        You are a dataset generator for training an 'Elite Interview Coach' AI.
        Generate 2 highly detailed interview evaluation examples. 
        Each example must include:
        1. A realistic interview question related to these topics: {', '.join(self.topics)}.
        2. A candidate's answer (vary the quality: some poor, some mediocre, some excellent).
        3. A comprehensive evaluation in structured JSON format.
        
        The feedback MUST be hyper-technical, referencing specific architectures, papers, or industry standards.
        
        OUTPUT FORMAT (JSON List):
        [
          {{
            "instruction": "Evaluate this interview answer for a [Senior/Principal/Mid-level] [Role Name] role. Provide a structured evaluation.",
            "input": "Question: [Question]\\nAnswer: [Answer]",
            "output": {{
                "scores": {{
                    "technical_depth": (1-10),
                    "relevance": (1-10),
                    "clarity": (1-10)
                }},
                "total_score": (1-10),
                "feedback": "[Detailed, ruthless, technical feedback]",
                "star_method_compliance": "[Analysis of STAR method use]",
                "seniority_signal": "[One highly specific advanced concept to 'name-drop']",
                "curveball_question": "[The exact follow-up stress-test question]",
                "ideal_answer": "[A 3-4 sentence version of a perfect 10/10 answer]"
            }}
          }}
        ]
        Return ONLY valid JSON.
        """
        try:
            response = await self.model.generate_content_async(prompt)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].strip()
            return json.loads(text)
        except Exception as e:
            print(f"Error generating example: {e}")
            return []

    async def run(self, total_examples=50):
        print(f"🚀 Generating {total_examples} synthetic interview examples...")
        
        # Load existing examples if they exist
        all_examples = []
        if os.path.exists("data/training/interview_dataset.json"):
            with open("data/training/interview_dataset.json", "r") as f:
                all_examples = json.load(f)
        
        print(f"Existing examples: {len(all_examples)}")
        if len(all_examples) >= total_examples:
            print("✅ Already have enough examples.")
            return

        batch_size = 2 # Reduced batch size for stability
        while len(all_examples) < total_examples:
            tasks = [self.generate_example() for _ in range(batch_size)]
            results = await asyncio.gather(*tasks)
            
            new_additions = 0
            for res in results:
                if res:
                    all_examples.extend(res)
                    new_additions += len(res)
            
            # Intermediate save
            os.makedirs("data/training", exist_ok=True)
            with open("data/training/interview_dataset.json", "w") as f:
                json.dump(all_examples[:total_examples], f, indent=4)
            
            print(f"Progress: {len(all_examples)}/{total_examples} (+{new_additions})")
            
            if len(all_examples) < total_examples:
                print("Waiting 15 seconds to respect rate limits...")
                await asyncio.sleep(15)

        print(f"✅ Dataset generation complete. Total examples: {len(all_examples[:total_examples])}")

if __name__ == "__main__":
    generator = DatasetGenerator()
    asyncio.run(generator.run(60))
