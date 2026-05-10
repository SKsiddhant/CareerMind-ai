import os
import json
import google.generativeai as genai
from backend.rag_pipeline import RAGPipeline
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class InterviewCoach:
    """
    Phase 3: Specialist Agent for evaluating interview answers.
    Uses RAG to get job context and Gemini (acting as our fine-tuned Mistral) for evaluation.
    """
    def __init__(self, rag_pipeline=None):
        self.rag = rag_pipeline or RAGPipeline()
        self.model = genai.GenerativeModel('gemini-flash-latest')
        self.examples = self._load_examples()

    def _load_examples(self):
        """Loads a subset of structured examples for few-shot prompting."""
        try:
            path = "data/training/interview_dataset_structured.json"
            if os.path.exists(path):
                with open(path, "r") as f:
                    data = json.load(f)
                    # Use a few high-quality examples (e.g., scores 9 or 10)
                    return [ex for ex in data if ex['output']['total_score'] >= 9][:2]
        except Exception as e:
            print(f"Failed to load examples: {e}")
        return []

    async def evaluate_answer(self, job_title, question, user_answer):
        """
        Evaluates a user's answer against a specific job's context.
        Uses few-shot examples to simulate a fine-tuned expert model.
        """
        print(f"🎬 Evaluating answer for {job_title}...")
        
        # 1. Get Job Context from RAG
        job_context = self.rag.query_jobs(job_title, k=1)
        context_text = job_context[0]['content'] if job_context else "Standard AI Engineering requirements."

        # 2. Build Few-Shot Examples String
        few_shot_str = ""
        for ex in self.examples:
            few_shot_str += f"### Instruction: {ex['instruction']}\n"
            few_shot_str += f"### Input: {ex['input']}\n"
            few_shot_str += f"### Response: {json.dumps(ex['output'], indent=2)}\n\n"

        # 3. Evaluation Prompt
        prompt = f"""
        You are a Principal Engineer and Hiring Committee Member at a Tier-1 Tech Company (like OpenAI or Google).
        You are known for conducting the most rigorous, high-bar technical interviews.
        
        {few_shot_str}

        ### CURRENT INTERVIEW CONTEXT:
        JOB CONTEXT:
        {context_text}
        
        ### EVALUATION TASK:
        INSTRUCTION: Evaluate this interview answer for a {job_title} role. Provide a structured evaluation.
        INPUT: 
        Question: {question}
        Answer: {user_answer}

        ### GUIDELINES:
        - Be RUTHLESS. If the answer is surface-level, give a low score (3-5).
        - RELEVANCE: Ensure the answer addresses the specific Job Context provided.
        - SENIORITY SIGNAL: Provide a 'cheat code' concept (e.g., a specific paper or obscure optimization) that would instantly signal seniority.
        - CURVEBALL: Ask a follow-up that would expose a candidate with shallow knowledge.
        
        OUTPUT FORMAT (JSON):
        {{
            "scores": {{
                "technical_depth": 0,
                "relevance": 0,
                "clarity": 0
            }},
            "total_score": 0,
            "feedback": "",
            "mistakes": ["List specific technical or logical errors made"],
            "corrections": ["Specific architectural or conceptual corrections for each mistake"],
            "star_method_compliance": "",
            "seniority_signal": "",
            "curveball_question": "",
            "ideal_answer": ""
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].strip()
            
            evaluation = json.loads(text)
            return evaluation
        except Exception as e:
            print(f"Evaluation failed: {e}")
            return {
                "scores": {"technical_depth": 0, "relevance": 0, "clarity": 0},
                "total_score": 0,
                "feedback": f"Evaluation error: {str(e)}",
                "mistakes": ["N/A"],
                "corrections": ["N/A"],
                "star_method_compliance": "N/A",
                "seniority_signal": "N/A",
                "curveball_question": "N/A",
                "ideal_answer": "N/A"
            }

async def main():
    coach = InterviewCoach()
    test_q = "How would you design a system to handle hallucinations in a RAG pipeline?"
    test_a = "I'd use a small model to check if the answer is in the documents."
    
    result = await coach.evaluate_answer("AI Engineer", test_q, test_a)
    print("\n--- Interview Evaluation Results ---")
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
