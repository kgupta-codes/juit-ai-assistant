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
import re


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


def build_context(documents, question="", per_document_limit=1000, total_limit=3000):
    clipped_documents = []

    for document in documents[:3]:
        if _is_btech_fee_question(question):
            document = _btech_fee_excerpt(document)

        clipped_documents.append(document[:per_document_limit])

    context = "\n\n".join(clipped_documents)

    if len(context) > total_limit:
        context = context[:total_limit]

    return context


def ask_juit(question: str):

    results = search(question, n_results=3)

    documents = results["documents"][0]
    sources = results["metadatas"][0]
    question_text = question.lower()

    # Prevent huge prompts that can make Qwen hang while preserving each source.
    context = build_context(documents, question)

    # Special handling for HOD questions
    if "hod" in question.lower() or "head of department" in question.lower():

        hod = extract_hod(context)

        if hod:
            return {
                "answer": f"The HOD of Civil Engineering is {hod}.",
                "sources": sources
            }

    if is_student_club_query(question):
        return {
            "answer": club_answer(),
            "sources": sources
        }

    if "cesedm" in question_text:
        return {
            "answer": (
                "CESEDM is the Centre for Structural Engineering and "
                "Disaster Management at JUIT."
            ),
            "sources": sources
        }

    if is_research_center_query(question):
        return {
            "answer": research_center_answer(),
            "sources": sources
        }

    if is_committee_query(question):
        return {
            "answer": committee_answer(),
            "sources": sources
        }

    if is_placement_query(question):
        answer = placement_answer(documents)

        if answer:
            return {
                "answer": answer,
                "sources": sources
            }

    prompt = f"""
You are the JUIT AI Assistant.

Answer ONLY using the provided context.

Rules:
- Use exact information from the context.
- Maximum 3 sentences.
- Do not invent facts.
- Do not use outside knowledge.
- If answer is not present, reply exactly:
I could not find that information in the JUIT knowledge base.

Context:
{context}

Question:
{question}

Answer:
"""

    try:
        answer = generate_answer(prompt)

        return {
            "answer": answer,
            "sources": sources
        }

    except Exception as e:

        return {
            "answer": f"Error generating answer: {str(e)}",
            "sources": sources
        }
