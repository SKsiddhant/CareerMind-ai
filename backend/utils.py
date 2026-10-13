"""Small helpers shared by the API and the agents."""
import json
import os
import re
import uuid


def safe_slug(value, default="file", max_len=40):
    """Reduce arbitrary text (company names, LLM output, upload names) to [A-Za-z0-9_-].
    Anything that ends up in a file path must go through this: a value like '../../x' otherwise
    escapes the target directory."""
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", str(value or "")).strip("_")[:max_len]
    return slug or default


def unique_name(prefix, ext):
    """Collision-free file name, e.g. unique_name('resume', 'pdf') -> 'resume_3f9a1c2e4b7d.pdf'."""
    return f"{safe_slug(prefix)}_{uuid.uuid4().hex[:12]}.{ext.lstrip('.')}"


def pdf_text(value):
    """FPDF's built-in fonts only cover latin-1; LLM output routinely contains en dashes, bullets and
    curly quotes, which make fpdf2 raise. Map the common ones and drop what cannot be encoded."""
    text = str(value or "")
    for src, dst in {"–": "-", "—": "-", "‘": "'", "’": "'", "“": '"', "”": '"',
                     "•": "-", "…": "...", " ": " "}.items():
        text = text.replace(src, dst)
    return text.encode("latin-1", "ignore").decode("latin-1")


def extract_json(text):
    """Parse JSON from an LLM reply, tolerating ```json fences and surrounding prose."""
    text = (text or "").strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # fall back to the outermost {...} or [...] block
        for open_c, close_c in (("{", "}"), ("[", "]")):
            i, j = text.find(open_c), text.rfind(close_c)
            if 0 <= i < j:
                try:
                    return json.loads(text[i:j + 1])
                except json.JSONDecodeError:
                    pass
        raise


def ensure_dirs(*paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)
