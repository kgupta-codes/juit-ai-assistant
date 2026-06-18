import re
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = BASE_DIR / "chroma_db"

CHROMA_CANDIDATES = 20

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

embedding_function = (
    embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
)

collection = client.get_collection(
    name="juit_knowledge_v2",
    embedding_function=embedding_function
)

# University-specific acronym expansion
ACRONYMS = {
    "CE": "Civil Engineering",
    "CSE": "Computer Science Engineering",
    "ECE": "Electronics and Communication Engineering",
    "IT": "Information Technology",
    "TNP": "Training and Placement",
    "CESEDM": "Centre for Structural Engineering and Disaster Management",
    "CESTRD": "Centre of Sustainable Technologies for Rural Development",
    "CEC": "Civil Engineering Consortium",
    "JYC": "JUIT Youth Club",
    "ICC": "Internal Complaint Committee",
    "NSS": "National Service Scheme",
    "NCC": "National Cadet Corps",
}

FILLER_PHRASES = [
    "what is",
    "what are",
    "tell me about",
    "explain",
    "give details about",
    "information about",
    "details about",
]

TITLE_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "about",
    "for",
    "in",
    "is",
    "me",
    "of",
    "on",
    "the",
    "to",
    "what",
}

COMMITTEE_TERMS = {
    "anti",
    "committee",
    "committees",
    "cell",
    "cells",
    "drug",
    "grievance",
    "ragging",
    "ethics",
    "complaint",
    "complaints",
    "discipline",
}


def _normalize_text(text: str) -> str:
    text = text or ""
    text = text.lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_query(query: str) -> str:
    normalized = _normalize_text(query)

    for phrase in FILLER_PHRASES:
        normalized = normalized.replace(phrase, " ")

    return re.sub(r"\s+", " ", normalized).strip()


def expand_query(query: str) -> str:
    expanded_parts = [query]
    padded_query = f" {query} "

    for acronym, expansion in ACRONYMS.items():
        normalized_acronym = acronym.lower()
        normalized_expansion = _normalize_text(expansion)

        if f" {normalized_acronym} " in padded_query:
            expanded_parts.append(normalized_expansion)
            continue

        if normalized_expansion in query:
            expanded_parts.append(normalized_acronym)

    return " ".join(dict.fromkeys(expanded_parts))


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in _normalize_text(text).split()
        if token and token not in TITLE_STOPWORDS
    }


def _exact_phrases(query: str) -> list[str]:
    words = [
        token
        for token in query.split()
        if token not in TITLE_STOPWORDS
    ]

    phrases = []

    for size in (4, 3, 2):
        for index in range(0, len(words) - size + 1):
            phrases.append(" ".join(words[index:index + size]))

    return phrases


def _semantic_score(distance) -> float:
    if distance is None:
        return 0.0

    return 1.0 / (1.0 + float(distance))


def _title_boost(query_tokens: set[str], title: str) -> float:
    title_tokens = _tokens(title)

    if not title_tokens:
        return 0.0

    overlap = query_tokens & title_tokens
    boost = 0.35 * len(overlap)

    if title_tokens.issubset(query_tokens):
        boost += 0.75

    if query_tokens and len(overlap) / len(title_tokens) >= 0.5:
        boost += 0.35

    return boost


def _exact_phrase_boost(phrases: list[str], title: str, document: str) -> float:
    haystack = f"{_normalize_text(title)} {_normalize_text(document)}"
    boost = 0.0

    for phrase in phrases:
        if phrase in haystack:
            boost += 0.45

    return min(boost, 1.8)


def _committee_boost(query_tokens: set[str], title: str, document: str, metadata: dict) -> float:
    if not (query_tokens & COMMITTEE_TERMS):
        return 0.0

    title_text = _normalize_text(title)
    document_text = _normalize_text(document)
    page_type = _normalize_text(metadata.get("page_type", ""))

    boost = 0.0

    if "committee" in title_text or "committees" in title_text:
        boost += 1.2

    if page_type == "committee":
        boost += 1.0

    if "committee" in document_text:
        boost += 0.4

    committee_overlap = (query_tokens & COMMITTEE_TERMS) & _tokens(document_text)
    boost += 0.25 * len(committee_overlap)

    if "anti drug" in document_text or "anti drug" in title_text:
        boost += 0.9

    if page_type == "events":
        boost -= 0.7

    return boost


def _rank_candidate(query: str, document: str, metadata: dict, distance) -> float:
    title = metadata.get("title", "")
    query_tokens = _tokens(query)
    phrases = _exact_phrases(query)

    score = _semantic_score(distance)
    score += _title_boost(query_tokens, title)
    score += _exact_phrase_boost(phrases, title, document)
    score += _committee_boost(query_tokens, title, document, metadata)

    return score


def _dedupe_key(metadata: dict) -> str:
    title = _normalize_text(metadata.get("title", ""))

    if title:
        return title

    return _normalize_text(metadata.get("canonical_url") or metadata.get("url") or "")


def _rerank(results: dict, query: str, n_results: int) -> dict:
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    candidates = []

    for index, document in enumerate(documents):
        metadata = metadatas[index] if index < len(metadatas) else {}
        distance = distances[index] if index < len(distances) else None

        candidates.append(
            {
                "index": index,
                "document": document,
                "metadata": metadata,
                "distance": distance,
                "score": _rank_candidate(query, document, metadata, distance),
            }
        )

    candidates.sort(key=lambda item: (-item["score"], item["index"]))

    deduped = []
    seen_titles = set()

    for candidate in candidates:
        key = _dedupe_key(candidate["metadata"])

        if key and key in seen_titles:
            continue

        if key:
            seen_titles.add(key)

        deduped.append(candidate)

        if len(deduped) >= n_results:
            break

    return {
        "documents": [[candidate["document"] for candidate in deduped]],
        "metadatas": [[candidate["metadata"] for candidate in deduped]],
        "distances": [[candidate["distance"] for candidate in deduped]],
    }


def search(query: str, n_results: int = 20):
    normalized_query = normalize_query(query)
    expanded_query = expand_query(normalized_query)

    exact_results = collection.get(
        where={"title": query.strip()}
    )

    if exact_results["documents"]:
        return {
            "documents": [exact_results["documents"][:n_results]],
            "metadatas": [exact_results["metadatas"][:n_results]],
            "distances": [[0.0] * len(exact_results["documents"][:n_results])],
        }

    results = collection.query(
        query_texts=[expanded_query],
        n_results=CHROMA_CANDIDATES,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    return _rerank(results, expanded_query, n_results)
