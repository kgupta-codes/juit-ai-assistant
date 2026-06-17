› Review backend/app/scraper.py only.

  Do NOT modify code.

  Analyze:

  1. Why navigation text is being captured
  2. Why titles become Index and Untitled
  3. Which HTML elements should be removed
  4. How a university-specific scraper should work

  Provide:

  - Problems
  - Root causes
  - Recommended architecture
  - Priority order

  No code changes.


• Problems

  1. The scraper is treating page chrome as content. In backend/app/
     scraper.py:60, the extractor only tries a few container selectors and
     then falls back to soup.get_text(...) at backend/app/scraper.py:74-78.
     On JUIT pages, that fallback pulls in menus, headers, footers,
     breadcrumbs, and repeated site navigation.

  2. Title handling is too weak. At backend/app/scraper.py:53-58, it uses
     only soup.title.string and otherwise defaults to Untitled. That
     preserves generic page titles like Index and misses the real page
     heading.

  3. The scraper is not template-aware. The hardcoded container list at
     backend/app/scraper.py:60-67 is too narrow for a university site with
     many page templates, section pages, committee pages, publication pages,
     event pages, and utility pages.

  4. It removes too little structure before text extraction. Only script,
     style, and noscript are removed at backend/app/scraper.py:47-51.

  5. Content quality gating is crude. The len(text) < 300 filter at backend/
     app/scraper.py:80-85 does not distinguish between useful short pages
     and long pages dominated by boilerplate.

  6. The output is flattened into one blob of text. That erases headings,
     lists, tables, and page sections, which are exactly what a university
     assistant needs for admissions, fees, notices, staff, and committees.

  Root Causes

  1. The scraper assumes a small set of generic layout containers instead of
     the real JUIT DOM structure.

  2. It uses title tag text as the page title, not the main page heading or
     a normalized canonical title.

  3. It has no blacklist for common non-content elements such as header,
     nav, footer, aside, form, and modal/utility wrappers.

  4. It has no content-classification step to decide whether a page is a
     notice, publication list, committee page, form page, event page, or
     index page.

  5. It has no cleanup pass for repeated navigation fragments that appear
     across many JUIT templates.

  Which HTML elements should be removed

  At minimum, the scraper should strip these before text extraction:

  - script, style, noscript
  - header, nav, footer, aside
  - form, button, input, select, textarea
  - iframe, svg, canvas
  - modal/popup containers and cookie/banner containers
  - repeated site chrome blocks such as top bars, sidebars, breadcrumbs, and
    social/share blocks

  - hidden or off-screen nodes when present
  - duplicate menu blocks inside the same page template

  Recommended Architecture

  1. Fetch page.
  2. Normalize URL and detect page type.
  3. Remove known non-content DOM regions.
  4. Prefer a page-specific main content container.
  5. Extract structured content, not just raw text:
      - title from h1 or a strong page heading
      - sections from h2/h3
      - tables as structured rows
      - lists as list items

  6. Run boilerplate detection to drop repeated menu text.
  7. Apply a content-quality score and page-type rules.
  8. Save metadata alongside text:
      - canonical URL
      - extracted title
      - page type
      - crawl time
      - content hash
      - source language/department if detectable

  For a university site, the scraper should be page-aware, not just HTML-to-
  text. A good scraper should recognize that admissions pages, notice pages,
  faculty pages, publication pages, and event pages have different
  structures and should be extracted differently.

  Priority Order

  1. Remove navigation and layout chrome before extraction.
  2. Replace title-tag-only logic with heading-based title extraction and
     normalization.

  3. Add a broader DOM blacklist for site boilerplate elements.
  4. Make extraction template-aware by page type.
  5. Preserve structure for tables, lists, and section headings.
  6. Add quality scoring and metadata so downstream ingestion can filter bad
     pages.

  The current scraper is usable as a prototype, but for JUIT it is too blunt
  for reliable RAG input.
