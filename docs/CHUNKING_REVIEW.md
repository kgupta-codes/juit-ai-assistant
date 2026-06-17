 Review backend/app/chunker.py

  Do NOT modify code.

  Analyze:

  1. Chunk size strategy
  2. Overlap strategy
  3. Table handling
  4. Metadata preservation
  5. Context loss risks

  Provide:
  - Problems
  - Root causes
  - Priority order


• I’m checking whether backend/app/chunker.py exists and, if not, where
  chunking actually lives so I can review the real implementation rather
  than guess. After that I’ll summarize the chunking risks only.

• Explored
  └ List app
    Search chunker|ingest|split
    Read ingest.py, ingest.py.save
    Search RecursiveCharacterTextSplitter|chunk_size|chunk_overlap|
    split_text|
           chunk in app

────────────────────────────────────────────────────────────────────────────

• backend/app/chunker.py does not exist in this repo. The actual chunking
  logic is in backend/app/ingest.py. That file is what this review is based
  on.

  Problems

  1. Chunk size is fixed at 1200 characters with 100 characters overlap.
     That is a blunt default for JUIT content and does not adapt to page
     type. A fee table, a notice, a faculty page, and a publication list
     should not be chunked the same way.

  2. Overlap is too small to reliably preserve context across section
     boundaries, but still large enough to duplicate boilerplate into
     neighboring chunks. On navigation-heavy pages, that increases repeated
     junk without solving semantic continuity.

  3. The splitter is character-based, not structure-based. It can split
     tables, lists, headings, and notices in the middle of a logical unit.

  4. Metadata preservation is minimal. Each chunk keeps only title, url, and
     chunk index at backend/app/ingest.py:75-80. There is no section
     heading, page type, content hash, canonical URL, or table/list
     indicator.

  5. The original page structure is flattened before splitting. The code
     prepends the title and then runs split_text(content) on raw text at
     backend/app/ingest.py:54-57. Once flattened, there is no way to
     reconstruct headings or tables downstream.

  6. Tiny chunks are dropped with a hard 100 character cutoff at backend/
     app/ingest.py:65-67. That can discard useful short answers such as
     office contacts, notice dates, form links, or committee details.

  7. Chunk IDs are positional, not content-based. backend/app/ingest.py:69
     uses file_path.stem plus index, so if chunk boundaries change, IDs
     change and the same content can be duplicated or orphaned across re-
     ingestions.

  8. Chunking does not protect against repeated boilerplate. Since the input
     content already often includes navigation text, the splitter faithfully
     propagates that noise into multiple chunks.

  9. There is no page-type-specific policy. Publication pages, gallery
     pages, alumni pages, committee pages, and admissions pages all need
     different chunking behavior, but the current code applies one global
     rule.

  Root Causes

  1. The ingestion pipeline assumes all JUIT pages have roughly the same
     information density and structure.

  2. It optimizes for implementation simplicity, not retrieval quality.
  3. It uses a generic LangChain splitter without an upstream document
     model.

  4. It stores chunks as plain text strings instead of structured records.
  5. It does not distinguish between semantic content and repeated site
     chrome.

  Priority Order

  1. Replace fixed character chunking with structure-aware chunking by page

  The short version: the current chunker is acceptable for prototype
  retrieval, but for a JUIT assistant it is too coarse and too lossy for
  anything that depends on exact institutional facts.
