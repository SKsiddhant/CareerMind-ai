from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import asyncio
import os
import shutil

from backend.job_intelligence import JobIntelligence
from backend.resume_tailor import ResumeTailor
from backend.rag_pipeline import RAGPipeline
from backend.interview_coach import InterviewCoach
from backend.salary_negotiator import SalaryNegotiator
from backend.voice_simulator import VoiceInterviewSimulator
from backend.commander import CareerCommander
from backend.autonomous_hunter import AutonomousHunter
from backend.database import engine, get_db
from backend import models

app = FastAPI(title="CareerMind AI - GOATed Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs("data/audio", exist_ok=True)
os.makedirs("data/resumes", exist_ok=True)
os.makedirs("data/uploads", exist_ok=True)

# Serve static files
app.mount("/audio", StaticFiles(directory="data/audio"), name="audio")
app.mount("/resumes", StaticFiles(directory="data/resumes"), name="resumes")

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize Shared Components
rag_pipeline = RAGPipeline()

# Initialize Agents
job_agent = JobIntelligence(pipeline=rag_pipeline)
tailor_agent = ResumeTailor(rag_pipeline=rag_pipeline)
interview_coach = InterviewCoach(rag_pipeline=rag_pipeline)
salary_negotiator = SalaryNegotiator()
voice_simulator = VoiceInterviewSimulator(coach=interview_coach)
commander = CareerCommander(rag_pipeline=rag_pipeline)
hunter = AutonomousHunter()

# --- Models ---

class SearchRequest(BaseModel):
    query: str

class InterviewRequest(BaseModel):
    job_title: str
    question: str
    answer: str

class NegotiationRequest(BaseModel):
    company: str
    role: str
    match_score: int

class WarRoomRequest(BaseModel):
    job_title: str
    company: str
    job_content: str

class UserCreate(BaseModel):
    name: str
    email: str
    profile_data: dict

# --- Core Endpoints ---

@app.get("/")
async def root():
    return {"status": "GOATed", "message": "CareerMind AI Backend is live."}

# --- Autonomous Hunter ---

@app.post("/hunter/start")
async def start_hunter(background_tasks: BackgroundTasks):
    background_tasks.add_task(hunter.start_infinite_hunt)
    return {"message": "Autonomous Hunter deployed. Scouting for elite opportunities 24/7."}

@app.get("/hunter/elite-leads")
def get_elite_leads(db: Session = Depends(get_db)):
    leads = db.query(models.JobLead).filter(models.JobLead.is_elite == True).all()
    return leads

# --- War Room Orchestration ---

@app.post("/strategy/war-room")
async def activate_war_room(request: WarRoomRequest):
    battle_card = await commander.run_war_room(
        request.job_title, request.company, request.job_content
    )
    return battle_card

# --- Resume Analysis & Feedback ---

@app.post("/tailor/analyze")
async def analyze_resume(resume: UploadFile = File(...)):
    """
    Performs a ruthless audit AND generates a reconstructed AI-edited PDF.
    """
    temp_path = f"data/uploads/{resume.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)
    
    analysis = await tailor_agent.analyze_resume(temp_path)
    
    # 3. Generate Reconstructed PDF if possible
    reconstructed_url = None
    if "reconstructed_profile" in analysis:
        pdf_path = tailor_agent.generate_reconstructed_pdf(analysis["reconstructed_profile"])
        reconstructed_url = f"/resumes/{os.path.basename(pdf_path)}"
    
    analysis["reconstructed_resume_url"] = reconstructed_url

    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    return analysis

# --- Database Management ---

@app.post("/users/", response_model=dict)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        return {"message": "User already exists", "user_id": db_user.id}
    new_user = models.User(name=user.name, email=user.email, profile_data=user.profile_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created", "user_id": new_user.id}

@app.get("/history/interviews/{user_id}")
def get_interview_history(user_id: int, db: Session = Depends(get_db)):
    interviews = db.query(models.InterviewSession).filter(models.InterviewSession.user_id == user_id).all()
    return interviews

# --- Agent Endpoints ---

@app.post("/intelligence/gather")
async def gather_intelligence(request: SearchRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(job_agent.gather_intelligence, request.query)
    return {"message": f"Intelligence gathering started for '{request.query}'."}

@app.post("/tailor/strategy")
async def get_strategy(request: SearchRequest):
    strategies = await tailor_agent.generate_elite_strategy(request.query)
    for strategy in strategies:
        if "error" not in strategy:
            pdf_path = tailor_agent.generate_pdf_resume(
                strategy["optimized_bullets"], strategy["role"], strategy["company"]
            )
            strategy["resume_url"] = f"/resumes/{os.path.basename(pdf_path)}"
    return {"strategies": strategies}

@app.get("/jobs/search")
async def search_jobs(query: str, k: int = 5):
    results = rag_pipeline.query_jobs(query, k=k)
    return {"results": results}

@app.post("/interview/evaluate")
async def evaluate_interview(request: InterviewRequest, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    evaluation = await interview_coach.evaluate_answer(
        request.job_title, request.question, request.answer
    )
    if user_id:
        session = models.InterviewSession(
            user_id=user_id, question=request.question, answer=request.answer, evaluation=evaluation
        )
        db.add(session)
        db.commit()
    return {"evaluation": evaluation}

@app.post("/interview/voice-turn")
async def voice_turn(
    job_title: str = Form(...),
    question: str = Form(...),
    audio: UploadFile = File(...),
    user_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    temp_path = f"data/audio/temp_{audio.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
    
    evaluation, tts_path = await voice_simulator.process_voice_turn(temp_path, job_title, question)
    audio_url = f"/audio/{os.path.basename(tts_path)}" if tts_path else None
    
    if user_id:
        session = models.InterviewSession(
            user_id=user_id, question=question, answer="[Voice Answer]", 
            evaluation=evaluation, audio_path=audio_url
        )
        db.add(session)
        db.commit()

    if os.path.exists(temp_path):
        os.remove(temp_path)
    return {"evaluation": evaluation, "audio_url": audio_url}

@app.get("/interview/generate-question")
async def generate_question(job_title: str):
    context = rag_pipeline.query_jobs(job_title, k=1)
    context_text = context[0]['content'] if context else "Standard technical requirements."
    prompt = f"Based on this job context: {context_text}, generate ONE ruthless, technical interview question for a {job_title} role. Return ONLY the question text."
    response = interview_coach.model.generate_content(prompt)
    question_text = response.text.strip()
    tts_filename = f"question_{asyncio.get_event_loop().time()}.mp3"
    tts_path = os.path.join("data", "audio", tts_filename)
    await voice_simulator.generate_speech(question_text, tts_path)
    return {"question": question_text, "audio_url": f"/audio/{tts_filename}"}

@app.post("/salary/negotiate")
async def negotiate_salary(request: NegotiationRequest):
    strategy = await salary_negotiator.generate_negotiation_strategy(
        request.company, request.role, request.match_score
    )
    return {"strategy": strategy}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
