from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = BASE_DIR / "chroma_db"

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
    "CESEDM": "Centre for Structural Engineering and Disaster Management",
    "CESTRD": "Centre of Sustainable Technologies for Rural Development",
    "CEC": "Civil Engineering Consortium",
    "JYC": "JUIT Youth Club",
    "ICC": "Internal Complaint Committee",
    "NSS": "National Service Scheme",
    "NCC": "National Cadet Corps"
}


def search(query: str, n_results: int = 20):

    query = query.strip()

    # --------------------------------------------------
    # STEP 1: Exact title match
    # --------------------------------------------------

    exact_results = collection.get(
        where={"title": query}
    )

    if exact_results["documents"]:

        return {
            "documents": [exact_results["documents"]],
            "metadatas": [exact_results["metadatas"]],
            "distances": [[0.0] * len(exact_results["documents"])]
        }

    # --------------------------------------------------
    # STEP 2: Acronym expansion
    # --------------------------------------------------

    expanded_query = ACRONYMS.get(
        query.upper(),
        query
    )

    # --------------------------------------------------
    # STEP 3: Semantic search
    # --------------------------------------------------

    results = collection.query(
        query_texts=[expanded_query],
        n_results=n_results,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    return results
