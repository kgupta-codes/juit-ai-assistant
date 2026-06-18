 Review backend/app/ingest.py only.

  Do NOT modify code.

  Analyze:

  1. ChromaDB ingestion
  2. Metadata schema
  3. Duplicate handling
  4. Collection rebuild strategy
  5. Error handling

  Provide:

  - Problems
  - Root causes
  - Priority order
  - Estimated impact of each fix

  Reference exact code lines where possible.

  No code changes.


• I’ll inspect the ingest module and nearby references only as needed
  to understand how it is called, without editing anything.

• Explored
  └ Read ingest.py
    Search ingest|Chroma|chromadb|metadata|collection in app
    Search juit|ingest|Chroma|chromadb in MEMORY.md

──────────────────────────────────────────────────────────────────────

• I have the target file with line numbers. I’m checking the immediate
  consumers of the stored metadata to distinguish ingest-only problems
  from downstream compatibility risks.

• Explored
  └ Read retriever.py, main.py
    Search *.json in pages
    Read rag.py

──────────────────────────────────────────────────────────────────────

• The consumers rely mainly on title, url, and chunk, so the metadata
  schema issues are about traceability, rebuild safety, and filtering
  rather than a direct field mismatch. I’m verifying Chroma’s
  duplicate behavior in the installed library before ranking that
  finding.

• Explored
  └ List data
    Search *.json in pages

• Ran python - <<'PY'
  │ import chromadb, inspect
  │ from chromadb.api.models.Collection import Collection
  │ … +3 lines
  └ chromadb 1.5.9
        def add(
    … +48 lines (ctrl + t to view transcript)
            )


──────────────────────────────────────────────────────────────────────

• There are 548 source JSON pages and an existing persistent Chroma
  directory, which makes rebuild and duplicate behavior high-impact
  rather than theoretical. I’m checking current collection size and ID
  shape as read-only evidence.

• Ran python - <<'PY'
  │ import json
  │ from pathlib import Path
  │ … +5 lines
  └ www.juit.ac.in_students-exchange-program-bioUniversityofMissouri.j
    son ['content', 'title', 'url'] 397 'Student Exchange Program Bio
    … +6 lines (ctrl + t to view transcript)
    ['content', 'title', 'url'] 2517 'Projects'
    'https://www.juit.ac.in/physics-and-materials-science-projects'

• Ran python - <<'PY'
  │ from pathlib import Path
  │ import chromadb
  │ … +12 lines
  └ '[Errno -3] Temporary failure in name resolution' thrown while
    requesting HEAD
    … +80 lines (ctrl + t to view transcript)
    RuntimeError: Cannot send a request, as the client has been
    closed.

──────────────────────────────────────────────────────────────────────

• A read-only collection probe hit the embedding model initialization
  path and failed on restricted network/DNS, which is itself relevant
  to import-time error handling. I’m avoiding escalation because this
  review can be completed from static code and installed API behavior.

──────────────────────────────────────────────────────────────────────

• I’ve got enough evidence to review the five requested areas. I’ll
  keep findings tied to backend/app/ingest.py lines, and note where
  downstream checks were only used to estimate impact.

• Ran python - <<'PY'
  │ from pathlib import Path
  │ from collections import Counter
  │ … +6 lines
  └ files 548
    duplicate_stems 0
    []

• Ran python - <<'PY'
  │ from pathlib import Path
  │ import chromadb
  │ … +8 lines
  └ count 4658
    ids
    … +14 lines (ctrl + t to view transcript)
    'https://www.juit.ac.in/physics-and-materials-science-projects',
    'title': 'Projects'}]

──────────────────────────────────────────────────────────────────────

• Findings

  1. P0: Re-running ingestion is not idempotent.
     chunk_id = f"{file_path.stem}_{i}" at backend/app/ingest.py:69
     creates stable IDs, then collection.add(...) at backend/app/
     ingest.py:84 tries to insert them again. ChromaDB add raises on
     existing IDs, so a second ingest can fail instead of refreshing
     the collection.
     Root cause: add is used without prior delete, upsert, or
     collection rebuild.
     Estimated fix impact: High. Makes ingestion repeatable and
     prevents stale or blocked updates.

  2. P0: No real collection rebuild strategy.
     The module uses get_or_create_collection(...) at backend/app/
     ingest.py:27, but main() only loops over files and adds chunks at
     backend/app/ingest.py:95. It never deletes the old collection,
     removes records for deleted pages, or replaces chunks for changed
     pages.
     Root cause: persistent Chroma storage is treated like an append-
     only target.
     Estimated fix impact: High. Prevents stale search results,
     inconsistent answers, and failed refreshes after content changes.

  3. P1: Import-time initialization makes failures happen before
     ingestion starts.
     PersistentClient, the sentence-transformer embedding function,
     and the collection are all created at module import time at
     backend/app/ingest.py:21. In this environment, probing the same
     embedding function attempted network/model resolution and failed
     before any ingest logic could run.
     Root cause: heavy external dependencies are initialized globally
     instead of inside controlled execution with error handling.
     Estimated fix impact: Medium-High. Makes failures diagnosable and
     avoids import-time crashes in scripts/tests.

  4. P1: Metadata schema is too thin for reliable maintenance.
     Metadata only stores title, url, and chunk at backend/app/
     ingest.py:75. It does not store source filename, content hash,
     crawl timestamp, total chunks, schema version, or canonical page
     ID.
     Root cause: metadata is designed only for display/filtering, not
     lifecycle management.
     Estimated fix impact: Medium-High. Enables per-file refresh,
     stale-record cleanup, auditability, and safer migrations.

  5. P2: Error handling is all-or-nothing and mostly implicit.
     JSON loading at backend/app/ingest.py:47, chunking at backend/
     app/ingest.py:57, and Chroma insert at backend/app/ingest.py:84
     are unguarded. One bad JSON file, embedding failure, duplicate
     ID, or Chroma error aborts the whole run without a structured
     summary.
     Root cause: no per-file exception boundary or ingest report.
     Estimated fix impact: Medium. Improves operability, especially
     with 548 page files.

  6. P2: Title is injected twice into stored documents.
     The title is prepended to content at backend/app/ingest.py:55,
     then prepended again to every stored chunk at backend/app/
     ingest.py:71.
     Root cause: retrieval boosting and stored document formatting are
     mixed together.
     Estimated fix impact: Medium. Reduces title overweighting and
     repeated context in RAG answers.

  7. P3: Chunk IDs can have gaps and are tied to splitter internals.
     IDs use the original split index at backend/app/ingest.py:63 and
     backend/app/ingest.py:69, but tiny chunks are skipped at backend/
     app/ingest.py:65. This produces missing chunk numbers and makes
     IDs change if splitter settings or content shape changes.
     Root cause: persisted IDs are derived from transient split
     positions.
     Estimated fix impact: Low-Medium. Mostly affects traceability and
     future differential updates.

  Priority Order

  1. Make ingestion idempotent: delete/upsert/rebuild before add.
  2. Define an explicit rebuild mode for the Chroma collection.
  3. Move Chroma/model initialization into controlled runtime code
     with clear failure handling.

  4. Expand metadata to support lifecycle and audit fields.
  5. Add per-file error handling and final success/failure reporting.
  6. Fix title duplication in stored documents.
  7. Normalize chunk numbering after skipped chunks.

  No code changes were made.

