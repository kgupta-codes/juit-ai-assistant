import re
import math
from collections import Counter
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from backend.app.nlu import department_matches, process_query, role_matches

BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = BASE_DIR / "chroma_db"

CHROMA_CANDIDATES = 60
KEYWORD_CANDIDATES = 40
HYBRID_KEYWORD_WEIGHT = 0.25
ENTITY_MISMATCH_PENALTY = 4.0
ENTITY_MATCH_BOOST = 1.25
INSTITUTION_TERMS = {
    "juit",
    "jaypee",
    "university",
    "information",
    "technology",
    "waknaghat",
}

CONFERENCE_URL_MARKERS = {
    "pdgc",
    "icbab",
    "iciip",
    "ispcc",
    "iccme",
    "icsmc",
}

STUDENT_CLUB_MARKERS = {
    "juit youth club",
    "nss",
    "ncc",
    "civil engineering cec",
    "synapse students club",
    "technical club cse it",
    "technovatorz electronics club",
    "koshishclub",
    "coding society juit cse it",
    "ieee student branch",
    "gender champions club",
}

RESEARCH_CENTER_MARKERS = {
    "cesedm",
    "cestrd",
    "cccwr",
    "cehti",
    "centre for climate change and water resources",
    "centre of excellence in structural engineering",
    "biotechnology bioinformatics cestrd",
    "biotechnology bioinformatics cehti",
    "ride centre of excellence",
    "center of excellence industry",
    "center of excellence ldra",
}

CANONICAL_CLUB_PAGES = {
    "juit-youth-club",
    "nss-in-juit",
    "nss",
    "ncc",
    "about-ncc",
    "civil-engineering-cec",
    "coding-society-juit-cse-it",
    "ieee-student-branch",
    "synapse-students-club",
    "technical-club-cse-it",
    "technovatorz-electronics-club",
    "koshishclub",
    "gender-champions-club",
}

CANONICAL_RESEARCH_CENTER_PAGES = {
    "centre-of-excellence-in-structural-engineering-and-disaster-management",
    "cesedm-about-the-centre",
    "biotechnology-bioinformatics-cestrd",
    "centre-for-climate-change-and-water-resources",
    "cccwr-about-the-centre",
    "biotechnology-bioinformatics-cehti",
    "center-of-excellence-industry",
    "center-of-excellence-ldra-cse-it",
    "ride-centre-of-excellence",
}

CANONICAL_COMMITTEE_PAGES = {
    "committees",
    "sgrc",
    "internal-complaint-committee",
    "student-counselling-committee",
    "ethics-committee",
    "committee-caste-based-discrimination",
    "nep-committee",
    "ece-department-committees",
    "website-committee",
}

DETAIL_PAGE_MARKERS = {
    "events",
    "past-events",
    "pastevents",
    "board",
    "faculty-in-charge",
    "staff",
    "notices",
    "announcements",
    "meetings",
    "objectives",
    "visionmission",
    "rolesandresponsibilities",
}

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
    "HOD": "Head of Department",
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
    query = query.replace("HOD", "Head of Department")
    query = query.replace("hod", "head of department")
    normalized = _normalize_text(query)

    for phrase in FILLER_PHRASES:
        normalized = normalized.replace(phrase, " ")

    return re.sub(r"\s+", " ", normalized).strip()


def expand_query(query: str) -> str:
    expanded_parts = [query]
    padded_query = f" {query} "
    query_tokens = _tokens(query)

    for acronym, expansion in ACRONYMS.items():
        normalized_acronym = acronym.lower()
        normalized_expansion = _normalize_text(expansion)

        if f" {normalized_acronym} " in padded_query:
            expanded_parts.append(normalized_expansion)
            continue

        if normalized_expansion in query:
            expanded_parts.append(normalized_acronym)

    if _is_fee_query(query_tokens):
        expanded_parts.append(
            "admissions indian students undergraduate course btech all courses "
            "tuition fees fee details"
        )

    if _is_research_center_query(query_tokens):
        expanded_parts.append(
            "research centres research centers centre of excellence CESEDM CESTRD "
            "CCCWR Centre for Structural Engineering and Disaster Management "
            "Centre of Sustainable Technologies for Rural Development "
            "Centre for Climate Change and Water Resources"
        )

    if _is_student_club_query(query_tokens):
        expanded_parts.append(
            "JUIT Youth Club JYC NSS NCC Civil Engineering Consortium CEC "
            "Synapse Technical Club Technovatorz Koshish Coding Society IEEE "
            "student club society organization"
        )

    if _is_placement_query(query_tokens):
        expanded_parts.append(
            "civil engineering placements placement record offers eligible students "
            "students placed CE placements"
        )

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

    content_title_tokens = title_tokens - INSTITUTION_TERMS

    if content_title_tokens and title_tokens.issubset(query_tokens):
        boost += 0.75

    if content_title_tokens and query_tokens and len(overlap) / len(title_tokens) >= 0.5:
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

    if _is_canonical_url(metadata, CANONICAL_COMMITTEE_PAGES):
        boost += 2.0

    if "committee" in document_text:
        boost += 0.4

    committee_overlap = (query_tokens & COMMITTEE_TERMS) & _tokens(document_text)
    boost += 0.25 * len(committee_overlap)

    if "anti drug" in document_text or "anti drug" in title_text:
        boost += 0.9

    if page_type == "events":
        boost -= 0.7

    if any(marker in _url_slug(metadata) for marker in DETAIL_PAGE_MARKERS):
        boost -= 0.5

    return boost


def _metadata_text(metadata: dict) -> str:
    return _normalize_text(
        " ".join(
            str(metadata.get(key, ""))
            for key in ("title", "url", "canonical_url", "page_type")
        )
    )


def _url_slug(metadata: dict) -> str:
    url = str(metadata.get("canonical_url") or metadata.get("url") or "")
    slug = url.rstrip("/").split("/")[-1]
    return _normalize_text(slug).replace(" ", "-")


def _is_canonical_url(metadata: dict, canonical_slugs: set[str]) -> bool:
    return _url_slug(metadata) in canonical_slugs


def is_student_club_query(query: str) -> bool:
    return _is_student_club_query(_tokens(query))


def is_research_center_query(query: str) -> bool:
    return _is_research_center_query(_tokens(query))


def is_committee_query(query: str) -> bool:
    return bool(_tokens(query) & COMMITTEE_TERMS)


def is_placement_query(query: str) -> bool:
    return _is_placement_query(_tokens(query))


def _is_fee_query(query_tokens: set[str]) -> bool:
    return bool(query_tokens & {"fee", "fees", "tuition"}) and bool(
        query_tokens & {"b", "tech", "btech", "undergraduate", "admission", "admissions"}
    )


def _is_research_center_query(query_tokens: set[str]) -> bool:
    return bool(query_tokens & {"research", "centre", "centres", "center", "centers"}) and bool(
        query_tokens & {"centre", "centres", "center", "centers", "available", "research"}
    )


def _is_student_club_query(query_tokens: set[str]) -> bool:
    return bool(query_tokens & {"student", "students"}) and bool(
        query_tokens & {"club", "clubs", "society", "societies", "organization", "organizations"}
    )


def _is_placement_query(query_tokens: set[str]) -> bool:
    return bool(query_tokens & {"placement", "placements", "placed", "record", "offers"}) and bool(
        query_tokens & {"civil", "engineering", "ce"}
    )


def _fee_boost(query_tokens: set[str], document: str, metadata: dict) -> float:
    if not _is_fee_query(query_tokens):
        return 0.0

    meta_text = _metadata_text(metadata)
    document_text = _normalize_text(document)
    boost = 0.0

    if "fee detail" in meta_text or "fee details" in meta_text:
        boost += 2.4

    if "indian students" in meta_text:
        boost += 1.1

    if "international students" in meta_text and not (
        query_tokens & {"international", "nri", "foreign", "usd"}
    ):
        boost -= 3.0

    if "undergraduate course btech" in document_text:
        boost += 1.2

    if "tuition fees" in document_text:
        boost += 0.9

    if "btech all courses" in document_text:
        boost += 0.6

    if any(marker in meta_text for marker in CONFERENCE_URL_MARKERS):
        boost -= 2.4

    if "conference" in document_text and "registration" in document_text:
        boost -= 1.4

    if "registration fee" in meta_text or "registration accommodation" in meta_text:
        boost -= 1.0

    if metadata.get("page_type") in {"curriculum", "general", "public_disclosure"} and (
        "tuition fee" not in document_text and "fee detail" not in meta_text
    ):
        boost -= 0.8

    return boost


def _research_center_boost(query_tokens: set[str], document: str, metadata: dict) -> float:
    if not _is_research_center_query(query_tokens):
        return 0.0

    meta_text = _metadata_text(metadata)
    document_text = _normalize_text(document)
    combined = f"{meta_text} {document_text[:1200]}"
    boost = 0.0

    if any(marker in meta_text for marker in RESEARCH_CENTER_MARKERS):
        boost += 2.0

    if _is_canonical_url(metadata, CANONICAL_RESEARCH_CENTER_PAGES):
        boost += 2.4

    if "cccwr" in meta_text:
        boost += 2.0

    if "cestrd" in meta_text:
        boost += 1.5

    for phrase in (
        "centre of sustainable technologies",
        "centre for structural engineering",
        "structural engineering and disaster management",
        "climate change and water resources",
        "centre of healthcare technologies",
        "centre of excellence",
    ):
        if phrase in combined:
            boost += 0.9

    if "about the centre" in meta_text and any(
        marker in meta_text for marker in {"cccwr", "cesedm", "cestrd", "cehti"}
    ):
        boost += 1.0

    if metadata.get("page_type") == "events":
        boost -= 0.8

    if any(marker in _url_slug(metadata) for marker in DETAIL_PAGE_MARKERS):
        boost -= 0.6

    if any(phrase in meta_text for phrase in ("research domains", "research projects")):
        boost -= 0.9

    return boost


def _student_club_boost(query_tokens: set[str], document: str, metadata: dict) -> float:
    if not _is_student_club_query(query_tokens):
        return 0.0

    meta_text = _metadata_text(metadata)
    document_text = _normalize_text(document)
    combined = f"{meta_text} {document_text[:1200]}"
    boost = 0.0

    if any(marker in meta_text for marker in STUDENT_CLUB_MARKERS):
        boost += 2.2

    if _is_canonical_url(metadata, CANONICAL_CLUB_PAGES):
        boost += 2.4

    if "juit youth club" in meta_text:
        boost += 2.0

    if "nss" in meta_text:
        boost += 2.2

    if "civil engineering cec" in meta_text:
        boost += 2.4

    if "ncc" in meta_text:
        boost += 0.8

    if "koshishclub" in meta_text:
        boost -= 0.5

    for phrase in (
        "juit youth club",
        "national service scheme",
        "national cadet corps",
        "civil engineering consortium",
        "synapse club",
        "technical club",
        "electronics club",
        "coding society",
        "ieee juit student branch",
        "koshish club",
    ):
        if phrase in combined:
            boost += 0.7

    if "club" in meta_text:
        boost += 0.6

    if any(term in meta_text for term in ("alumni", "placement", "faculty", "department")):
        boost -= 1.0

    if "cell" in meta_text and "club" not in combined:
        boost -= 0.8

    if any(marker in _url_slug(metadata) for marker in DETAIL_PAGE_MARKERS):
        boost -= 0.6

    return boost


def _placement_boost(query_tokens: set[str], document: str, metadata: dict) -> float:
    if not _is_placement_query(query_tokens):
        return 0.0

    meta_text = _metadata_text(metadata)
    document_text = _normalize_text(document)
    boost = 0.0

    if "ce placements" in meta_text or "juit ce placements" in meta_text:
        boost += 2.8

    if "ece placements" in meta_text:
        boost -= 3.0

    if "civil" not in f"{meta_text} {document_text[:1500]}":
        boost -= 2.5

    if metadata.get("page_type") == "placements":
        boost += 1.0

    if "civil engineering department" in document_text and "students placed" in document_text:
        boost += 1.1

    if "no of students placed" in document_text or "received offers" in document_text:
        boost += 0.9

    if metadata.get("page_type") in {"curriculum", "department", "faculty"}:
        boost -= 0.8

    if "consortium" in meta_text:
        boost -= 1.0

    return boost

def _hostel_boost(query_tokens: set[str], document: str, metadata: dict) -> float:
    if not (query_tokens & {"hostel", "hostels"}):
        return 0.0

    meta_text = _metadata_text(metadata)
    document_text = _normalize_text(document)

    boost = 0.0

    if "hostel" in meta_text:
        boost += 3.0

    if metadata.get("title", "").lower() == "hostels":
        boost += 5.0

    for term in (
        "hostel",
        "hostels",
        "bhawan",
        "mess",
        "gym",
        "accommodation",
        "residential",
    ):
        if term in document_text:
            boost += 0.5

    return boost

def _faculty_boost(query: str, title: str, document: str, metadata: dict) -> float:
    query_text = query.lower()
    title_text = title.lower()
    document_text = document.lower()

    boost = 0.0

    faculty_terms = {
        "hod",
        "head",
        "faculty",
        "professor",
        "teacher",
        "dean",
        "director",
    }

    if any(term in query_text for term in faculty_terms):

        if "faculty" in title_text:
            boost += 1.0

        if "head" in document_text:
            boost += 0.8

        if "professor" in document_text:
            boost += 0.3

        if metadata.get("page_type") == "faculty":
            boost += 0.5

    return boost

def _rank_candidate(
    query: str,
    document: str,
    metadata: dict,
    distance,
    keyword_score: float = 0.0,
) -> float:
    title = metadata.get("title", "")
    query_tokens = _tokens(query)
    phrases = _exact_phrases(query)
    processed = process_query(query)

    score = _semantic_score(distance)
    score += HYBRID_KEYWORD_WEIGHT * keyword_score
    score += _title_boost(query_tokens, title)
    score += _exact_phrase_boost(phrases, title, document)
    score += _committee_boost(query_tokens, title, document, metadata)
    score += _faculty_boost(query, title, document, metadata)
    score += _fee_boost(query_tokens, document, metadata)
    score += _research_center_boost(query_tokens, document, metadata)
    score += _student_club_boost(query_tokens, document, metadata)
    score += _placement_boost(query_tokens, document, metadata)
    score += _hostel_boost(query_tokens, document, metadata)

    department = processed.entities.primary_department
    role = processed.entities.primary_role

    if department:
        if department_matches(metadata, document, department):
            score += ENTITY_MATCH_BOOST
        else:
            score -= ENTITY_MISMATCH_PENALTY

    if role:
        if role_matches(metadata, document, role):
            score += ENTITY_MATCH_BOOST
        else:
            score -= ENTITY_MISMATCH_PENALTY / 2

    return score


def _dedupe_key(metadata: dict) -> str:
    title = _normalize_text(metadata.get("title", ""))
    chunk_id = metadata.get("chunk_id")
    chunk_index = metadata.get("chunk_index", 0)

    if chunk_id:
        return str(chunk_id)

    return f"{title}:{chunk_index}"


def _candidate_key(metadata: dict, index: int) -> str:
    key = _dedupe_key(metadata)
    if key and key != ":0":
        return key
    return f"candidate:{index}"


def _rerank(results: dict, query: str, n_results: int) -> dict:
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    keyword_scores = results.get("keyword_scores", [[]])[0]

    candidates = []

    for index, document in enumerate(documents):
        metadata = metadatas[index] if index < len(metadatas) else {}
        distance = distances[index] if index < len(distances) else None
        keyword_score = keyword_scores[index] if index < len(keyword_scores) else 0.0

        candidates.append(
            {
                "index": index,
                "document": document,
                "metadata": metadata,
                "distance": distance,
                "keyword_score": keyword_score,
                "score": _rank_candidate(query, document, metadata, distance, keyword_score),
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
        "scores": [[candidate["score"] for candidate in deduped]],
        "keyword_scores": [[candidate["keyword_score"] for candidate in deduped]],
    }


def _keyword_candidates(query: str, limit: int = KEYWORD_CANDIDATES) -> dict:
    query_terms = [
        token
        for token in _tokens(query)
        if len(token) > 1 and token not in INSTITUTION_TERMS
    ]

    if not query_terms:
        return {"documents": [[]], "metadatas": [[]], "distances": [[]], "keyword_scores": [[]]}

    all_results = collection.get(include=["documents", "metadatas"])
    documents = all_results.get("documents", [])
    metadatas = all_results.get("metadatas", [])

    if not documents:
        return {"documents": [[]], "metadatas": [[]], "distances": [[]], "keyword_scores": [[]]}

    doc_tokens = [_tokens(f"{metadatas[index].get('title', '')} {document}") for index, document in enumerate(documents)]
    doc_count = len(documents)
    document_frequency = Counter(
        term
        for terms in doc_tokens
        for term in set(terms)
        if term in query_terms
    )

    scored = []
    for index, terms in enumerate(doc_tokens):
        if not terms:
            continue

        term_counts = Counter(terms)
        score = 0.0
        for term in query_terms:
            frequency = term_counts.get(term, 0)
            if not frequency:
                continue

            idf = math.log(1 + (doc_count - document_frequency[term] + 0.5) / (document_frequency[term] + 0.5))
            score += idf * (frequency / (frequency + 1.2))

        if score > 0:
            scored.append((score, index))

    scored.sort(key=lambda item: item[0], reverse=True)
    selected = scored[:limit]

    return {
        "documents": [[documents[index] for _score, index in selected]],
        "metadatas": [[metadatas[index] for _score, index in selected]],
        "distances": [[None for _score, _index in selected]],
        "keyword_scores": [[score for score, _index in selected]],
    }


def _merge_results(dense_results: dict, keyword_results: dict) -> dict:
    merged = {}

    for source in (dense_results, keyword_results):
        documents = source.get("documents", [[]])[0]
        metadatas = source.get("metadatas", [[]])[0]
        distances = source.get("distances", [[]])[0]
        keyword_scores = source.get("keyword_scores", [[]])[0]

        for index, document in enumerate(documents):
            metadata = metadatas[index] if index < len(metadatas) else {}
            key = _candidate_key(metadata, len(merged))
            distance = distances[index] if index < len(distances) else None
            keyword_score = keyword_scores[index] if index < len(keyword_scores) else 0.0

            if key not in merged:
                merged[key] = {
                    "document": document,
                    "metadata": metadata,
                    "distance": distance,
                    "keyword_score": keyword_score,
                }
                continue

            current = merged[key]
            if current["distance"] is None or (distance is not None and distance < current["distance"]):
                current["distance"] = distance
            current["keyword_score"] = max(current["keyword_score"], keyword_score)

    candidates = list(merged.values())
    return {
        "documents": [[candidate["document"] for candidate in candidates]],
        "metadatas": [[candidate["metadata"] for candidate in candidates]],
        "distances": [[candidate["distance"] for candidate in candidates]],
        "keyword_scores": [[candidate["keyword_score"] for candidate in candidates]],
    }


def search(query: str, n_results: int = 20):
    processed = process_query(query)
    normalized_query = normalize_query(processed.standalone)
    expanded_query = f"{processed.expanded} {expand_query(normalized_query)}"

    exact_results = collection.get(
        where={"title": query.strip()}
    )

    if exact_results["documents"]:
        return {
            "documents": [exact_results["documents"][:n_results]],
            "metadatas": [exact_results["metadatas"][:n_results]],
            "distances": [[0.0] * len(exact_results["documents"][:n_results])],
        }

    dense_results = collection.query(
        query_texts=[expanded_query],
        n_results=CHROMA_CANDIDATES,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )
    keyword_results = _keyword_candidates(expanded_query)
    results = _merge_results(dense_results, keyword_results)

    return _rerank(results, expanded_query, n_results)
