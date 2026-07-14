import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import chromadb
from chromadb.utils import embedding_functions

LOGGER = logging.getLogger(__name__)

# -----------------------------
# Paths
# -----------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

PAGES_DIR = BASE_DIR / "data" / "pages"
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "juit_knowledge_v2"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

CHUNK_TARGET_CHARS = 3500
CHUNK_MAX_CHARS = 5000
CHUNK_OVERLAP_CHARS = 200
MIN_CHUNK_CHARS = 80

GENERIC_TITLES = {
    "",
    "home",
    "index",
    "untitled",
    "welcome",
    "juit",
}

PAGE_TYPE_KEYWORDS = [
    ("admissions", ["admission", "admissions", "eligibility"]),
    ("fees", ["fee", "fees", "hostel charges"]),
    ("academic_calendar", ["academic calendar"]),
    ("curriculum", ["curriculum", "syllabus", "course curriculum"]),
    ("faculty", ["faculty"]),
    ("staff", ["staff", "technical staff"]),
    ("committee", ["committee", "cell", "grievance"]),
    ("notices", ["notice", "notices", "circular"]),
    ("placements", ["placement", "placements"]),
    ("public_disclosure", ["disclosure", "nirf", "naac", "rti"]),
    ("library", ["library", "lrc"]),
    ("publications", ["publication", "publications"]),
    ("events", ["event", "workshop", "webinar", "conference"]),
    ("alumni", ["alumni"]),
]

DEPARTMENT_KEYWORDS = [
    ("cse_it", ["cse", "computer science", "information technology", "cse-it"]),
    ("ece", ["ece", "electronics", "communication"]),
    ("civil", ["civil"]),
    ("biotech_bioinformatics", ["biotechnology", "bioinformatics", "bi bt", "bi-bt"]),
    ("mathematics", ["maths", "mathematics"]),
    ("physics_materials_science", ["physics", "materials science", "pms"]),
    ("hss", ["hss", "humanities", "social sciences"]),
    ("library", ["library", "lrc"]),
]


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def canonicalize_url(url: str) -> str:
    url = clean_text(url).replace("%20", "")
    parts = urlsplit(url)

    netloc = parts.netloc.lower()
    if parts.scheme == "https" and netloc.endswith(":443"):
        netloc = netloc[:-4]

    path = parts.path.replace("%20", "")
    if path != "/":
        path = path.rstrip("/")

    return urlunsplit(
        (
            parts.scheme.lower(),
            netloc,
            path,
            parts.query,
            "",
        )
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def title_from_url(url: str) -> str:
    path = urlsplit(url).path.strip("/")
    slug = path.split("/")[-1] if path else ""
    slug = re.sub(r"[-_]+", " ", slug.replace("%20", ""))
    return slug.title() if slug else "Untitled"


def normalize_title(title: str, url: str) -> str:
    title = clean_text(title)
    title = re.sub(
        r"\s*[-|]\s*(JUIT|Jaypee University Of Information Technology)\s*$",
        "",
        title,
        flags=re.IGNORECASE,
    ).strip()

    if title.lower() in GENERIC_TITLES:
        return title_from_url(url)

    return title


def classify_page_type(url: str, title: str, content: str) -> str:
    haystack = f"{url} {title} {content[:1000]}".lower()

    for page_type, keywords in PAGE_TYPE_KEYWORDS:
        if any(keyword in haystack for keyword in keywords):
            return page_type

    if any(keyword in haystack for keyword in ["department", "programmes", "laboratories"]):
        return "department"

    return "general"


def detect_department(url: str, title: str, content: str) -> str:
    haystack = f"{url} {title} {content[:1000]}".lower()

    for department, keywords in DEPARTMENT_KEYWORDS:
        if any(keyword in haystack for keyword in keywords):
            return department

    return "central"


def priority_for_page(page_type: str) -> int:
    if page_type in {"admissions", "fees", "academic_calendar", "curriculum"}:
        return 100
    if page_type == "public_disclosure":
        return 90
    if page_type in {"department", "faculty", "staff", "committee", "placements"}:
        return 80
    if page_type == "library":
        return 70
    if page_type in {"publications", "events"}:
        return 50
    if page_type == "alumni":
        return 30
    return 60


def chunk_type_for_text(text: str) -> str:
    lowered = text.lower()

    if re.search(r"[\w.-]+@[\w.-]+", text) or re.search(r"\+?\d[\d\s-]{7,}", text):
        return "contact"
    if any(word in lowered for word in ["fee", "tuition", "hostel charges"]):
        return "fees"
    if any(word in lowered for word in ["notice", "circular", "dated"]):
        return "notice"
    if any(word in lowered for word in ["faculty", "professor", "assistant professor"]):
        return "faculty"
    if any(word in lowered for word in ["publication", "journal", "conference"]):
        return "publication"

    return "section"


def split_sentences(text: str) -> list[str]:
    text = clean_text(text)
    if not text:
        return []

    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text)
        if sentence.strip()
    ]


def split_long_text(text: str) -> list[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_MAX_CHARS, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = max(end - CHUNK_OVERLAP_CHARS, start + 1)

    return chunks


def build_chunks(content: str) -> list[str]:
    sentences = split_sentences(content)

    if not sentences:
        return []

    chunks = []
    current = ""

    for sentence in sentences:
        if len(sentence) > CHUNK_MAX_CHARS:
            if current:
                chunks.append(current.strip())
                current = ""

            chunks.extend(split_long_text(sentence))
            continue

        candidate = f"{current} {sentence}".strip()

        if len(candidate) <= CHUNK_TARGET_CHARS:
            current = candidate
            continue

        if current:
            chunks.append(current.strip())

        current = sentence

    if current:
        chunks.append(current.strip())

    filtered_chunks = []
    for chunk in chunks:
        if len(chunk) >= MIN_CHUNK_CHARS or chunk_type_for_text(chunk) == "contact":
            filtered_chunks.append(chunk)

    return filtered_chunks


def document_text(title: str, canonical_url: str, chunk: str) -> str:
    return clean_text(
        f"Title: {title}\n"
        f"URL: {canonical_url}\n\n"
        f"{chunk}"
    )


def build_chunk_id(page_id: str, chunk_index: int, chunk_hash: str) -> str:
    return f"ingest_v2:{page_id[:16]}:{chunk_index}:{chunk_hash[:16]}"


def load_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function
    )


def delete_existing_page_chunks(collection, url: str, canonical_url: str) -> None:
    for where in (
        {"url": url},
        {"url": canonical_url},
        {"canonical_url": canonical_url},
    ):
        try:
            collection.delete(where=where)
        except Exception:
            pass


def ingest_file(file_path: Path, collection, ingested_at: str) -> int:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    raw_url = clean_text(data.get("url", ""))
    canonical_url = canonicalize_url(raw_url)
    title = normalize_title(data.get("title", ""), canonical_url)
    content = clean_text(data.get("content", ""))

    if not canonical_url or not title or not content:
        LOGGER.info("Skipping page with missing required fields: %s", file_path.name)
        return 0

    content_hash = sha256_text(content)
    page_id = sha256_text(canonical_url)
    page_type = classify_page_type(canonical_url, title, content)
    department = detect_department(canonical_url, title, content)
    priority = priority_for_page(page_type)
    chunks = build_chunks(content)

    if not chunks:
        LOGGER.info("Skipping page with no usable chunks: %s", file_path.name)
        return 0

    delete_existing_page_chunks(collection, raw_url, canonical_url)

    documents = []
    ids = []
    metadatas = []
    chunk_count = len(chunks)

    for chunk_index, chunk in enumerate(chunks):
        chunk_hash = sha256_text(chunk)
        chunk_id = build_chunk_id(page_id, chunk_index, chunk_hash)

        documents.append(document_text(title, canonical_url, chunk))
        ids.append(chunk_id)
        metadatas.append(
            {
                "schema_version": "ingest_v2",
                "source_type": "html",
                "source_file": file_path.name,
                "url": canonical_url,
                "canonical_url": canonical_url,
                "title": title,
                "page_id": page_id,
                "page_type": page_type,
                "department": department,
                "chunk": chunk_index,
                "chunk_index": chunk_index,
                "chunk_count": chunk_count,
                "chunk_id": chunk_id,
                "chunk_type": chunk_type_for_text(chunk),
                "section": "",
                "content_hash": content_hash,
                "chunk_hash": chunk_hash,
                "content_chars": len(content),
                "chunk_chars": len(chunk),
                "ingested_at": ingested_at,
                "priority": priority,
                "has_email": bool(re.search(r"[\w.-]+@[\w.-]+", chunk)),
                "has_phone": bool(re.search(r"\+?\d[\d\s-]{7,}", chunk)),
            }
        )

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    LOGGER.info("Upserted %s chunks from %s", len(documents), file_path.name)
    return len(documents)


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    collection = load_collection()
    files = sorted(PAGES_DIR.glob("*.json"))
    ingested_at = datetime.now(timezone.utc).isoformat()

    LOGGER.info("Found %s files", len(files))

    total_chunks = 0
    failed_files = 0

    for file_path in files:
        try:
            total_chunks += ingest_file(file_path, collection, ingested_at)
        except Exception:
            failed_files += 1
            LOGGER.exception("Failed to ingest %s", file_path.name)

    LOGGER.info("Ingestion complete")
    LOGGER.info("Chunks upserted: %s", total_chunks)
    LOGGER.info("Failed files: %s", failed_files)


if __name__ == "__main__":
    main()
