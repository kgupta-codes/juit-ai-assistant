from collections import OrderedDict


MAX_PAGE_LENGTH = 2500
MAX_CONTEXT_LENGTH = 9000

def context_limit(num_sources: int) -> int:
    """
    Decide how much text to keep from each source
    based on how many sources are being sent.
    """

    if num_sources <= 2:
        return 4000

    if num_sources <= 5:
        return 2500

    return 1500

def build_page_context(results: dict) -> str:
    """
    Merge retrieved chunks by their source page before
    sending them to the LLM.
    """

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    grouped = OrderedDict()

    for doc, meta in zip(documents, metadatas):

        page = (
    meta.get("page_id")
    or meta.get("canonical_url")
    or meta.get("url")
    or meta.get("title")
    or "Unknown"
)

        if page not in grouped:

            grouped[page] = {
    "title": meta.get("title", ""),
    "url": meta.get("url", ""),
    "source_type": meta.get("source_type", "html"),
    "department": meta.get("department", ""),
    "page_type": meta.get("page_type", ""),
    "chunks": [],
}

        if doc not in grouped[page]["chunks"]:
            grouped[page]["chunks"].append(doc)

    sections = []

    total = 0

    for page in grouped.values():

        title = page["title"]

        body = "\n\n".join(page["chunks"])

        limit = context_limit(len(grouped))

        body = body[:limit]

        section = f"""
==================================================
Title: {title}

URL: {page["url"] or "Not Available"}

Source Type: {page["source_type"].upper()}

Department: {page["department"] or "General"}
==================================================

Content:

{body}
""".strip()

        total += len(section)

        if total > MAX_CONTEXT_LENGTH:
            break

        sections.append(section)

    return "\n\n".join(sections)