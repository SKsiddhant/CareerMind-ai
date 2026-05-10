import os
import json
import asyncio
import google.generativeai as genai
from backend.rag_pipeline import RAGPipeline
from dotenv import load_dotenv
from fpdf import FPDF
from pypdf import PdfReader

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class ResumeTailor:
    """
    GOATed Phase 2 Agent: Ultra-precision resume tailoring and gap analysis.
    Now supports full AI-led reconstruction and ruthless audits with roadmaps.
    """
    def __init__(self, rag_pipeline=None):
        self.rag = rag_pipeline or RAGPipeline()
        self.model = genai.GenerativeModel('gemini-flash-latest')
        self.user_profile = {
            "name": "Siddhant Kothiya",
            "contact": "siddhant@example.com | San Francisco, CA",
            "skills": ["Python", "C++", "Kotlin", "Java", "RAG", "LangChain", "FineTuning", "Machine Learning", "Artificial Intelligence", "Android Development", "NLP", "Flask", "Scikit-Learn"],
            "projects": [
                {
                    "name": "SudokuXpert",
                    "tech": "Android, Java, Kotlin, XML",
                    "details": "Developed a high-performance Sudoku app with advanced solving algorithms."
                },
                {
                    "name": "AI Chatbot",
                    "tech": "Python, NLP, Flask",
                    "details": "Built a conversational AI using NLP techniques and Flask for deployment."
                },
                {
                    "name": "Fraud Detection",
                    "tech": "Python, Scikit-Learn, Streamlit",
                    "details": "Implemented machine learning models to detect financial fraud with high precision."
                }
            ],
            "experience": [
                {
                    "role": "SDE Intern",
                    "company": "Bluestock Fintech",
                    "details": "Engineered real-world fintech applications with a focus on performance and scalability."
                },
                {
                    "role": "Data Analyst Intern",
                    "company": "Zudio",
                    "details": "Conducted deep-dive analysis on sales trends and inventory management."
                }
            ]
        }

    async def analyze_resume(self, pdf_path):
        """
        Performs an Absolute Ruthless multi-dimensional audit AND reconstructs the profile.
        Gatekeeper Persona: Head of Talent at OpenAI.
        """
        print(f"💀 DEEP AUDIT & CATALYST ACTIVATED: {pdf_path}")
        
        # 1. Extract Text
        try:
            reader = PdfReader(pdf_path)
            resume_text = ""
            for page in reader.pages:
                resume_text += page.extract_text()
        except Exception as e:
            return {"error": f"Failed to parse PDF: {str(e)}"}

        # 2. THE INTENSIFIED RUTHLESS PROMPT
        prompt = f"""
        PERSONA: You are the Head of Talent and Lead Research Engineer at OpenAI. 
        TASK: Audit this resume ruthlessly. Tearing it down for mediocrity, then architecting a God-tier Catalyst Roadmap.

        RESUME TEXT:
        {resume_text}
        
        TASK 1 (DESTRUCTION): Identify fluff, generic claims, and shallow tech spots. Be brutal.
        
        TASK 2 (CATALYST): 
        - CRITICAL EDITS: Top 3 structural changes.
        - LEARNING ROADMAP: 3 Extreme technical topics to master (e.g. Distributed Training, CUDA).
        - RECOMMENDED PROJECTS: 2 God-tier project ideas that prove 0.1% capability.

        OUTPUT FORMAT (JSON):
        {{
            "overall_score": (1-10),
            "summary": "1-sentence lethal assessment",
            "anti_patterns": ["mediocre traits"],
            "mistakes": ["specific brutal critiques"],
            "critical_edits": ["immediate surgical changes"],
            "elite_rewrites": [
                {{ "original": "old", "rewrite": "God-tier version" }}
            ],
            "missing_skills": ["top-tier skills"],
            "learning_roadmap": [
                {{ "topic": "Complex Topic", "resources": "Specific high-level resources (papers/repo)" }}
            ],
            "recommended_projects": [
                {{ "name": "Project Name", "description": "High-complexity brief", "reasoning": "Why it fixes their profile" }}
            ],
            "reconstructed_profile": {{
                "name": "Name", "contact": "Info", "summary": "Elite Summary",
                "experience": [{{ "role": "R", "company": "C", "bullets": ["Elite Bullets"] }}],
                "projects": [{{ "name": "N", "tech": "T", "bullets": ["Elite Bullets"] }}],
                "skills": ["Optimized skills"]
            }},
            "formatting_critique": "Layout assessment"
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].strip()
            
            return json.loads(text)
        except Exception as e:
            print(f"Audit/Catalyst failed: {e}")
            return {"error": "Failed to generate deep insights."}

    def generate_reconstructed_pdf(self, profile):
        """Generates a professional PDF from a reconstructed profile."""
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", "B", 22)
        pdf.cell(0, 12, profile.get("name", "Candidate"), ln=True, align="C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, profile.get("contact", ""), ln=True, align="C")
        pdf.ln(5)

        # Summary
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "PROFESSIONAL SUMMARY", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 5, profile.get("summary", ""))
        pdf.ln(5)

        # Experience
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "TECHNICAL EXPERIENCE", ln=True)
        for exp in profile.get("experience", []):
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 8, f"{exp.get('role', '')} | {exp.get('company', '')}", ln=True)
            pdf.set_font("Arial", "", 10)
            for bullet in exp.get("bullets", []):
                pdf.multi_cell(0, 5, f"- {bullet}")
            pdf.ln(3)

        # Projects
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "TECHNICAL PROJECTS", ln=True)
        for proj in profile.get("projects", []):
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 8, f"{proj.get('name', '')} ({proj.get('tech', '')})", ln=True)
            pdf.set_font("Arial", "", 10)
            for bullet in proj.get("bullets", []):
                pdf.multi_cell(0, 5, f"- {bullet}")
            pdf.ln(3)

        # Skills
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "CORE COMPETENCIES", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 5, ", ".join(profile.get("skills", [])))
        
        safe_name = profile.get("name", "Edited").replace(" ", "_")
        filename = f"data/resumes/AI_RECONSTRUCTED_{safe_name}.pdf"
        os.makedirs("data/resumes", exist_ok=True)
        pdf.output(filename)
        return filename

    def generate_pdf_resume(self, tailored_bullets, job_title, company):
        """Generates a professional PDF resume tailored to a job."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 10, self.user_profile["name"], ln=True, align="C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, self.user_profile["contact"], ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Target Role: {job_title} at {company}", ln=True)
        pdf.set_line_width(0.5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Experience", ln=True)
        pdf.set_font("Arial", "", 10)
        for exp in self.user_profile["experience"]:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 8, f"{exp['role']} | {exp['company']}", ln=True)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 6, f"- {exp['details']}")
        pdf.ln(5)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 8, "Optimization for this role:", ln=True)
        pdf.set_font("Arial", "I", 10)
        for bullet in tailored_bullets[:3]:
            pdf.multi_cell(0, 6, f"* {bullet}")
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Technical Skills", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, ", ".join(self.user_profile["skills"]))
        filename = f"data/resumes/Tailored_Resume_{company.replace(' ', '_')}.pdf"
        os.makedirs("data/resumes", exist_ok=True)
        pdf.output(filename)
        return filename

    async def generate_elite_strategy(self, job_query="AI Engineer"):
        print(f"🎯 Generating elite strategy for {job_query}...")
        job_results = self.rag.query_jobs(job_query, k=2)
        context = json.dumps(job_results, indent=2)
        prompt = f"Generate Unfair Advantage strategy for {job_query}. Context: {context}. Return JSON list."
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception:
            return [{"error": "Failed"}]

if __name__ == "__main__":
    import asyncio
    async def test():
        tailor = ResumeTailor()
        res = await tailor.analyze_resume("RESUME_SIddhant 2 (1).pdf")
        print(json.dumps(res, indent=4))
    asyncio.run(test())
