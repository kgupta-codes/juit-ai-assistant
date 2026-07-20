from pathlib import Path
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[3]

PAGES_DIR = ROOT / "data" / "pages"
OUTPUT_FILE = ROOT / "data" / "pdf_metadata" / "pdf_links.json"

OFFICIAL_DOMAINS = (
    "https://www.juit.ac.in/",
    "https://juit.ac.in/",
)


def discover_pdf_links():
    pdfs = {}

    for file in PAGES_DIR.glob("*.json"):

        try:
            with open(file, "r", encoding="utf-8") as f:
                page = json.load(f)
        except Exception:
            continue

        html = page.get("html", "")
        if not html:
            continue

        source_url = page.get("url", "https://www.juit.ac.in/")

        soup = BeautifulSoup(html, "lxml")

        for a in soup.find_all("a", href=True):

            href = a.get("href", "").strip()

            if ".pdf" not in href.lower():
                continue

            absolute = urljoin(source_url, href)

            # Remove Chrome PDF Viewer prefix
            if absolute.startswith("chrome-extension://"):
                idx = absolute.find("http")
                if idx != -1:
                    absolute = absolute[idx:]

            # Force HTTPS
            absolute = absolute.replace(
                "http://www.juit.ac.in",
                "https://www.juit.ac.in",
            )
            absolute = absolute.replace(
                "http://juit.ac.in",
                "https://juit.ac.in",
            )

            # Keep only official JUIT PDFs
            if not absolute.startswith(OFFICIAL_DOMAINS):
                continue

            pdfs[absolute] = {
                "url": absolute,
                "title": a.get_text(" ", strip=True),
                "source_page": source_url,
            }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            sorted(pdfs.values(), key=lambda x: x["url"]),
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"Discovered {len(pdfs)} official PDF links")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    discover_pdf_links()