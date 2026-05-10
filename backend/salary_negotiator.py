import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class SalaryNegotiator:
    """
    Exceptional Feature Agent: Predicts real-time market salary bands and generates 
    ruthless negotiation scripts based on the user's specific skill gaps and match score.
    """
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-flash-latest')

    async def generate_negotiation_strategy(self, company, role, match_score, user_name="Siddhant Kothiya"):
        """
        Generates compensation predictions and negotiation scripts.
        """
        print(f"💰 Generating Negotiation Strategy for {role} at {company}...")

        prompt = f"""
        You are a highly sought-after Tech Salary Negotiator and former Recruiter at {company}.
        Your client, {user_name}, is applying for the role of '{role}' at '{company}'.
        Their technical match score for this specific role is {match_score}/100.
        
        TASK:
        1. ESTIMATED COMPENSATION: Based on current Silicon Valley / Top Tech trends for a '{role}' at '{company}', predict the exact compensation band (Base, Equity, Bonus).
        2. LEVERAGE ANALYSIS: Give the 'brutal truth' on the candidate's leverage based on their match score ({match_score}/100). Are they in a position of power, or do they need to prove themselves?
        3. THE NEGOTIATION SCRIPT: Write the exact email/spoken script the candidate should use when the recruiter asks "What are your salary expectations?". This script MUST be psychological and strategic, deflecting the first number and anchoring to market value.
        4. COUNTER-OFFER SCRIPT: Write the script for when the initial offer is 10% lower than expected.

        OUTPUT FORMAT (JSON):
        {{
            "estimated_compensation": {{
                "base_salary": "$XXXk - $YYYk",
                "equity_stock": "$XXXk (over 4 years)",
                "sign_on_bonus": "$XXk"
            }},
            "leverage_analysis": "",
            "initial_script": "",
            "counter_offer_script": ""
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].strip()
            
            strategy = json.loads(text)
            return strategy
        except Exception as e:
            print(f"Negotiation generation failed: {e}")
            return {"error": str(e)}

async def main():
    negotiator = SalaryNegotiator()
    result = await negotiator.generate_negotiation_strategy("OpenAI", "AI Engineer", 88)
    print("\n--- Negotiation Strategy ---")
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
