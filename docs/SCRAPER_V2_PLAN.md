› Review backend/app/scraper.py.

  Using:

  docs/SCRAPER_REVIEW.md
  docs/DATASET_REVIEW.md
  docs/CHUNKING_REVIEW.md

  Design Scraper v2.

  Do NOT write code.

  Provide:

  1. New extraction pipeline
  2. DOM elements to remove
  3. Better title extraction strategy
  4. Metadata schema
  5. Navigation/header/footer removal strategy
  6. JUIT-specific selectors to prioritize
  7. Migration plan from v1 to v2
  8. Expected retrieval impact

  Output only a detailed implementation plan.


• I’ll read the current scraper and the three review docs, then
  synthesize a v2 implementation plan without touching files.

• Explored
  └ Read SCRAPER_REVIEW.md, scraper.py, DATASET_REVIEW.md,
         CHUNKING_REVIEW.md

• Searching the web

• Searched the web for site:juit.ac.in JUIT admissions bio-left div
  class content

• Searching the web

• Searched the web for https://www.juit.ac.in/juit-admissions

• Searching the web

• Searched the web for
  https://www.juit.ac.in/fee-detail-2026-indian-students

──────────────────────────────────────────────────────────────────────

• Scraper V2 Implementation Plan

  1. New Extraction Pipeline

  Build Scraper v2 as a staged pipeline, not a single soup.get_text()
  pass.

  1. URL intake and canonicalization
      - Read URLs from the discovered/filtered URL list.
      - Normalize before fetching:
          - remove default port :443
          - strip trailing spaces and encoded %20
          - normalize trailing slashes
          - lowercase scheme/host
          - preserve meaningful path segments
          - drop tracking query params, but keep query params only if
            they change page identity

      - Compute:
          - raw_url
          - canonical_url
          - url_path
          - url_slug
          - source_domain

  2. Fetch and classify response
      - Fetch with timeout, retry policy, and status capture.
      - Accept only HTML for this scraper path.
      - Record:
          - HTTP status
          - content type
          - final URL after redirects
          - response size
          - fetch timestamp
          - failure reason if skipped

      - Route PDFs and documents to a future document-ingestion path
        instead of silently ignoring them.

  3. Parse HTML
      - Use BeautifulSoup/lxml.
      - Remove non-content elements globally before choosing content.
      - Normalize whitespace, HTML entities, repeated spaces, non-
        breaking spaces, and broken line joins.

  4. Page type detection
     Assign a page_type before extraction using URL path, title
     candidates, headings, and DOM patterns:
      - admissions
      - fee_details
      - academic_calendar
      - curriculum
      - department
      - faculty_profile
      - staff_directory
      - committee
      - notices
      - placements
      - public_disclosure
      - library
      - publication_list
      - event
      - gallery
      - alumni
      - utility
      - unknown

  5. Main content selection
      - Prefer JUIT-specific containers first.
      - Then use semantic containers.
      - Then use a scored-content fallback.
      - Avoid full-page fallback unless a quality score proves most
        boilerplate has been removed.

  6. Structured extraction
     Extract a document model, not only one text string:
      - page title
      - breadcrumbs
      - section headings
      - paragraphs
      - lists
      - tables
      - important links
      - contact blocks
      - notices/dates
      - attachments
      - image alt text only when meaningful

  7. Boilerplate detection
      - Remove known repeated menu/footer fragments.
      - Detect repeated text blocks across pages by hash/frequency.
      - Drop blocks appearing on many unrelated pages unless
        whitelisted.

  8. Quality scoring and exclusion
     Compute:
      - content length
      - boilerplate ratio
      - link density
      - title quality
      - section count
      - table/list presence
      - duplicate hash
      - page type confidence
      - ingestion eligibility
      - manual review reason

  9. Output dataset record
     Save one JSON file per canonical page with structured fields and
     extracted text.
     Keep old url, title, content compatibility fields during
     migration, but add v2 fields.

  10. Emit crawl report
     Generate a summary report with:

  - fetched
  - skipped
  - failed
  - duplicates
  - excluded from ingestion
  - manual review
  - changed content hash
  - high-noise pages

  2. DOM Elements To Remove

  Remove these before selecting the main content:

  - script
  - style
  - noscript
  - template
  - svg
  - canvas
  - iframe
  - object
  - embed
  - video
  - audio
  - form
  - input
  - button
  - select
  - textarea
  - header
  - nav
  - footer
  - aside

  Remove nodes by common class/id patterns:

  - menu
  - navbar
  - nav
  - navigation
  - header
  - topbar
  - footer
  - sidebar
  - breadcrumb
  - breadcrumbs
  - social
  - share
  - login
  - register
  - search
  - enquire
  - popup
  - modal
  - cookie
  - banner
  - slider
  - carousel
  - owl-carousel
  - captcha
  - counter
  - copyright

  Remove hidden or inactive nodes:

  - [hidden]
  - [aria-hidden="true"]
  - inline style containing display:none
  - inline style containing visibility:hidden
  - collapsed mobile menus where class indicates hidden state

  Remove repeated JUIT boilerplate text blocks:

  - top utility links such as “Enquire”
  - “Research & Innovation”
  - “JUIT Exclusive”
  - “Campus/ Facilities”
  - “Student Activities”
  - “Downloads”
  - “Grievances Redressal”
  - main menu groups such as “About Us”, “Academic Departments”,
    “Programs”, “Admissions”, “Training”, “Placement”, “ALUMNI”,
    “Careers”, “Contact Us”

  - footer groups such as “Important linkages”, “Academic
    Departments”, “Admissions”, “Training”, “Contact Us”

  - copyright and counter text
  - “Website Last Updated...” should be stored as metadata, not mixed
    into content

  3. Better Title Extraction Strategy

  Use a ranked title strategy instead of relying on <title>.

  Priority order:

  1. First meaningful h1 inside the selected main content.
  2. Breadcrumb final item when it is not “Home” and not a section
     label.

  3. Prominent content heading:
      - h2
      - .page-title
      - .title
      - .heading
      - .content-title
      - .inner-title
      - .bio-left h1/h2

  4. URL-derived title as fallback.
  5. HTML <title> only after cleanup.

  Title cleanup rules:

  - Strip suffixes:
      - - JUIT
      - | JUIT
      - Jaypee University Of Information Technology
      - duplicated site name

  - Reject generic titles:
      - Index
      - Untitled
      - Home
      - Welcome
      - LRC - JUIT when page path gives a better title

  - Normalize case carefully:
      - preserve acronyms like CSE, IT, ECE, MBA, B.Tech, M.Tech, PhD,
        NIRF

      - avoid title-casing already-correct official headings

  - If the title is generic, derive from:
      - final breadcrumb
      - URL slug
      - first content heading
      - first strong table/list heading

  Examples:

  - /fee-detail-2026-indian-students -> Fee Details 2026-27 Admissions
    - Indian Students

  - /coursescurriculum -> Course Curriculum
  - /alumni/view-profile/712 should likely be excluded or titled as an
    alumni profile only if profile content is real

  - /lrc-publications -> LRC Publications, not LRC - JUIT

  4. Metadata Schema

  Use a v2 dataset schema that supports retrieval, cleanup,
  deduplication, and citations.

  Top-level fields:

  {
    "schema_version": "scraper_v2",
    "raw_url": "",
    "canonical_url": "",
    "final_url": "",
    "source_domain": "www.juit.ac.in",
    "url_path": "",
    "url_slug": "",
    "title": "",
    "title_source": "h1|breadcrumb|content_heading|url|html_title",
    "html_title": "",
    "breadcrumbs": [],
    "page_type": "",
    "department": "",
    "audience": "",
    "academic_year": "",
    "published_date": "",
    "updated_date": "",
    "website_last_updated": "",
    "crawl_timestamp": "",
    "http_status": 200,
    "content_type": "text/html",
    "language": "en",
    "content_hash": "",
    "raw_text_hash": "",
    "canonical_duplicate_of": null,
    "quality": {
      "content_chars": 0,
      "useful_text_chars": 0,
      "boilerplate_ratio": 0.0,
      "link_density": 0.0,
      "title_quality": "good|generic|missing",
      "extraction_confidence": 0.0,
      "page_type_confidence": 0.0,
      "ingest_eligible": true,
      "manual_review": false,
      "review_reasons": []
    },
    "content": "",
    "sections": [],
    "tables": [],
    "links": [],
    "attachments": []
  }

  Section fields:

  {
    "section_id": "",
    "heading": "",
    "heading_level": 2,
    "text": "",
    "items": [],
    "links": [],
    "tables": [],
    "char_start": 0,
    "char_end": 0
  }

  Table fields:

  {
    "table_id": "",
    "caption": "",
    "section_heading": "",
    "headers": [],
    "rows": [],
    "normalized_text": "",
    "table_type": "fees|placements|curriculum|contacts|generic"
  }

  Link fields:

  {
    "text": "",
    "href": "",
    "absolute_url": "",
    "file_type": "",
    "is_external": false,
    "section_heading": ""
  }

  Recommended metadata values:

  - department values:
      - cse_it
      - ece
      - civil
      - biotech_bioinformatics
      - mathematics
      - physics_materials_science
      - hss
      - library
      - central

  - audience values:
      - prospective_students
      - current_students
      - faculty
      - staff
      - alumni
      - public

  - page_type should be used downstream for chunking and ranking.

  5. Navigation/Header/Footer Removal Strategy

  Use three layers.

  Layer 1: DOM removal

  - Remove semantic tags and known layout classes before content
    selection.

  - This prevents the current failure mode where top navigation
    appears before the actual page heading. Live JUIT pages show heavy
    navigation before content; for example, admissions content starts
    only after long menu and breadcrumb blocks, around the actual #
    Admission heading. Source: https://www.juit.ac.in/juit-admissions

  Layer 2: main content isolation

  - After global removal, locate the best content container by scoring
    candidates.

  - Candidate score should reward:
      - heading count
      - paragraph length
      - table/list presence
      - low link density
      - proximity to h1
      - presence of page-specific keywords from URL/title

  - Candidate score should penalize:
      - high repeated-link count
      - many known menu labels
      - footer labels
      - social links
      - very high link-to-text ratio
      - repeated across many pages

  Layer 3: text-block boilerplate filter

  - Split extracted content into blocks.
  - Hash normalized blocks.
  - Build a corpus-level frequency table.
  - Remove blocks appearing above a threshold across unrelated pages.
  - Keep repeated official content only if page type expects it, such
    as admissions link lists or important notices.

  Special handling:

  - Breadcrumbs should be extracted separately, then removed from body
    text.

  - “Important linkages” footer section should be removed from body
    text. If needed, keep its links in metadata with is_footer_link:
    true.

  - “Website Last Updated on ...” should populate
    website_last_updated, not be embedded in content.

  - Header/menu labels should never enter Chroma content.

  6. JUIT-Specific Selectors To Prioritize

  Content selectors, in order:

  1. div.bio-left
      - Already used in v1 and likely relevant for some JUIT
        templates.

  2. main
  3. article
  4. div#content
  5. div.content
  6. .content
  7. .main-content
  8. .inner-content
  9. .page-content
  10. .entry-content
  11. .news-detail
  12. .notice-detail
  13. .department-content
  14. .profile-content
  15. .faculty-profile
  16. table/list container near the page h1

  Heading selectors:

  1. selected-content h1
  2. selected-content h2
  3. .page-title
  4. .inner-title
  5. .title
  6. .heading
  7. .content-title
  8. breadcrumb final item

  Remove/avoid selectors and class/id patterns:

  - header
  - nav
  - footer
  - aside
  - .navbar
  - .main-menu
  - .menu
  - .dropdown
  - .top-header
  - .topbar
  - .site-header
  - .site-footer
  - .footer
  - .sidebar
  - .breadcrumb
  - .social
  - .search
  - .login
  - .register
  - .enquire
  - .important-linkages
  - .counter
  - .copyright

  JUIT content patterns to prioritize:

  - Admissions pages:
      - headings containing Admission, B.Tech, M.Tech, MBA, PhD,
        Important Dates, Fee Details

      - links to brochures, application forms, admission procedures

  - Fee pages:
      - tables or table-like rows containing Tuition Fees, Hostel
        Charges, Caution Money, Admission Charges

      - the live fee page has the real page content after
        breadcrumb/menu blocks under FEE DETAILS 2026-27 ADMISSIONS
        (INDIAN STUDENTS). Source:
        https://www.juit.ac.in/fee-detail-2026-indian-students

  - Curriculum pages:
      - grouped lists by batch/year and program
      - links to course PDFs
      - the live curriculum page has useful grouped program links
        after the Course Curriculum heading. Source:
        https://www.juit.ac.in/coursescurriculum

  - Placement pages:
      - tables with branch, eligible students, offers, percentages,
        salary highlights

  - Department pages:
      - faculty, labs, projects, publications, visitors, board of
        studies

  - Committee/contact pages:
      - names, roles, emails, phone numbers

  - Notice pages:
      - notice title, date, attachment links

  - Library/LRC pages:
      - services, publications, resources, membership, timings

  7. Migration Plan From V1 To V2

  Phase 1: Baseline current data

  - Freeze current data/pages as v1 input.
  - Generate a read-only quality report:
      - total pages
      - generic titles
      - duplicate canonical URLs
      - navigation-heavy pages
      - low-content pages
      - excluded pages

  - Use the existing findings as baseline:
      - 548 JSON pages
      - many Untitled and Index titles
      - duplicate :443, %20, trailing-slash, and index-page variants
      - navigation-heavy official pages requiring re-scrape/cleanup

  Phase 2: Add v2 output location

  - Write v2 records to a separate dataset path, for example:
      - data/pages_v2

  - Do not overwrite v1 initially.
  - Keep compatibility fields:
      - url
      - title
      - content

  - Add v2 metadata and structured fields.

  Phase 3: URL canonicalization and dedupe

  - Normalize all discovered URLs before scraping.
  - Build a canonical URL map.
  - Skip exact canonical duplicates.
  - Record duplicate relationships in metadata.
  - Explicitly handle known duplicate patterns:
      - https://www.juit.ac.in:443/...
      - trailing %20
      - trailing slash copies
      - index.php / index.html aliases
      - alumni login/profile shells

  Phase 4: Implement page-type routing

  - Start with high-value page types:
      - admissions
      - fees
      - curriculum
      - academic calendar
      - placements
      - departments
      - faculty/staff
      - committees
      - notices
      - public disclosure

  - Exclude or manually review:
      - alumni login/account pages
      - thank-you pages
      - privacy/terms pages
      - gallery shells
      - placeholder pages
      - pure navigation pages

  Phase 5: Structured extraction

  - Preserve headings, lists, tables, and links.
  - Convert tables into both structured rows and readable normalized
    text.

  - Keep section boundaries for downstream chunking.
  - Store attachment links for future PDF ingestion.

  Phase 6: Quality gate

  - Mark each page:
      - ingest_eligible: true|false
      - manual_review: true|false
      - review_reasons

  - Exclude from Chroma:
      - duplicate pages
      - utility/account/legal pages
      - alumni login/profile shells
      - pages with high boilerplate and low useful text
      - empty or generic title pages unless content is clearly useful

  Phase 7: Compare v1 and v2

  - For each canonical URL, compare:
      - title quality
      - content length
      - boilerplate ratio
      - first 300 characters
      - section count
      - table/list preservation

  - Manually inspect high-value pages:
      - admissions
      - fees
      - programs on offer
      - curriculum
      - academic calendar
      - placements
      - staff
      - authorities
      - committees

  Phase 8: Rebuild ingestion pipeline after v2 validation

  - Update ingestion later to consume pages_v2.
  - Use metadata-driven chunking:
      - page title
      - section heading
      - page type
      - canonical URL
      - table/list markers

  - Rebuild Chroma from scratch after validating v2.
  - Do not mix v1 and v2 chunks in the same collection unless a schema
    version filter is added.

  Phase 9: Retrieval regression test

  - Build a small evaluation set before switching:
      - admission deadlines
      - fee amounts
      - hostel charges
      - B.Tech programs
      - curriculum links
      - placement stats
      - committee contacts
      - department faculty
      - academic calendar

  - Compare v1 vs v2:
      - correct source in top 3
      - answerable context
      - no menu/footer pollution
      - citation quality
      - duplicate source reduction

  8. Expected Retrieval Impact

  High-impact improvements:

  - Cleaner embeddings
      - Removing navigation/header/footer text will stop repeated menu
        phrases from dominating vector similarity.

      - Queries for admissions, departments, placements, committees,
        and fees should retrieve real content instead of page chrome.

  - Better exact and semantic title matching
      - Replacing Index and Untitled with meaningful titles will
        improve exact-title lookup, source display, and reranking.

  - Better chunking downstream
      - Preserved sections and tables will allow chunking by semantic
        units instead of arbitrary character windows.

      - Fee tables, curriculum lists, contacts, and placement stats
        will become more retrievable.

  - Lower duplicate pollution
      - Canonical URL dedupe will reduce duplicate chunks from :443,
        %20, trailing-slash, and index variants.

      - Fewer duplicate chunks means more diverse top-k results.

  - Better source ranking
      - Metadata such as page_type, department, academic_year,
        updated_date, and quality enables ranking official, current,
        high-value pages above archives and shells.

  - Better answer grounding
      - Structured source records let RAG context include title,
        section heading, URL, and table labels.

      - This should reduce hallucinations caused by context blobs with
        no boundaries.

  - Better exclusion control
      - ingest_eligible and manual_review prevent low-value account,
        alumni login, utility, and placeholder pages from entering

  Primary success criteria:


  - Sources have meaningful titles.
  - Duplicate canonical pages are not indexed multiple times.
  - Fee/curriculum/table answers retrieve the correct table section.
  - Utility and login pages are excluded before Chroma ingestion.
