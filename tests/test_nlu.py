from backend.app.nlu import (
    ConversationState,
    extract_entities,
    process_query,
    role_matches,
    update_state_from_query,
)
from backend.app.query_rewriter import rewrite_query


def test_expands_vc_abbreviation_to_role():
    entities = extract_entities("Who is the VC?")

    assert entities.roles == ("Vice Chancellor",)


def test_detects_department_and_hod_role():
    entities = extract_entities("Who is the HOD of CSE?")

    assert entities.roles == ("Head of Department",)
    assert entities.departments == (
        "Computer Science Engineering and Information Technology",
    )


def test_follow_up_uses_active_department():
    state = ConversationState(active_department="Civil Engineering")

    processed = process_query("What laboratories does this department have?", state)

    assert processed.used_memory is True
    assert "Civil Engineering" in processed.standalone
    assert processed.entities.departments == ("Civil Engineering",)


def test_plain_it_is_not_detected_as_information_technology():
    state = ConversationState(active_department="Civil Engineering")

    processed = process_query("What software is used in it?", state)

    assert processed.entities.departments == ("Civil Engineering",)


def test_rewrite_query_updates_conversation_state():
    state = ConversationState()
    rewrite_query("Tell me about Civil Engineering.", state=state)

    rewritten = rewrite_query("Who is the HOD?", state=state)

    assert state.active_department == "Civil Engineering"
    assert rewritten == "Who is the HOD? for Civil Engineering"


def test_update_state_tracks_program_and_topic():
    state = ConversationState()
    processed = process_query("What is the BTech fee?")

    update_state_from_query(state, processed)

    assert state.active_program == "B.Tech"
    assert state.active_topic == "Fee"


def test_hod_role_matches_professor_and_head_evidence():
    assert role_matches(
        {"title": "Civil Engineering Faculty", "page_type": "faculty"},
        "Faculty Name : Dr. Example Professor and Head Email example@juit.ac.in",
        "Head of Department",
    )
