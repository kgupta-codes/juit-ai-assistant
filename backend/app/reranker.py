from functools import lru_cache
from typing import Any

import torch
from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L6-v2"

# Number of query-document pairs processed together.
RERANK_BATCH_SIZE = 16


@lru_cache(maxsize=1)
def get_reranker() -> CrossEncoder:
    """
    Lazily load the reranker only once.

    The model is automatically placed on GPU if CUDA is available,
    otherwise CPU is used.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"

    return CrossEncoder(
        MODEL_NAME,
        device=device,
    )


def _build_document(candidate: dict[str, Any]) -> str:
    """
    Build a richer document for reranking.

    Giving the reranker title + section + content consistently improves
    ranking over using the chunk text alone.
    """

    metadata = candidate.get("metadata", {})

    title = metadata.get("title", "")
    section = metadata.get("section", "")
    page_type = metadata.get("page_type", "")

    parts = []

    if title:
        parts.append(f"Title: {title}")

    if section:
        parts.append(f"Section: {section}")

    if page_type:
        parts.append(f"Page Type: {page_type}")

    parts.append(candidate["document"])

    return "\n".join(parts)


def rerank_candidates(
    query: str,
    candidates: list[dict[str, Any]],
    top_k: int,
) -> list[dict[str, Any]]:
    """
    Semantic reranking using CrossEncoder.

    Input:
        Query
        Candidate documents from heuristic reranker

    Output:
        Top-K candidates sorted by semantic relevance.
    """

    if not candidates:
        return []

    model = get_reranker()

    pairs = [
        (
            query,
            _build_document(candidate),
        )
        for candidate in candidates
    ]

    with torch.inference_mode():
        scores = model.predict(
            pairs,
            batch_size=RERANK_BATCH_SIZE,
            show_progress_bar=False,
        )

    for candidate, score in zip(candidates, scores):
        candidate["cross_score"] = float(score)

    candidates.sort(
        key=lambda candidate: candidate["cross_score"],
        reverse=True,
    )

    return candidates[:top_k]