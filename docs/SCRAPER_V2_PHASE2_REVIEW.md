 Review the output of Scraper v2 Phase 1.

  Observed issues:

  * Some pages still start with "Related Links"
  * Some department pages still contain sidebar navigation
  * Content quality improved significantly

  Analyze:

  1. Remaining navigation pollution
  2. How to remove "Related Links" blocks
  3. Whether JUIT uses a common sidebar structure
  4. Minimal changes needed before a full re-scrape

  Do NOT write code.

  Return only recommendations.


• I’ll do a read-only check for “Related Links” and sidebar patterns
  in the scraped JSON and current scraper, then give recommendations
  only.

• Explored
  └ Read scraper.py
    Search Related Links|related links|sidebar|side-bar|bio-left|
           department in pages

• Searching the web

• Searched the web for https://www.juit.ac.in/ece-latest-updates

──────────────────────────────────────────────────────────────────────

• Recommendations

  1. Treat Related Links as a navigation block, not content. It is
     still entering output because it is inside or adjacent to the
     selected content area, so tag/class removal alone will not catch
     it.

  2. Remove Related Links at the block level before text extraction:
      - Find headings or text nodes whose normalized text is exactly
        Related Links.

      - Remove that heading plus the immediately associated ul, ol, or
        parent container.

      - If the block is not cleanly wrapped, remove following siblings
        until the next real content heading.

      - Keep this rule exact; do not remove generic “important links”
        globally because admissions/curriculum pages may contain
        useful official links.

  3. Add a conservative text fallback for pages where DOM structure is
     poor:
      - If extracted text contains Related Links followed by known
        department menu items like Programmes & Courses, Laboratories
        & Tools, Faculty, Technical Staff, Placements, Publications,
        Research Groups, Notices/Circulars, remove from Related Links
        onward.

      - If content starts with Related Links, skip the page unless
        meaningful content remains after removal.

  4. Yes, JUIT appears to use a common department sidebar structure.
     Department pages expose a repeated Related Links navigation menu
     with department-local links. On ECE pages, this block appears
     after the main content in the rendered text, with repeated
     entries such as Programmes & Courses, Laboratories & Tools,
     Faculty, Technical Staff, Placements, Publications, and
     Notices/Circulars. Source checked:
     https://www.juit.ac.in/ece-latest-updates

  5. Extend removal patterns carefully, but avoid broad deletion:
      - Add exact handling for Related Links.
      - Add class/id patterns only if confirmed in HTML, such as
        related, related-links, quick-links, department-menu, dept-
        menu, left-sidebar, right-sidebar.

      - Do not blindly remove every element containing links; that can
        delete useful curriculum, fee, admissions, notice, and
        download content.

  6. Do not change the JSON schema before the re-scrape. Keep url,
     title, and content unchanged so ingest.py remains compatible.

  7. Minimal changes before full re-scrape:
      - Add DOM removal for exact Related Links blocks.
      - Add text-level fallback removal for department sidebar
        phrases.

      - Add a post-clean quality gate: skip pages where cleaned
        content is mostly sidebar text or under the existing minimum
        length.

      - Keep the current improved title extraction and
        canonicalization.

  8. Re-scrape strategy:
      - Because the scraper skips existing JSON files, a full re-
        scrape requires clearing or moving the current data/pages
        output first, or temporarily scraping to a fresh directory.

      - Re-scrape after the Related Links fix, then spot-check
        department pages first: ECE, CSE/IT, Civil, Biotechnology/
        Bioinformatics, Mathematics, Physics, HSS.

      - Only rebuild Chroma after confirming the cleaned files no
        longer start or end with department sidebar navigation.

  9. Expected impact:
      - High for department queries, because repeated department
        sidebars currently pollute embeddings.

      - Medium for general pages, since header/footer cleanup already
        improved quality significantly.

      - High for source ranking, because fewer chunks will match
        generic department navigation terms instead of actual page
        content.
