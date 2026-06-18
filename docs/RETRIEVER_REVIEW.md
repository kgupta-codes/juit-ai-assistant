 Review backend/app/retriever.py.

  Context:

  - Scraper V2 complete
  - Ingest V2 complete
  - Chroma contains 1168 chunks
  - Retrieval testing completed

  Observed failures:


  Example:

  Query:

  Analyze:

  1. Ranking weaknesses
  2. Query normalization
  3. Metadata boosting opportunities
  4. Title matching strategy

  - Problems
  - Root causes
  - Retriever V2 architecture
  - Priority order


• I’ll review the retriever in read-only mode and cross-check
• Explored
  └ Read retriever.py, ingest.py
    Search metadata|title|department|placement|acronym|query|retriev
    in
           app

──────────────────────────────────────────────────────────────────────

• The retriever itself is very small: exact title lookup, a literal
  acronym map, then raw Chroma vector search. I’m checking the V2
  metadata shape now so the recommendations are tied to fields the
  retriever can actually use.

• Explored
  └ Read ingest.py
    Search JUIT AI assistant repository quality review|Chroma
    ingestion|
           Scraper V2|Ingest V2|retrieval in MEMORY.md
    List pages
• V2 ingestion gives the retriever useful signals: page_type,
  department, priority, canonical_url, page_id, chunk position/count,
  and contact/type flags. The current retriever is not using any of
  them after ingestion, which explains the “right page, wrong rank”
  failure mode.

• Explored
  └ Read retriever.py, ingest.py

• Ran python - <<'PY'
  │ import chromadb
  │ from pathlib import Path
  │ … +18 lines
  └ count 1168

    … +31 lines (ctrl + t to view transcript)
    'https://www.juit.ac.in/physics-and-materials-science-programmes',
    80)

──────────────────────────────────────────────────────────────────────

• One important data issue surfaced during review: the CE placements
  page is stored as page_type=placements but department=ece, because
  detect_department checks ece before civil and the URL/title token CE
  appears inside strings that trigger the ECE keyword. Retriever V2
  should compensate for this at query time, but the ingestion
  classifier should also be tightened later.

• Explored
  └ Read MEMORY.md

• Ran python - <<'PY'
  │ import json, pathlib
  │ for p in pathlib.Path('data/pages').glob('*CE*Placements*.json'):
  │ … +6 lines
  └ www.juit.ac.in_CE-Placements.json
    https://www.juit.ac.in/CE-Placements
    … +19 lines (ctrl + t to view transcript)
    students from M.Tech (IoT) 2023 passing out batch received
    placements wit

• Ran python - <<'PY'
  │ from backend.app.retriever import search
  │ q='What is the placement record of Civil Engineering?'
  │ … +6 lines
  └ '[Errno -3] Temporary failure in name resolution' thrown while
    requesting HEAD
    … +81 lines (ctrl + t to view transcript)
    RuntimeError: Cannot send a request, as the client has been
    closed.

──────────────────────────────────────────────────────────────────────

• Problems

  1. Ranking is almost entirely embedding-distance based. backend/app/
     retriever.py:36 only does:
     exact title == query, acronym expansion for whole-query matches,
     then raw Chroma semantic search. There is no post-retrieval
     scoring, metadata boost, page grouping, or query intent handling.

  2. Exact title matching is too brittle. The query What is the
     placement record of Civil Engineering? will never match JUIT CE –
     PLACEMENTS, Civil Engineering, or Programmes exactly. The only
     title shortcut works for literal title queries.

  3. Query normalization is minimal. query.strip() is the only
     normalization. There is no lowercasing for scoring, punctuation
     cleanup, singular/plural handling, stopword removal, “record” to
     “statistics/placements” mapping, or department alias extraction.

  4. Metadata is rich enough but unused. Ingest V2 stores page_type,
     department, priority, canonical_url, page_id, chunk_index,
     chunk_count, chunk_type, contact flags, and title. See backend/
     app/ingest.py:320. The retriever ignores all of these.

  5. Department metadata has at least one classifier error. I verified
     Chroma has JUIT CE – PLACEMENTS as page_type=placements but
     department=ece. The cause is likely department keyword order in
     backend/app/ingest.py:53: ece is checked before civil, and CE-
     Placements / CE can collide with ECE-style matching. Retriever V2
     should not blindly trust department metadata until this is fixed.

  6. Duplicate suppression is absent. If multiple chunks from one page
     rank highly, they can crowd out better page-level diversity. The
     current return shape passes raw chunk results straight through.

  7. Acronym expansion is too narrow. backend/app/retriever.py:24 only
     expands when the entire query equals an acronym. It will not
     expand acronyms embedded in natural questions, and it lacks
     aliases like CE -> Civil Engineering, CSE -> Computer Science,
     ECE -> Electronics and Communication, TNP -> Training and
     Placement.

  Root Causes

  The current retriever is a thin Chroma wrapper, not a ranking layer.
  It assumes the embedding model will infer user intent and order
  results correctly. That works for recall, which matches your
  observation that correct documents are retrieved, but it is weak for
  precision at rank 1.

  The example failure is predictable: “placement record” semantically
  resembles generic programme/department pages, while the actual page
  title uses CE and PLACEMENTS. Without title-token scoring,
  department/page-type boosting, and alias expansion, the precise page
  can sit behind broader pages.

  There is also a metadata trust issue. Ingest V2 created the right
  metadata fields, but the CE placements page’s department is wrong.
  So Retriever V2 should combine metadata with lexical URL/title
  evidence instead of treating metadata as absolute truth.

  Retriever V2 Architecture

  Use a two-stage retrieval pipeline.

  Stage 1: query understanding.

  Normalize the query into structured intent:

  raw query: What is the placement record of Civil Engineering?

  normalized terms:
  - page_type intent: placements
  - department intent: civil
  - aliases: civil engineering, CE
  - answer type: statistics / record
  - title terms: placement, placements, civil, engineering, CE

  This should include:

  - lowercase normalized copy
  - punctuation/hyphen normalization
  - singular/plural normalization for common site terms
  - synonym map: record, statistics, stats -> placement/statistics
    intent

  - department alias map: civil engineering, civil, CE
  - acronym expansion inside the query, not just whole-query
    replacement

  Stage 2: broad candidate retrieval.

  Fetch more than the final result count, for example top 50-100
  chunks. Use multiple candidate sources if practical:

  - semantic query over expanded query
  - title/URL metadata candidates for strong lexical matches
  - optional filtered Chroma query when metadata is reliable enough,
    e.g. page_type=placements

  - fallback unfiltered semantic query to preserve recall

  Stage 3: deterministic reranking.

  Compute a final score per chunk/page:

  score =
    semantic_score
    + title_match_boost
    + page_type_boost
    + department_boost
    + url_slug_boost
    + priority_boost
    + chunk_position_boost
    - duplicate_penalty
    - wrong_intent_penalty

  For the example, JUIT CE – PLACEMENTS should win because it has:

  - title match: CE + PLACEMENTS
  - URL match: /CE-Placements
  - page type: placements
  - content match: “Civil Engineering Department”
  - answer-type match: placement table/statistics

  Even if its department metadata says ece, title/URL/content evidence
  should recover it.

  Stage 4: page-level grouping and duplicate suppression.

  Group candidates by page_id or canonical_url. Keep the best chunk
  per page for ranking, then optionally attach adjacent chunks from
  the winning page if answer generation needs more context. This
  prevents one broad page from occupying multiple result slots and
  improves page diversity.

  Stage 5: return explainable scores.

  For debugging, include internal score components in development
  mode:

  semantic=0.72 title=0.20 page_type=0.15 department=0.10 url=0.10
  duplicate=-0.05 final=1.22

  That will make retrieval testing much faster.

  Priority Order

  1. Add reranking after Chroma retrieval. This is the biggest fix for
     “correct result is #3/#4.” Do not replace Chroma; use it for
     recall, then rerank for precision.

  2. Add query intent extraction for page type and department.
     Placement, fee, faculty, curriculum, admission, contact, notices,
     and department queries should map to known intents.

  3. Add title and URL slug matching. For JUIT’s site, titles and
     slugs are strong signals. CE-Placements should heavily boost
     placement queries mentioning Civil/CE.

  4. Add acronym and alias expansion inside natural-language queries.
     Include department aliases and common institute terms.

  5. Add duplicate suppression by canonical_url / page_id. Rank pages
     first, chunks second.

  6. Use metadata boosts carefully. Boost page_type, priority,
     chunk_index, and chunk_type; use department with caution until
     classifier errors like CE being tagged as ECE are fixed.

  7. Fix ingestion department detection next. Retriever V2 can
     compensate, but the CE/ECE collision should be corrected at the
     metadata source.

  I did not modify files. One live retriever query attempt failed
  because the embedding model tried to reach Hugging Face and DNS/
  network access is unavailable in this environment, so the analysis
  is based on inspected code, Chroma metadata, and the observed test
  result you provided.
