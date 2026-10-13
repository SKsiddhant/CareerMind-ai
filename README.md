# CareerMind AI 🚀
### *The Most Advanced AI-Powered Career Acceleration Platform*

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-00D1FF?style=for-the-badge&logo=chroma&logoColor=white)](https://www.trychroma.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

CareerMind AI is a comprehensive, production-grade ecosystem designed to automate and optimize the entire job-seeking lifecycle. Unlike simple "GPT-wrappers," this platform features a sophisticated multi-agent system, a high-performance RAG pipeline, and real-time voice simulation.

---

## 🌟 Key Features

### 🤖 Multi-Agent Orchestration
Powered by **LangChain**, the system coordinates specialized agents to handle distinct phases of the career journey:
*   **Job Intelligence Agent:** Scans and analyzes live job postings using a custom Playwright-based scraper.
*   **Resume Tailor Agent:** Performs "ruthless" audits and generates optimized, ATS-friendly PDF resumes.
*   **Expert Interview Coach:** Provides deep evaluation of candidate answers based on relevance, clarity, and technical depth.
*   **Elite Salary Negotiator:** Crafts data-driven negotiation strategies to maximize compensation.

### 🔍 Advanced RAG Pipeline
Utilizes **ChromaDB** to index thousands of job descriptions and resumes, enabling:
*   Semantic search across local and scraped job listings.
*   Context-aware resume optimization.
*   Hyper-relevant interview question generation.

### 🎙️ Voice Interview Simulator
A real-time, end-to-end voice interface:
*   **STT (Whisper):** Transcribes spoken answers with high precision.
*   **AI Evaluation:** Gemini scores answers using a few-shot prompt built from the bundled dataset. (The LoRA training script in `models/` is included, but its output is not wired into the app.)
*   **TTS:** Reads follow-up questions back to the user for a fully immersive experience.

### 🧠 LoRA Fine-Tuning
Includes an (optional, GPU-only) training pipeline for **Mistral-7B** (via PEFT/LoRA). It is a standalone script: the running app calls Gemini, not the fine-tuned model. Install its extra dependencies with `pip install -r requirements-training.txt`.

### 🕵️ Autonomous Hunter
A 24/7 background worker that scouts for "elite" opportunities, filtering through noise to find the top 1% of jobs matching your profile.

---

## 🏗️ Architecture

The platform is built with a decoupled, micro-service-ready architecture:

*   **Frontend:** React 18 + TypeScript + Vite + Cyberpunk-inspired Vanilla CSS.
*   **Backend:** FastAPI (Python) + SQLAlchemy + Pydantic.
*   **Vector Database:** ChromaDB for semantic embeddings.
*   **Storage:** SQLite (local fallback) / PostgreSQL. (A Redis container is in `docker-compose.yml`, but nothing in the code uses it yet.)
*   **AI/ML:** OpenAI/Gemini API + Local Mistral-7B (Fine-tuned) + Whisper + TTS.

> Refer to `architecture.svg` for a detailed visual breakdown of the multi-agent design.

---

## 🚀 Getting Started

### 1. Prerequisites
*   Docker & Docker Compose
*   Node.js 18+ (for local development)
*   Python 3.10+ (for local development)

### 2. Using Docker (Recommended)
```bash
cp .env.example .env      # then set GOOGLE_API_KEY (and change POSTGRES_PASSWORD)
docker compose up --build
```
The first start downloads the Whisper and embedding models (several hundred MB; cached in a Docker volume afterwards).
If the app is not served from `http://localhost`, set `CORS_ORIGINS` and `VITE_API_URL` in `.env` (see `.env.example`).
The application will be available at:
*   **Frontend:** `http://localhost`
*   **Backend API:** `http://localhost:8002`
*   **API Docs:** `http://localhost:8002/docs`

### 3. Local Manual Setup

**Backend:**
```bash
cp .env.example .env      # set GOOGLE_API_KEY
pip install -r requirements.txt
playwright install chromium
uvicorn backend.main:app --port 8002
```

**Tests** (offline, no API key or model downloads):
```bash
pip install -r requirements-dev.txt
pytest
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 📅 Roadmap

- [x] **Phase 1-2:** RAG Pipeline + ChromaDB + Job Scraper
- [x] **Phase 3:** Expert Interview Coach + Structured Dataset
- [x] **Phase 4:** Voice Interview Simulator (Whisper + TTS)
- [x] **Phase 5:** LoRA Fine-Tuning on Mistral-7B
- [x] **Phase 8:** Production Persistence (PostgreSQL + SQLite Fallback)
- [x] **Phase 9:** Deployment & Dockerization
- [ ] **Phase 10:** Real-time Market Analytics Dashboard (Coming Soon)

---

## 🛠️ Technical Demonstration
This project showcases production-level AI engineering skills:
*   **Agentic Workflows:** Complex tool-use and state management.
*   **Vector Embeddings:** Efficient retrieval and semantic matching.
*   **Model Optimization:** Quantization (4-bit) and LoRA fine-tuning.
*   **Full-Stack DevOps:** Containerization, CI/CD readiness, and clean architecture.

---

## 📜 License
[MIT License](LICENSE) — Created by [Siddhant](https://github.com/SKsiddhant)
