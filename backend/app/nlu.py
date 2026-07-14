import re
from dataclasses import dataclass, field

from backend.app.query_config import (
    DEPARTMENT_ALIASES,
    GENERAL_ALIASES,
    PROGRAM_ALIASES,
    ROLE_ALIASES,
    EntityAlias,
)


TOKEN_RE = re.compile(r"[a-z0-9]+")

FOLLOW_UP_TERMS = {
    "it",
    "its",
    "this",
    "that",
    "their",
    "there",
    "department",
    "dept",
}


@dataclass(frozen=True)
class QueryEntities:
    roles: tuple[str, ...] = ()
    departments: tuple[str, ...] = ()
    programs: tuple[str, ...] = ()
    topics: tuple[str, ...] = ()

    @property
    def primary_department(self) -> str | None:
        return self.departments[0] if self.departments else None

    @property
    def primary_role(self) -> str | None:
        return self.roles[0] if self.roles else None


@dataclass
class ConversationState:
    active_department: str | None = None
    active_program: str | None = None
    active_topic: str | None = None
    facts: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ProcessedQuery:
    original: str
    normalized: str
    standalone: str
    expanded: str
    entities: QueryEntities
    used_memory: bool = False


def normalize_text(text: str) -> str:
    text = (text or "").lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9.]+", " ", text)
    text = re.sub(r"\bph\.?\s*d\b", "phd", text)
    text = re.sub(r"\bb\.?\s*tech\b", "btech", text)
    text = re.sub(r"\bm\.?\s*tech\b", "mtech", text)
    return re.sub(r"\s+", " ", text).strip()


def tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall(normalize_text(text)))


def extract_entities(query: str) -> QueryEntities:
    normalized = normalize_text(query)

    return QueryEntities(
        roles=_matches(ROLE_ALIASES, normalized),
        departments=_matches(DEPARTMENT_ALIASES, normalized),
        programs=_matches(PROGRAM_ALIASES, normalized),
        topics=_matches(GENERAL_ALIASES, normalized),
    )


def process_query(query: str, state: ConversationState | None = None) -> ProcessedQuery:
    state = state or ConversationState()
    normalized = normalize_text(query)
    entities = extract_entities(query)
    used_memory = False

    standalone = query.strip()
    if _needs_department_context(normalized, entities) and state.active_department:
        standalone = f"{standalone} for {state.active_department}"
        used_memory = True
        entities = extract_entities(standalone)

    if not entities.programs and state.active_program and _is_follow_up(normalized):
        standalone = f"{standalone} for {state.active_program}"
        used_memory = True
        entities = extract_entities(standalone)

    expanded = expand_query(standalone, entities)

    return ProcessedQuery(
        original=query,
        normalized=normalized,
        standalone=standalone,
        expanded=expanded,
        entities=entities,
        used_memory=used_memory,
    )


def update_state_from_query(state: ConversationState, processed: ProcessedQuery) -> None:
    if processed.entities.primary_department:
        state.active_department = processed.entities.primary_department
    if processed.entities.programs:
        state.active_program = processed.entities.programs[0]
    if processed.entities.topics:
        state.active_topic = processed.entities.topics[0]
    elif processed.entities.primary_role:
        state.active_topic = processed.entities.primary_role


def expand_query(query: str, entities: QueryEntities | None = None) -> str:
    entities = entities or extract_entities(query)
    parts = [query.strip()]

    for values in (entities.roles, entities.departments, entities.programs, entities.topics):
        parts.extend(values)

    for alias_group in (*ROLE_ALIASES, *DEPARTMENT_ALIASES, *PROGRAM_ALIASES, *GENERAL_ALIASES):
        if alias_group.canonical in parts:
            parts.extend(alias_group.aliases)

    return " ".join(dict.fromkeys(part for part in parts if part))


def department_matches(metadata: dict, document: str, department: str | None) -> bool:
    if not department:
        return True

    haystack = normalize_text(
        " ".join(
            [
                str(metadata.get("department", "")),
                str(metadata.get("title", "")),
                str(metadata.get("url", "")),
                str(metadata.get("canonical_url", "")),
                document[:1500],
            ]
        )
    )

    aliases = _aliases_for(DEPARTMENT_ALIASES, department)
    return any(_contains_alias(haystack, alias) for alias in aliases)


def role_matches(metadata: dict, document: str, role: str | None) -> bool:
    if not role:
        return True

    haystack = normalize_text(
        f"{metadata.get('title', '')} {metadata.get('page_type', '')} {document[:1500]}"
    )
    if role == "Head of Department" and "head" in haystack:
        return True

    aliases = _aliases_for(ROLE_ALIASES, role)
    return any(_contains_alias(haystack, alias) for alias in aliases)


def _matches(alias_groups: tuple[EntityAlias, ...], normalized: str) -> tuple[str, ...]:
    matches = []
    for alias_group in alias_groups:
        if any(_contains_alias(normalized, alias) for alias in alias_group.aliases):
            matches.append(alias_group.canonical)
    return tuple(dict.fromkeys(matches))


def _contains_alias(normalized: str, alias: str) -> bool:
    alias = normalize_text(alias)
    if not alias:
        return False
    return re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", normalized) is not None


def _aliases_for(alias_groups: tuple[EntityAlias, ...], canonical: str) -> tuple[str, ...]:
    for alias_group in alias_groups:
        if alias_group.canonical == canonical:
            return (alias_group.canonical, *alias_group.aliases)
    return (canonical,)


def _needs_department_context(normalized: str, entities: QueryEntities) -> bool:
    if entities.departments:
        return False
    query_tokens = set(normalized.split())
    return bool(query_tokens & FOLLOW_UP_TERMS) or bool(
        entities.roles or "Laboratory" in entities.topics or "lab" in query_tokens
    )


def _is_follow_up(normalized: str) -> bool:
    return bool(set(normalized.split()) & FOLLOW_UP_TERMS)
