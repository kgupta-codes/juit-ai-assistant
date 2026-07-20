from collections import OrderedDict


def build_citations(sources: list[dict]) -> list[dict]:
    """
    Deduplicate and clean citations before sending
    them to the frontend.
    """

    unique = OrderedDict()

    for source in sources:

        title = (
            source.get("title")
            or "Official JUIT Source"
        )

        url = source.get("url") or ""

        source_type = source.get(
            "source_type",
            "html"
        )

        key = (title, url)

        if key in unique:
            continue

        unique[key] = {
    "title": title,
    "url": url,
    "type": source_type,
    "department": source.get("department"),
    "page_type": source.get("page_type"),
}

    return list(unique.values())