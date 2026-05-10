# CareerMind AI

The most advanced AI-powered career acceleration platform.

## Project Roadmap Progress
- [x] **Phase 1-2:** RAG Pipeline + ChromaDB + Job Scraper
- [x] **Phase 3:** Expert Interview Coach + Structured Dataset
- [x] **Phase 4:** Voice Interview Simulator (Whisper + TTS)
- [x] **Phase 8:** Production Persistence (PostgreSQL + SQLite Fallback)
- [x] **Phase 9:** Deployment & Dockerization (Full Stack Orchestration)

## Project Architecture
Refer to `architecture.svg` for the full multi-agent system design.

## How to Run
### 1. Using Docker (Recommended)
Run the entire stack (Frontend, Backend, DB, Redis) with one command:
```bash
docker-compose up --build
```
Access the dashboard at `http://localhost`.

### 2. Local Manual Setup
1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
2. **Start Backend:**
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8002
   ```
3. **Start Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
