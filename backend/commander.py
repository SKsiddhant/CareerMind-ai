import asyncio
import json
from backend.job_intelligence import JobIntelligence
from backend.resume_tailor import ResumeTailor
from backend.interview_coach import InterviewCoach
from backend.salary_negotiator import SalaryNegotiator
from backend.hiring_intelligence import HiringIntelligence

class CareerCommander:
    """
    The Ultimate Orchestrator. Coordinates the 'War Room' protocol.
    Agents debate and refine the strategy autonomously.
    """
    def __init__(self, rag_pipeline=None):
        self.tailor = ResumeTailor(rag_pipeline=rag_pipeline)
        self.coach = InterviewCoach(rag_pipeline=rag_pipeline)
        self.hiring = HiringIntelligence()
        self.salary = SalaryNegotiator()

    async def run_war_room(self, job_title, company, job_content):
        """
        Executes the 'Battle Plan' protocol:
        1. OSINT: Find the Manager.
        2. Draft: Generate initial resume strategy.
        3. Critique: Coach reviews the strategy for 'ruthlessness'.
        4. Refine: Tailor adjusts based on Coach's feedback.
        5. Finalize: Generate Battle Card (PDF, Scripts, Negotiation).
        """
        print(f"🚩 WAR ROOM ACTIVATED: {job_title} at {company}")
        
        # Step 1: Human Intel (Parallel with initial draft)
        intel_task = asyncio.create_task(self.hiring.discover_manager(company, job_title))
        
        # Step 2: Initial Draft
        print("Agent [ResumeTailor]: Generating initial unfair advantage...")
        # We simulate the multi-step strategy here
        initial_strategy = await self._generate_base_strategy(job_title, company, job_content)
        
        # Step 3: The Critique (Agentic Feedback Loop)
        print("Agent [InterviewCoach]: Critiquing strategy for technical depth...")
        critique = await self._critique_strategy(initial_strategy, job_content)
        
        # Step 4: The Refinement
        print("Agent [ResumeTailor]: Refining based on Coach's critique...")
        final_strategy = await self._refine_strategy(initial_strategy, critique)
        
        # Step 5: Wrap it up
        hiring_manager = await intel_task
        
        battle_card = {
            "job": {"title": job_title, "company": company},
            "hiring_manager": hiring_manager,
            "strategy": final_strategy,
            "negotiation": await self.salary.generate_negotiation_strategy(company, job_title, final_strategy['match_score']),
            "war_room_log": [
                {"agent": "ResumeTailor", "action": "Generated initial strategy"},
                {"agent": "InterviewCoach", "action": f"Critique: {critique['summary']}"},
                {"agent": "ResumeTailor", "action": "Applied refinements for maximum impact"}
            ]
        }
        
        # Generate the final PDF with the REFINED bullets
        pdf_path = self.tailor.generate_pdf_resume(
            final_strategy["optimized_bullets"], 
            job_title, 
            company
        )
        battle_card["resume_url"] = f"/resumes/{os.path.basename(pdf_path)}"
        
        return battle_card

    async def _generate_base_strategy(self, title, company, content):
        # Simplified for internal logic
        prompt = f"Generate an 'Unfair Advantage' strategy for {title} at {company}. Context: {content}. Return JSON."
        response = self.tailor.model.generate_content(prompt)
        text = response.text
        if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
        return json.loads(text)

    async def _critique_strategy(self, strategy, job_content):
        prompt = f"""
        You are a Ruthless Hiring Manager. Critique this application strategy:
        {json.dumps(strategy)}
        
        Job Requirements: {job_content}
        
        TASK: Identify 2 weak points in the 'optimized_bullets'. Are they too generic? Do they lack specific metrics?
        Return JSON with keys: "weaknesses" (list), "summary" (string).
        """
        response = self.coach.model.generate_content(prompt)
        text = response.text
        if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
        return json.loads(text)

    async def _refine_strategy(self, strategy, critique):
        prompt = f"""
        Refine this strategy based on the critique:
        Original: {json.dumps(strategy)}
        Critique: {json.dumps(critique)}
        
        TASK: Rewrite the 'optimized_bullets' to address the weaknesses. Make them punchier and more metric-driven.
        Return the FULL updated strategy object as JSON.
        """
        response = self.tailor.model.generate_content(prompt)
        text = response.text
        if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
        return json.loads(text)
