from collections import defaultdict

from backend.app.nlu import ConversationState

# Stores conversations in memory.
# Later we can replace this with Redis or a database.

_conversations = defaultdict(list)
_states = defaultdict(ConversationState)


def add_message(session_id: str, role: str, content: str):
    _conversations[session_id].append(
        {
            "role": role,
            "content": content,
        }
    )


def get_history(session_id: str):
    return _conversations[session_id]


def get_state(session_id: str) -> ConversationState:
    return _states[session_id]


def clear_history(session_id: str):
    _conversations.pop(session_id, None)
    _states.pop(session_id, None)
