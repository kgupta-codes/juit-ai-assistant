import logging
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
DISCOVERED_URLS_PATH = BASE_DIR / "data" / "discovered_urls.txt"
START_URL = "https://www.juit.ac.in/"
MAX_PAGES = 500
REQUEST_TIMEOUT_SECONDS = 15

SKIP_EXTENSIONS = (
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".zip",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
)

SKIP_MARKERS = (
    "webmail",
    "webportal",
    "login",
    "logout",
    "facebook",
    "twitter",
    "instagram",
    "linkedin",
    "youtube",
)


def normalize_url(url: str) -> str:
    parsed = urlparse(url.split("#")[0])
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def should_visit(url: str) -> bool:
    lowered = url.lower()
    return (
        url.startswith("https://www.juit.ac.in")
        and not lowered.endswith(SKIP_EXTENSIONS)
        and not any(marker in lowered for marker in SKIP_MARKERS)
    )


def discover_urls(start_url: str = START_URL, max_pages: int = MAX_PAGES) -> set[str]:
    visited = set()
    discovered = set()
    queue = deque([start_url])

    while queue and len(visited) < max_pages:
        url = queue.popleft()

        if url in visited:
            continue

        visited.add(url)
        LOGGER.info("Crawling %s", url)

        try:
            response = requests.get(
                url,
                timeout=REQUEST_TIMEOUT_SECONDS,
                headers={"User-Agent": "JUIT-AI-Assistant/1.0"},
            )
            response.raise_for_status()
        except requests.RequestException:
            LOGGER.exception("Failed to crawl %s", url)
            continue

        soup = BeautifulSoup(response.text, "lxml")

        for anchor in soup.find_all("a", href=True):
            absolute_url = normalize_url(urljoin(url, anchor["href"]))

            if not should_visit(absolute_url):
                continue

            if absolute_url not in visited:
                discovered.add(absolute_url)
                queue.append(absolute_url)

    return discovered


def write_urls(urls: set[str], output_path: Path = DISCOVERED_URLS_PATH) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "".join(f"{url}\n" for url in sorted(urls)),
        encoding="utf-8",
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    urls = discover_urls()
    write_urls(urls)
    LOGGER.info("Found %s URLs", len(urls))


if __name__ == "__main__":
    main()
