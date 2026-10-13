import asyncio
import json
import os

import pytest
from pypdf import PdfReader

from conftest import FakeGeminiModel

from backend import utils


# ---------- helpers ----------

def test_safe_slug_blocks_path_traversal():
    assert "/" not in utils.safe_slug("../../etc/passwd")
    assert utils.safe_slug("..") == "file"
    assert utils.safe_slug("Acme & Sons, Inc.") == "Acme_Sons_Inc"


def test_unique_name_differs_every_call():
    assert utils.unique_name("a", "pdf") != utils.unique_name("a", "pdf")


def test_extract_json_handles_fences_and_prose():
    assert utils.extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert utils.extract_json('Sure! Here you go: {"a": 1} hope it helps') == {"a": 1}
    assert utils.extract_json('```\n[1, 2]\n```') == [1, 2]
    with pytest.raises(Exception):
        utils.extract_json("no json here")


# ---------- PDF generation (fpdf2 >= 2.7 broke repeated multi_cell calls) ----------

PROFILE = {
    "name": "../../Eve – O'Neil",
    "contact": "eve@example.com • Remote",
    "summary": "Built “fast” systems — at scale.",
    "experience": [{"role": "Engineer", "company": "Acme", "bullets": ["one", "two", "three …"]}],
    "projects": [{"name": "P", "tech": "Py", "bullets": ["a", "b"]}],
    "skills": ["Python", "SQL"],
}


def test_reconstructed_pdf_renders_many_bullets_and_unicode(app_env):
    main, work = app_env
    os.chdir(work)
    path = main.tailor_agent.generate_reconstructed_pdf(PROFILE)
    assert os.path.dirname(os.path.abspath(path)) == str(work / "data" / "resumes")
    text = "".join(p.extract_text() for p in PdfReader(path).pages)
    assert "three" in text and "SQL" in text


def test_reconstructed_pdf_names_do_not_collide(app_env):
    main, work = app_env
    os.chdir(work)
    a = main.tailor_agent.generate_reconstructed_pdf({"name": "Same"})
    b = main.tailor_agent.generate_reconstructed_pdf({"name": "Same"})
    assert a != b


def test_tailored_pdf_company_cannot_escape_directory(app_env):
    main, work = app_env
    os.chdir(work)
    path = main.tailor_agent.generate_pdf_resume(["x", "y", "z"], "Role", "../../../tmp/evil")
    assert os.path.dirname(os.path.abspath(path)) == str(work / "data" / "resumes")


# ---------- API ----------

def test_root(client):
    assert client.get("/").status_code == 200


def test_analyze_rejects_non_pdf(client):
    r = client.post("/tailor/analyze", files={"resume": ("cv.txt", b"hello", "text/plain")})
    assert r.status_code == 400


def test_analyze_ignores_client_filename_and_cleans_up(client, app_env):
    _, work = app_env
    FakeGeminiModel.reply = json.dumps({"overall_score": 5, "summary": "ok"})
    r = client.post("/tailor/analyze", files={"resume": ("../../../escape.pdf", b"%PDF-not-really", "application/pdf")})
    assert r.status_code == 200
    assert not (work.parent / "escape.pdf").exists() and not (work / "escape.pdf").exists()
    assert os.listdir(work / "data" / "uploads") == []  # temp upload removed even though parsing failed


def test_analyze_rejects_oversized_upload(client, app_env):
    _, work = app_env
    big = b"%PDF" + b"0" * (10 * 1024 * 1024 + 10)
    r = client.post("/tailor/analyze", files={"resume": ("big.pdf", big, "application/pdf")})
    assert r.status_code == 413
    assert os.listdir(work / "data" / "uploads") == []


def test_evaluate_unknown_user_is_404_not_500(client):
    FakeGeminiModel.reply = json.dumps({"total_score": 7})
    r = client.post("/interview/evaluate?user_id=999", json={"job_title": "t", "question": "q", "answer": "a"})
    assert r.status_code == 404


def test_evaluate_and_history_for_real_user(client):
    FakeGeminiModel.reply = '```json\n{"total_score": 7, "feedback": "fine"}\n```'
    uid = client.post("/users/", json={"name": "A", "email": "a@x.io", "profile_data": {}}).json()["user_id"]
    r = client.post(f"/interview/evaluate?user_id={uid}", json={"job_title": "t", "question": "q", "answer": "a"})
    assert r.json()["evaluation"]["total_score"] == 7
    assert len(client.get(f"/history/interviews/{uid}").json()) == 1


def test_voice_turn_cleans_up_and_returns_audio(client, app_env):
    _, work = app_env
    FakeGeminiModel.reply = json.dumps({"total_score": 8, "feedback": "good"})
    r = client.post("/interview/voice-turn", data={"job_title": "t", "question": "q"},
                    files={"audio": ("../../a.webm", b"abc", "audio/webm")})
    assert r.status_code == 200 and r.json()["audio_url"].startswith("/audio/")
    assert os.listdir(work / "data" / "uploads") == []


def test_generate_question_survives_tts_failure(client, app_env, monkeypatch):
    main, _ = app_env
    FakeGeminiModel.reply = "What is a mutex?"

    async def boom(*_a, **_k):
        raise RuntimeError("offline")
    monkeypatch.setattr(main.voice_simulator, "generate_speech", boom)
    r = client.get("/interview/generate-question", params={"job_title": "SWE"})
    assert r.status_code == 200 and r.json() == {"question": "What is a mutex?", "audio_url": None}


def test_generate_question_gemini_failure_is_502(client, app_env, monkeypatch):
    main, _ = app_env
    monkeypatch.setattr(main.interview_coach.model, "generate_content", lambda p: (_ for _ in ()).throw(RuntimeError("quota")))
    assert client.get("/interview/generate-question", params={"job_title": "SWE"}).status_code == 502


def test_hunter_cannot_be_started_twice(client, app_env, monkeypatch):
    main, _ = app_env
    started = []

    async def fake_hunt():
        started.append(1)
    monkeypatch.setattr(main.hunter, "start_infinite_hunt", fake_hunt)
    monkeypatch.setattr(main, "hunter_running", True)
    assert "already running" in client.post("/hunter/start").json()["message"]
    assert started == []
    monkeypatch.setattr(main, "hunter_running", False)
    client.post("/hunter/start")
    assert started == [1] and main.hunter_running is False  # flag is released when the hunt ends


def test_cors_only_allows_configured_origins(client):
    ok = client.options("/", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    evil = client.options("/", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in evil.headers


def test_strategy_tolerates_dict_reply(client):
    FakeGeminiModel.reply = json.dumps({"role": "SWE", "company": "Acme", "optimized_bullets": ["a"]})
    r = client.post("/tailor/strategy", json={"query": "swe"})
    assert r.status_code == 200 and r.json()["strategies"][0]["resume_url"].startswith("/resumes/")


# ---------- War Room ----------

def test_war_room_completes_even_if_model_omits_match_score(app_env):
    """Used to raise NameError (missing `import os`) and KeyError (match_score)."""
    main, work = app_env
    os.chdir(work)
    replies = iter([
        json.dumps({"optimized_bullets": ["b1", "b2"]}),            # base strategy
        json.dumps({"weaknesses": ["w"]}),                           # critique (no summary key)
        json.dumps({"optimized_bullets": ["b1+", "b2+"]}),           # refinement (no match_score)
        json.dumps({"estimated_compensation": {}}),                  # salary
    ])
    FakeGeminiModel.reply = None

    def fake(prompt):
        from conftest import FakeResponse
        return FakeResponse(next(replies))
    main.commander.tailor.model.generate_content = fake
    main.commander.coach.model.generate_content = fake
    main.commander.salary.model.generate_content = fake

    async def no_manager(*_a, **_k):
        return {"name": "Unknown Manager", "emails": []}
    main.commander.hiring.discover_manager = no_manager
    card = asyncio.run(main.commander.run_war_room("SWE", "Acme", "desc"))
    assert card["resume_url"].startswith("/resumes/")


# ---------- RAG indexing ----------

def test_index_skips_jobs_without_url_and_dedupes_ids(app_env, tmp_path):
    from backend.rag_pipeline import RAGPipeline
    rag = RAGPipeline(persist_directory=str(tmp_path / "chroma"))
    job = {"url": "https://x/1", "title": "T", "company": "C", "description": "word " * 300}
    path = tmp_path / "jobs.json"
    path.write_text(json.dumps([job, dict(job), {"title": "no url", "description": "d" * 300}]))
    rag.add_jobs_to_index(str(path))
    docs, ids = rag.vector_db.added[0]
    assert len(ids) == len(set(ids)) and all(i.startswith("https://x/1#chunk") for i in ids)


# ---------- hiring helper ----------

def test_company_domain_guess_keeps_ai_inside_names(app_env):
    from backend.hiring_intelligence import HiringIntelligence
    h = HiringIntelligence()
    assert h.get_domain("Airbnb") == "airbnb.com"
    assert h.get_domain("Foo AI") == "foo.com"
    assert h.get_domain("OpenAI") == "openai.com"
