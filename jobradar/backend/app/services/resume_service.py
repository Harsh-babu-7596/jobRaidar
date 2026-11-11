from __future__ import annotations

import io
import re
from collections import Counter

from app.services.keyword_lexicon import SKILL_PHRASES, STOPWORDS


def extract_text_from_bytes(filename: str, data: bytes) -> str:
    name = filename.lower()
    if name.endswith(".txt") or name.endswith(".md"):
        return data.decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        return _extract_pdf(data)
    if name.endswith(".docx"):
        return _extract_docx(data)
    raise ValueError("Unsupported resume format. Use PDF, DOCX, TXT, or MD.")


def _extract_pdf(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        parts.append(text)
    return "\n".join(parts)


def _extract_docx(data: bytes) -> str:
    from docx import Document

    document = Document(io.BytesIO(data))
    return "\n".join(p.text for p in document.paragraphs if p.text)


def normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_keywords(text: str, limit: int = 40) -> list[str]:
    """Pull skills from a resume using a curated lexicon + light heuristics."""
    cleaned = normalize_text(text)
    lowered = cleaned.lower()
    found: list[str] = []
    occupied = [False] * len(lowered)

    for phrase in SKILL_PHRASES:
        start = 0
        while True:
            idx = lowered.find(phrase, start)
            if idx < 0:
                break
            end = idx + len(phrase)
            # Prefer word-ish boundaries for short tokens.
            left_ok = idx == 0 or not lowered[idx - 1].isalnum()
            right_ok = end >= len(lowered) or not lowered[end].isalnum()
            if left_ok and right_ok and not any(occupied[idx:end]):
                found.append(_canonical(phrase))
                for i in range(idx, end):
                    occupied[i] = True
            start = end

    # Heuristic: CamelCase / dotted tech tokens not already covered.
    extras = re.findall(
        r"\b(?:[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+|[A-Za-z][A-Za-z0-9+#.]{2,})\b",
        cleaned,
    )
    counts = Counter()
    for token in extras:
        key = token.lower()
        if key in STOPWORDS or len(key) < 3:
            continue
        if any(key == f or key in f or f in key for f in (x.lower() for x in found)):
            continue
        if key in {p.lower() for p in SKILL_PHRASES}:
            counts[_canonical(key)] += 2
        elif token[:1].isupper() and any(ch.isupper() for ch in token[1:]):
            counts[token] += 1

    for token, _ in counts.most_common(12):
        if token.lower() not in {k.lower() for k in found}:
            found.append(token)

    # Preserve order, case-insensitive unique, capped.
    seen: set[str] = set()
    ordered: list[str] = []
    for item in found:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(item)
        if len(ordered) >= limit:
            break
    return ordered


def _canonical(phrase: str) -> str:
    aliases = {
        "nodejs": "Node.js",
        "node.js": "Node.js",
        "nextjs": "Next.js",
        "next.js": "Next.js",
        "golang": "Go",
        "postgres": "PostgreSQL",
        "postgresql": "PostgreSQL",
        "k8s": "Kubernetes",
        "ci/cd": "CI/CD",
        "fullstack": "Full Stack",
        "full stack": "Full Stack",
        "ml engineer": "ML Engineer",
        "machine learning engineer": "Machine Learning Engineer",
        "genai": "GenAI",
        "generative ai": "Generative AI",
        "rest api": "REST API",
        "react native": "React Native",
        "spring boot": "Spring Boot",
        "github actions": "GitHub Actions",
        "google cloud": "Google Cloud",
        "scikit-learn": "scikit-learn",
        "sklearn": "scikit-learn",
        ".net": ".NET",
        "dotnet": ".NET",
        "ui/ux": "UI/UX",
        "power bi": "Power BI",
    }
    return aliases.get(phrase.lower(), phrase.title() if " " in phrase else phrase)
