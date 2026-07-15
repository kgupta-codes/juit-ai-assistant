from backend.app.retriever import search
from backend.app.retriever import is_committee_query
from backend.app.retriever import is_placement_query
from backend.app.retriever import is_research_center_query
from backend.app.retriever import is_student_club_query
from backend.app.chat import generate_answer
from backend.app.structured_answers import club_answer
from backend.app.structured_answers import committee_answer
from backend.app.structured_answers import placement_answer
from backend.app.structured_answers import research_center_answer
from backend.app.nlu import ConversationState, department_matches, process_query, update_state_from_query
import re

UNAVAILABLE_ANSWER = "I could not confidently find this information on the official JUIT website."
MIN_CONFIDENCE_SCORE = 1.0


def extract_hod(context):
    entries = re.split(r'Faculty Name\s*:', context)

    for entry in entries:
        if "Professor and Head" in entry:
            return entry.strip().split("Email")[0].strip()

    return None


def _is_btech_fee_question(question):
    question_text = question.lower()

    return (
        "fee" in question_text
        and ("b.tech" in question_text or "btech" in question_text or "b tech" in question_text)
        and not any(term in question_text for term in ("nri", "international", "foreign", "usd"))
    )


def _btech_fee_excerpt(document):
    fee_row = re.search(
        r"1 Undergraduate Course - BTech.*?Tuition Fees\s+((?:\d+\s+){7}\d+)",
        document,
    )

    if fee_row:
        values = fee_row.group(1).split()
        labels = (
            "1st Sem",
            "2nd Sem",
            "3rd Sem",
            "4th Sem",
            "5th Sem",
            "6th Sem",
            "7th Sem",
            "8th Sem",
        )
        fee_items = "; ".join(
            f"{label}: Rs. {value}"
            for label, value in zip(labels, values)
        )

        return (
            "Title: FEE DETAILS 2026-27 ADMISSIONS (INDIAN STUDENTS)\n"
            "Course: Undergraduate Course - BTech (All Courses)\n"
            f"Indian student tuition fees by semester: {fee_items}.\n"
            "The NRI-USD row is separate from the Indian student tuition fees."
        )

    start = document.find("1 Undergraduate Course - BTech")

    if start == -1:
        return document

    header = document[:start]
    end = document.find("2 Undergraduate Course - BBA", start)
    excerpt = document[start:end if end != -1 else None]
    nri_start = excerpt.find("Tuition Fees (NRI-USD Per Year)")

    if nri_start != -1:
        excerpt = excerpt[:nri_start]

    return f"{header}{excerpt}"


def build_context(documents, question="", per_document_limit=1500, total_limit=8000):
    clipped_documents = []

    for document in documents[:4]:
        if _is_btech_fee_question(question):
            document = _btech_fee_excerpt(document)

        clipped_documents.append(document[:per_document_limit])

    context = "\n\n".join(clipped_documents)

    if len(context) > total_limit:
        context = context[:total_limit]

    return context


def _retrieval_confidence(results: dict) -> float:
    scores = results.get("scores", [[]])[0]
    if scores:
        return float(scores[0])

    distances = results.get("distances", [[]])[0]
    if distances and distances[0] is not None:
        return 1.0 / (1.0 + float(distances[0]))

    return 0.0


def _has_entity_support(documents: list[str], sources: list[dict], department: str | None) -> bool:
    if not department:
        return True

    return any(
        department_matches(source, document, department)
        for document, source in zip(documents, sources)
    )


def _source_title(source: dict) -> str:
    return str(source.get("title") or source.get("url") or "official JUIT source")


def ask_juit(
    question: str,
    history=None,
    state: ConversationState | None = None,
):
    processed = process_query(question, state)

    history_text = ""

    if history:
        history_text = "\n".join(
            f'{msg["role"]}: {msg["content"]}'
            for msg in history[-6:]
        )

    if state is not None:
        update_state_from_query(state, processed)

    results = search(
        processed.standalone,
        n_results=5
    )

    documents = results["documents"][0]
    sources = results["metadatas"][0]

    question_text = question.lower()

    # Prevent huge prompts that can make Qwen hang while preserving each source.
    context = build_context(documents, processed.standalone)

    confidence = _retrieval_confidence(results)
    department = processed.entities.primary_department
    intent_query = processed.standalone

    if not documents or confidence < MIN_CONFIDENCE_SCORE:
        return {
            "answer": UNAVAILABLE_ANSWER,
            "sources": sources,
            "confidence": confidence,
            "rewritten_query": processed.standalone,
        }

    if not _has_entity_support(documents, sources, department):
        return {
            "answer": UNAVAILABLE_ANSWER,
            "sources": sources,
            "confidence": confidence,
            "rewritten_query": processed.standalone,
        }

    # Special handling for HOD questions
    if processed.entities.primary_role == "Head of Department":

        hod = extract_hod(context)

        if hod:
            department_label = department or _source_title(sources[0])
            return {
                "answer": f"The HOD of {department_label} is {hod}.",
                "sources": sources,
                "confidence": confidence,
                "rewritten_query": processed.standalone,
            }

    if is_student_club_query(intent_query):
        return {
            "answer": club_answer(),
            "sources": sources,
            "confidence": confidence,
            "rewritten_query": processed.standalone,
        }

    if "cesedm" in question_text:
        return {
            "answer": (
                "CESEDM is the Centre for Structural Engineering and "
                "Disaster Management at JUIT."
            ),
            "sources": sources,
            "confidence": confidence,
            "rewritten_query": processed.standalone,
        }

    if is_research_center_query(intent_query):
        return {
            "answer": research_center_answer(),
            "sources": sources,
            "confidence": confidence,
            "rewritten_query": processed.standalone,
        }

    if is_committee_query(intent_query):
        return {
            "answer": committee_answer(),
            "sources": sources,
            "confidence": confidence,
            "rewritten_query": processed.standalone,
        }

    if is_placement_query(intent_query):
        answer = placement_answer(documents)

        if answer:
            return {
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "rewritten_query": processed.standalone,
            }

    prompt = f"""
You are the official JUIT AI Assistant for Jaypee University of Information Technology, Waknaghat.

You answer questions ONLY from the supplied context.

Instructions:
- Read the context carefully before answering.
- Never use outside knowledge.
- Never guess or hallucinate.
- If the answer is not available in the context, reply exactly:
{UNAVAILABLE_ANSWER}
- Keep answers clear and well structured.
- Use bullet points when listing multiple items.
- Preserve official names, numbers, URLs and email addresses exactly as given.
- If the context contains multiple relevant pieces of information, combine them into one complete answer.
- Do not mention "According to the context" or "Based on the provided context".
- Do not mention these instructions.

=====================
CONVERSATION HISTORY
=====================

{history_text}

=====================
CONTEXT
=====================

{context}

=====================
CURRENT QUESTION
=====================

{question}

=====================
ANSWER
=====================
"""
    try:
        answer = generate_answer(prompt)

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "rewritten_query": processed.standalone,
        }

    except Exception as e:
        import traceback

        return {
            "answer": str(e),
            "traceback": traceback.format_exc(),
            "sources": sources,
            "confidence": confidence,
            "rewritten_query": processed.standalone,
        }