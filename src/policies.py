from functools import lru_cache
from pathlib import Path
import re
import unicodedata

from pypdf import PdfReader


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def normalize_text(value: str) -> str:
    value = value.lower().strip()

    normalized = unicodedata.normalize("NFKD", value)

    return "".join(
        char for char in normalized
        if not unicodedata.combining(char)
    )


def find_policy_pdf() -> Path:
    matches = list(DATA_DIR.glob("*políticas_da_loja.pdf"))

    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected exactly one policy PDF, but found {len(matches)}."
        )

    return matches[0]


@lru_cache(maxsize=1)
def load_policy_text() -> str:
    pdf_path = find_policy_pdf()

    reader = PdfReader(pdf_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""

        text = re.sub(r"\s+", " ", text)

        pages.append(text.strip())

    return "\n".join(pages)


def chunk_policy_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[str]:

    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def search_policies(
    query: str,
    top_k: int = 3,
) -> list[dict]:

    text = load_policy_text()

    chunks = chunk_policy_text(text)

    query_terms = {
        word
        for word in normalize_text(query).split()
        if len(word) > 2
    }

    scored_chunks = []

    for index, chunk in enumerate(chunks):
        normalized_chunk = normalize_text(chunk)

        score = sum(
            normalized_chunk.count(term)
            for term in query_terms
        )

        if score > 0:
            scored_chunks.append(
                {
                    "chunk_id": index,
                    "score": score,
                    "content": chunk,
                }
            )

    scored_chunks.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return scored_chunks[:top_k]