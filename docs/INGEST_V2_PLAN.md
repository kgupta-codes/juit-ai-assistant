# Ingestion V2 Implementation Plan

## 1. Better Chunking Strategy

### Goals

Ingestion V2 should create chunks that match how users ask university questions. The current fixed character splitter should be replaced with a lightweight document-aware chunker that still works with the current scraper output:

```json
{
  "url": "...",
  "title": "...",
  "content": "..."
}
```

The scraper has already been upgraded, so V2 can assume cleaner page text, better titles, and canonicalized URLs, but it should still defend against low-value, duplicate, or malformed records.

### Chunking Pipeline

1. Load each JSON page.
2. Validate required fields:
   - `url`
   - `title`
   - `content`
3. Normalize fields:
   - trim whitespace
   - collapse repeated whitespace
   - canonicalize URL again as a defense-in-depth step
   - normalize weak titles only when obviously recoverable from URL
4. Classify page type from URL, title, and content.
5. Split content into semantic blocks before character splitting.
6. Build chunks from complete blocks.
7. Apply size limits only after semantic grouping.
8. Attach rich metadata to every chunk.
9. Upsert chunks using deterministic IDs.

### Page Type Detection

Detect page type with simple rules, not a large framework.

Use URL/title/content keywords to assign:

- `admissions`
- `fees`
- `academic_calendar`
- `curriculum`
- `department`
- `faculty`
- `staff`
- `committee`
- `notices`
- `placements`
- `public_disclosure`
- `library`
- `publications`
- `events`
- `alumni`
- `utility`
- `general`

Page type should influence chunk size, metadata, and ranking later.

### Chunk Shape

Each chunk document stored in Chroma should include enough context to stand alone:

```text
Title: <page title>
URL: <canonical url>
Section: <section heading if available>

<chunk text>
```

Do not prepend the title twice. The stored document should contain one clean title/context header followed by the chunk body.

### Chunk Size Policy

Use token-aware sizing if a tokenizer is available. If not, use character approximations.

Recommended defaults:

- Target chunk size: 700-1,000 words or 3,500-5,000 characters.
- Hard maximum: 6,000 characters.
- Minimum useful chunk: 80 characters, but allow shorter chunks for contacts, notices, dates, and committee entries.
- Overlap: 0 for structured blocks; 150-250 characters only when splitting a long paragraph or long publication list.

### Page-Specific Chunking Rules

Admissions and fees:

- Keep fee rows, eligibility rules, important dates, and procedure steps intact.
- Avoid splitting a fee table or deadline list across chunks.
- Prefer smaller chunks around each fee category, program, or admission section.

Curriculum:

- Chunk by program, batch, semester, or curriculum group when detectable.
- Preserve course-code and program labels in the same chunk.

Faculty and staff:

- Chunk by person or compact profile group.
- Keep name, designation, email, phone, department, and research areas together.

Committees and contacts:

- Chunk by committee or office.
- Keep role, name, email, phone, and responsibility together.
- Do not drop short chunks if they contain email, phone, designation, or office names.

Notices and events:

- Chunk by notice/event item when possible.
- Preserve title, date, attachment/link text, and short description together.

Placements:

- Keep statistics tables or year-wise summaries intact.
- Chunk by year, branch, or placement section.

Publications:

- Avoid letting large publication pages dominate Chroma.
- Chunk by publication group or department.
- Cap the number of chunks per publication-heavy page unless the page is high-value.

General pages:

- Split on heading-like boundaries first.
- Fall back to recursive character splitting only for long unstructured text.

### Section Detection From Flat Text

Because the current JSON schema stores plain text, infer sections conservatively:

- Treat lines or spans ending with `:` as possible headings.
- Treat known labels as section boundaries:
  - `Admission Procedure`
  - `Eligibility`
  - `Fee Details`
  - `Important Dates`
  - `Programmes`
  - `Faculty`
  - `Contact`
  - `Placements`
  - `Research`
  - `Publications`
  - `Notices`
- If no reliable boundaries exist, use paragraph/block grouping.

Do not overfit section parsing. The first V2 should improve chunk quality without requiring scraper schema changes.

## 2. Metadata Schema

### Required Chunk Metadata

Every Chroma record should store:

```json
{
  "schema_version": "ingest_v2",
  "source_type": "html",
  "source_file": "www.juit.ac.in_example.json",
  "url": "https://www.juit.ac.in/example",
  "canonical_url": "https://www.juit.ac.in/example",
  "title": "Example Page",
  "page_id": "sha256 canonical url",
  "page_type": "admissions",
  "department": "cse_it",
  "chunk_index": 0,
  "chunk_count": 5,
  "chunk_id": "deterministic id",
  "chunk_type": "section",
  "section": "Fee Details",
  "content_hash": "sha256 normalized full page content",
  "chunk_hash": "sha256 normalized chunk text",
  "content_chars": 4200,
  "chunk_chars": 900,
  "ingested_at": "ISO timestamp"
}
```

### Optional Metadata

Add these when detectable:

```json
{
  "academic_year": "2026-27",
  "audience": "prospective_students",
  "priority": 80,
  "is_current": true,
  "is_duplicate": false,
  "duplicate_of": null,
  "quality_score": 0.87,
  "has_email": true,
  "has_phone": true,
  "has_table_like_content": true
}
```

### Department Detection

Infer department from URL and title:

- `cse_it`
- `ece`
- `civil`
- `biotech_bioinformatics`
- `mathematics`
- `physics_materials_science`
- `hss`
- `library`
- `central`

Keep `central` as the default for admissions, fees, calendar, authorities, public disclosure, and general university pages.

### Priority Metadata

Store a numeric `priority` field for later source ranking.

Suggested defaults:

- Admissions, fees, curriculum, academic calendar: `100`
- Public disclosure, NIRF, NAAC, authorities: `90`
- Departments, faculty, staff, committees, placements: `80`
- Library and student services: `70`
- Publications and events: `50`
- Alumni, gallery, utility, low-value pages: `10-30`

This should not replace retrieval scoring, but it enables reranking.

## 3. Duplicate Prevention

### URL-Level Deduplication

Canonicalize all URLs before ingestion:

- remove `:443`
- remove trailing `%20`
- remove trailing slash except root
- normalize scheme and host
- remove fragments
- preserve meaningful query params only if needed

Use `canonical_url` as the page identity.

### File-Level Deduplication

Before chunking:

1. Load all page JSON files.
2. Build a map by `canonical_url`.
3. If multiple files map to the same canonical URL:
   - keep the record with the best title quality and largest useful content length
   - mark the others as skipped duplicates in the ingest report

### Content-Level Deduplication

Compute `content_hash` from normalized page content.

If different URLs have identical or near-identical content:

- keep the canonical or higher-priority URL
- skip exact duplicate content from Chroma
- log duplicate groups

Known duplicate patterns from the dataset review should be explicitly handled:

- `:443` copies
- `%20` URL copies
- trailing slash copies
- `index.php` / `index.html` aliases
- alumni login/profile shells
- duplicate publication pages

### Chunk-Level Deduplication

Compute `chunk_hash` from normalized chunk body without the metadata header.

Before adding/upserting:

- skip chunks whose `chunk_hash` already exists for the same `canonical_url`
- optionally skip globally duplicate chunks if they are boilerplate-like

This prevents repeated sidebars, footer remnants, and repeated publication/list sections from dominating retrieval.

### Stable IDs

Use deterministic IDs:

```text
ingest_v2:<page_id>:<chunk_hash_prefix>
```

If strict chunk ordering is needed:

```text
ingest_v2:<page_id>:<chunk_index>:<chunk_hash_prefix>
```

The preferred ID should include content hash so unchanged chunks keep stable identities across rebuilds.

## 4. Re-Indexing Strategy

### Supported Modes

Ingestion V2 should support three operational modes:

1. `rebuild`
   - delete and recreate the V2 Chroma collection
   - ingest all eligible records
   - safest mode after scraper upgrades or metadata schema changes

2. `refresh`
   - load all current page JSON files
   - delete records for pages that no longer exist
   - upsert changed pages
   - leave unchanged pages untouched

3. `single-file`
   - re-ingest one JSON file
   - delete old chunks for that file/page first
   - upsert new chunks

### Recommended Initial Migration Mode

Use full `rebuild` for the first V2 index.

Reason:

- scraper output changed
- title quality changed
- canonical URLs changed
- chunking strategy will change
- metadata schema will change
- old chunks contain navigation pollution and duplicate records

### Refresh Algorithm

For incremental refresh:

1. Build current source manifest:
   - canonical URL
   - source file
   - content hash
   - title
   - page type
2. Read existing manifest from Chroma or local `data/ingest_manifest.json`.
3. Determine:
   - new pages
   - changed pages
   - unchanged pages
   - deleted pages
4. For deleted pages:
   - delete records by `page_id` or `canonical_url`
5. For changed pages:
   - delete old chunks by `page_id`
   - chunk current content
   - upsert new records
6. For unchanged pages:
   - skip
7. Write an ingest report.

### Error Handling

Do not let one bad page abort the entire run.

For each file, report:

- `ingested`
- `skipped_duplicate`
- `skipped_low_quality`
- `skipped_utility`
- `failed_json`
- `failed_chunking`
- `failed_chroma`

At the end, print and save:

- total files
- eligible files
- skipped files
- chunks created
- chunks upserted
- chunks deleted
- failures
- duplicate groups

## 5. Chroma Collection Design

### Collection Names

Do not overwrite the existing collection during development.

Use:

```text
juit_knowledge_v2
```

Keep the existing collection:

```text
juit_knowledge
```

This allows side-by-side comparison before switching retrieval.

### Embedding Function

Use the same embedding model initially:

```text
all-MiniLM-L6-v2
```

Reason:

- isolates ingestion changes from model changes
- allows fair V1 vs V2 comparison
- avoids changing retriever behavior too much at once

Move embedding initialization inside runtime functions instead of module import scope so model-loading errors are reported cleanly.

### Collection Metadata

Store collection-level metadata where supported:

```json
{
  "schema_version": "ingest_v2",
  "embedding_model": "all-MiniLM-L6-v2",
  "source": "data/pages",
  "chunking": "semantic_blocks_v1",
  "created_by": "backend/app/ingest.py"
}
```

### Record Design

Chroma document:

```text
Title: Fee Details 2026-27 Admissions - Indian Students
URL: https://www.juit.ac.in/fee-detail-2026-indian-students
Section: Hostel Charges

<clean chunk text>
```

Chroma metadata:

- keep scalar-only values compatible with Chroma filters
- avoid nested dicts/lists in metadata
- stringify dates and booleans if needed
- keep full structured diagnostics in a separate manifest/report if Chroma metadata becomes restrictive

### Query Compatibility

The retriever can initially switch from `juit_knowledge` to `juit_knowledge_v2` with minimal changes later.

Metadata fields `title`, `url`, and `chunk_index` should remain present so existing API response behavior can continue.

## 6. Migration Plan

### Phase 0: Preconditions

Confirm scraper V2 Phase 1/2 output has been regenerated into `data/pages`.

Before ingestion:

- verify no pages start with main site navigation
- verify department pages do not start/end with `Related Links`
- verify common titles are no longer mostly `Index` or `Untitled`
- keep the current JSON schema unchanged

### Phase 1: Add Ingestion V2 Behind Existing V1

Implement V2 functions in `backend/app/ingest.py` or a new internal module later, but do not remove V1 until V2 is validated.

Required functions:

- `canonicalize_url`
- `load_pages`
- `classify_page_type`
- `detect_department`
- `quality_score_page`
- `build_chunks`
- `build_metadata`
- `build_chunk_id`
- `rebuild_collection`
- `refresh_collection`
- `write_ingest_report`

### Phase 2: Build `juit_knowledge_v2`

Run a full rebuild into `juit_knowledge_v2`.

Expected outputs:

- Chroma collection with V2 chunks
- local ingest report
- local ingest manifest
- duplicate report
- skipped-page report

Do not point production retrieval to V2 yet.

### Phase 3: Validate V2

Compare V1 and V2 using representative queries:

- admissions process
- fee details
- hostel charges
- academic calendar
- course curriculum
- faculty contacts
- committee contacts
- placement details
- department labs
- NIRF/public disclosure

Metrics:

- relevant source appears in top 3
- top chunks do not contain menu/footer/sidebar text
- sources have meaningful titles
- duplicate pages do not crowd results
- contact/date/table answers preserve required facts

### Phase 4: Switch Retriever

After validation, update retrieval later to use:

```text
juit_knowledge_v2
```

Keep `juit_knowledge` until rollback is no longer needed.

### Phase 5: Remove or Archive V1

After V2 is stable:

- archive old collection
- document rebuild command
- document refresh command
- make V2 the default collection name, or keep explicit versioning

### Phase 6: Future Improvements

After V2 is working, consider:

- PDF ingestion for brochures, notices, academic calendars, syllabi, and statutory disclosures
- hybrid retrieval with BM25 plus Chroma
- reranking using metadata priority and recency
- section-aware citations in RAG context
- structured scraper output with real `sections`, `tables`, and `links`

## Recommended Implementation Order

1. Add URL/content canonicalization and duplicate manifest.
2. Add page type and department detection.
3. Implement semantic-block chunking with page-specific rules.
4. Add V2 metadata schema.
5. Create deterministic chunk IDs.
6. Add full rebuild mode for `juit_knowledge_v2`.
7. Add ingest report and error summaries.
8. Validate retrieval quality against V1.
9. Switch retriever only after validation.

## Expected Impact

- Cleaner top-k retrieval because navigation/sidebar chunks are no longer indexed.
- Better exact and semantic matches because chunks carry title, page type, section, and canonical URL.
- Lower duplicate pressure in Chroma because canonical URL, content hash, and chunk hash are enforced.
- Safer re-runs because ingestion becomes idempotent.
- Better RAG grounding because each chunk has enough source context to stand alone.
- Easier future ranking because metadata captures page type, department, priority, and freshness signals.
