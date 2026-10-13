from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import asyncio
import os
import logging

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
from backend.utils import unique_name

logger = logging.getLogger("careermind")

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # resumes / short voice answers; larger bodies are rejected with 413

app = FastAPI(title="CareerMind AI - GOATed Backend")

# Add CORS middleware. Allowed origins come from CORS_ORIGINS (comma separated); the defaults cover the
# Vite dev server and the docker-compose frontend.
CORS_ORIGINS = [o.strip() for o in (
    os.getenv("CORS_ORIGINS") or "http://localhost:5173,http://127.0.0.1:5173,http://localhost,http://127.0.0.1"
).split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,  # no cookies are used; credentialed wildcard CORS would let any site call the API as the user
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

# --- Helpers ---

def save_upload(upload: UploadFile, directory: str, prefix: str, ext: str) -> str:
    """Stream an upload to a server-chosen filename (never the client's), enforcing a size cap.
    Using upload.filename directly allowed '../' paths to write outside the target folder."""
    path = os.path.join(directory, unique_name(prefix, ext))
    written = 0
    with open(path, "wb") as buffer:
        while chunk := upload.file.read(1024 * 1024):
            written += len(chunk)
            if written > MAX_UPLOAD_BYTES:
                buffer.close()
                os.remove(path)
                raise HTTPException(status_code=413, detail="File too large (limit 10 MB).")
            buffer.write(chunk)
    return path


def remove_quietly(path):
    try:
        os.remove(path)
    except OSError:
        pass


def require_user(db: Session, user_id: Optional[int]):
    """Reject a user_id that does not exist: it would otherwise fail later as a foreign-key 500."""
    if user_id is not None and db.get(models.User, user_id) is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")


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

hunter_running = False


async def _run_hunter():
    global hunter_running
    try:
        await hunter.start_infinite_hunt()
    finally:
        hunter_running = False


@app.post("/hunter/start")
async def start_hunter(background_tasks: BackgroundTasks):
    # Every call used to start another endless loop, so clicking the button twice doubled the scraping.
    global hunter_running
    if hunter_running:
        return {"message": "Autonomous Hunter is already running."}
    hunter_running = True
    background_tasks.add_task(_run_hunter)
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
    if not (resume.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF resume.")
    temp_path = save_upload(resume, "data/uploads", "resume", "pdf")
    try:
        analysis = await tailor_agent.analyze_resume(temp_path)

        # Generate Reconstructed PDF if possible
        reconstructed_url = None
        if isinstance(analysis.get("reconstructed_profile"), dict):
            try:
                pdf_path = tailor_agent.generate_reconstructed_pdf(analysis["reconstructed_profile"])
                reconstructed_url = f"/resumes/{os.path.basename(pdf_path)}"
            except Exception:
                logger.exception("Could not render the reconstructed resume PDF")
        analysis["reconstructed_resume_url"] = reconstructed_url
        return analysis
    finally:
        remove_quietly(temp_path)  # also on errors; the upload used to be left behind

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
        if isinstance(strategy, dict) and "error" not in strategy:
            try:
                pdf_path = tailor_agent.generate_pdf_resume(
                    strategy.get("optimized_bullets", []), strategy.get("role", request.query), strategy.get("company", "company")
                )
                strategy["resume_url"] = f"/resumes/{os.path.basename(pdf_path)}"
            except Exception:
                logger.exception("Could not render the tailored resume PDF")
    return {"strategies": strategies}

@app.get("/jobs/search")
async def search_jobs(query: str, k: int = 5):
    results = rag_pipeline.query_jobs(query, k=k)
    return {"results": results}

@app.post("/interview/evaluate")
async def evaluate_interview(request: InterviewRequest, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    require_user(db, user_id)
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
    require_user(db, user_id)
    ext = os.path.splitext(audio.filename or "")[1].lstrip(".").lower()
    temp_path = save_upload(audio, "data/uploads", "voice", ext if ext.isalnum() and len(ext) <= 5 else "webm")
    try:
        evaluation, tts_path = await voice_simulator.process_voice_turn(temp_path, job_title, question)
        audio_url = f"/audio/{os.path.basename(tts_path)}" if tts_path else None

        if user_id:
            session = models.InterviewSession(
                user_id=user_id, question=question, answer="[Voice Answer]",
                evaluation=evaluation, audio_path=audio_url
            )
            db.add(session)
            db.commit()
        return {"evaluation": evaluation, "audio_url": audio_url}
    finally:
        remove_quietly(temp_path)

@app.get("/interview/generate-question")
async def generate_question(job_title: str):
    context = rag_pipeline.query_jobs(job_title, k=1)
    context_text = context[0]['content'] if context else "Standard technical requirements."
    prompt = f"Based on this job context: {context_text}, generate ONE ruthless, technical interview question for a {job_title} role. Return ONLY the question text."
    try:
        response = await asyncio.to_thread(interview_coach.model.generate_content, prompt)  # don't block the event loop
        question_text = response.text.strip()
    except Exception:
        logger.exception("Question generation failed")
        raise HTTPException(status_code=502, detail="The AI service could not generate a question. Check GOOGLE_API_KEY and try again.")
    tts_filename = unique_name("question", "mp3")
    tts_path = os.path.join("data", "audio", tts_filename)
    audio_url = None
    try:
        await voice_simulator.generate_speech(question_text, tts_path)
        audio_url = f"/audio/{tts_filename}"
    except Exception:
        logger.exception("Text-to-speech failed; returning the question without audio")  # TTS needs internet access
    return {"question": question_text, "audio_url": audio_url}

@app.post("/salary/negotiate")
async def negotiate_salary(request: NegotiationRequest):
    strategy = await salary_negotiator.generate_negotiation_strategy(
        request.company, request.role, request.match_score
    )
    return {"strategy": strategy}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8002")))
