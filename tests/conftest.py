"""Offline tests. Heavy / networked dependencies (Gemini, Whisper, Chroma, Playwright, DuckDuckGo, embedding
models) are replaced by light fakes before the backend is imported, so the suite needs only
fastapi, sqlalchemy, fpdf2, pypdf, httpx and pytest - no API keys, GPU or model downloads."""
import os
import sys
import types

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)


def _module(name, **attrs):
    m = types.ModuleType(name)
    m.__dict__.update(attrs)
    sys.modules[name] = m
    return m


class FakeResponse:
    def __init__(self, text):
        self.text = text


class FakeGeminiModel:
    """Returns whatever the test put in `FakeGeminiModel.reply`."""
    reply = "{}"
    calls = []

    def __init__(self, *_a, **_k):
        pass

    def generate_content(self, prompt):
        FakeGeminiModel.calls.append(prompt)
        return FakeResponse(FakeGeminiModel.reply)


class FakeChroma:
    def __init__(self, *_a, **_k):
        self.added = []

    def add_documents(self, documents, ids):
        if len(set(ids)) != len(ids):
            raise ValueError("DuplicateIDError")  # what real Chroma does
        self.added.append((documents, ids))

    def similarity_search(self, *_a, **_k):
        return []


class FakeSearch:
    def run(self, _q):
        return ""


def install_fakes():
    genai = _module("google.generativeai", configure=lambda **k: None, GenerativeModel=FakeGeminiModel)
    google = sys.modules.get("google") or _module("google")
    google.generativeai = genai
    sys.modules["google"] = google
    _module("whisper", load_model=lambda name: types.SimpleNamespace(transcribe=lambda p: {"text": "my answer"}))

    async def _save(self, path):
        open(path, "wb").write(b"mp3")
    _module("edge_tts", Communicate=type("Communicate", (), {"__init__": lambda s, t, v: None, "save": _save}))
    _module("sentence_transformers", CrossEncoder=lambda *a, **k: types.SimpleNamespace(predict=lambda pairs: [0.9] * len(pairs)))
    _module("langchain_huggingface", HuggingFaceEmbeddings=lambda **k: object())
    _module("langchain_chroma", Chroma=FakeChroma)
    _module("langchain_community")
    _module("langchain_community.tools", DuckDuckGoSearchRun=FakeSearch)
    _module("playwright")
    _module("playwright.async_api", async_playwright=lambda: None)


install_fakes()


@pytest.fixture(scope="session")
def app_env(tmp_path_factory):
    """Import the FastAPI app once, from inside a scratch working directory (it creates ./data and a SQLite file)."""
    work = tmp_path_factory.mktemp("work")
    os.makedirs(work / "data", exist_ok=True)
    old = os.getcwd()
    os.chdir(work)
    try:
        from backend import main
        yield main, work
    finally:
        os.chdir(old)


@pytest.fixture
def client(app_env):
    from fastapi.testclient import TestClient
    main, work = app_env
    os.chdir(work)
    with TestClient(main.app) as c:
        yield c


@pytest.fixture(autouse=True)
def _reset_gemini():
    FakeGeminiModel.reply, FakeGeminiModel.calls = "{}", []
