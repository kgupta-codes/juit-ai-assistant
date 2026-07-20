from app.nlu import ConversationState, process_query, update_state_from_query


def rewrite_query(
    question: str,
    history=None,
    state: ConversationState | None = None,
) -> str:
    """Return a deterministic standalone query for retrieval.

    The history parameter is accepted for API compatibility. Follow-up
    resolution is driven by structured ConversationState, not by an LLM.
    """
    processed = process_query(question, state)

    if state is not None:
        update_state_from_query(state, processed)

    return processed.standalone

