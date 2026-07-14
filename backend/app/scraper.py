import json
import logging
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)

# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Paths
DATA_DIR = BASE_DIR / "data" / "pages"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Use discovered URLs instead of seed URLs
SEED_FILE = BASE_DIR / "data" / "discovered_urls.txt"

HEADERS = {
    "User-Agent": "JUIT-AI-Assistant/1.0"
}

REMOVE_TAGS = [
    "script",
    "style",
    "noscript",
    "template",
    "header",
    "nav",
    "footer",
    "aside",
    "form",
    "button",
    "input",
    "select",
    "textarea",
    "iframe",
    "svg",
    "canvas",
]

REMOVE_PATTERN = re.compile(
    r"(nav|menu|header|footer|sidebar|login|search|breadcrumb|"
    r"social|share|popup|modal|cookie|banner|carousel|slider|"
    r"topbar|enquire)",
    re.IGNORECASE,
)

GENERIC_TITLES = {
    "",
    "home",
    "index",
    "untitled",
    "welcome",
    "juit",
}

DEPARTMENT_NAV_LABELS = [
    "programmes & courses",
    "laboratories & tools",
    "faculty",
    "technical staff",
    "placements",
    "publications",
    "research groups",
    "notices/circulars",
]


def canonicalize_url(url: str) -> str:
    url = url.strip().replace("%20", "")
    parts = urlsplit(url)

    netloc = parts.netloc
    if parts.scheme == "https" and netloc.endswith(":443"):
        netloc = netloc[:-4]

    path = parts.path.replace("%20", "")
    if path != "/":
        path = path.rstrip("/")

    return urlunsplit(
        (
            parts.scheme,
            netloc,
            path,
            parts.query,
            "",
        )
    )


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def department_nav_score(text: str) -> int:
    normalized = clean_text(text).lower()
    return sum(label in normalized for label in DEPARTMENT_NAV_LABELS)


def remove_unwanted_elements(soup: BeautifulSoup) -> None:
    for tag in soup(REMOVE_TAGS):
        tag.decompose()

    for tag in soup.find_all(True):

        if not hasattr(tag, "attrs") or tag.attrs is None:
            continue

        marker = " ".join(
            [
                str(tag.attrs.get("id", "")),
                " ".join(tag.attrs.get("class", [])),
                str(tag.attrs.get("role", "")),
            ]
        )

        if REMOVE_PATTERN.search(marker):
            tag.decompose()
            continue

        style = str(tag.attrs.get("style", "")).replace(" ", "").lower()

        if "display:none" in style or "visibility:hidden" in style:
            tag.decompose()


def remove_related_links_blocks(content) -> None:
    for tag in list(content.find_all(True)):
        text = clean_text(tag.get_text(" ", strip=True))
        if not text:
            continue

        normalized = text.lower()
        if "related links" not in normalized:
            continue

        if tag is not content and department_nav_score(text) >= 3:
            tag.decompose()
            continue

        if normalized == "related links":
            sibling = tag.find_next_sibling()
            tag.decompose()

            while sibling:
                next_sibling = sibling.find_next_sibling()
                sibling_text = clean_text(sibling.get_text(" ", strip=True))

                if (
                    sibling.name in {"h1", "h2", "h3", "h4"}
                    and department_nav_score(sibling_text) == 0
                ):
                    break

                if department_nav_score(sibling_text) > 0 or len(sibling_text) < 1000:
                    sibling.decompose()
                    sibling = next_sibling
                    continue

                break


def remove_related_links_text(text: str) -> str:
    marker = re.search(r"\bRelated Links\b", text, flags=re.IGNORECASE)
    if not marker:
        return text

    suffix = text[marker.start():]
    if department_nav_score(suffix) >= 3:
        return clean_text(text[:marker.start()])

    return text


def normalize_title(title: str) -> str:
    title = clean_text(title)
    title = re.sub(
        r"\s*[-|]\s*(JUIT|Jaypee University Of Information Technology)\s*$",
        "",
        title,
        flags=re.IGNORECASE,
    )
    return title.strip()


def is_good_title(title: str) -> bool:
    return normalize_title(title).lower() not in GENERIC_TITLES


def title_from_url(url: str) -> str:
    path = urlsplit(url).path.strip("/")
    slug = path.split("/")[-1] if path else ""
    slug = slug.replace("%20", "")
    slug = re.sub(r"[-_]+", " ", slug)
    return slug.title() if slug else "Untitled"


def find_main_content(soup: BeautifulSoup):
    selectors = [
        ".bio-left",
        "main",
        "article",
        "#content",
        ".content",
        ".main-content",
        ".page-content",
        ".entry-content",
    ]

    for selector in selectors:
        element = soup.select_one(selector)
        if element and len(clean_text(element.get_text(" ", strip=True))) >= 200:
            return element

    return soup.body or soup


def extract_title(content, soup: BeautifulSoup, url: str) -> str:
    for selector in ["h1", "h2"]:
        heading = content.select_one(selector)
        if heading:
            title = normalize_title(heading.get_text(" ", strip=True))
            if is_good_title(title):
                return title

    if soup.title and soup.title.string:
        title = normalize_title(soup.title.string)
        if is_good_title(title):
            return title

    return normalize_title(title_from_url(url))


def output_filename(url: str) -> str:
    return (
        url.replace("https://", "")
        .replace("http://", "")
        .replace("/", "_")
        .replace("?", "_")
        .replace("&", "_")
        + ".json"
    )


def scrape_page(url: str):
    try:
        url = canonicalize_url(url)
        LOGGER.info("Scraping %s", url)

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        # Skip non-HTML content
        if "text/html" not in response.headers.get(
            "Content-Type",
            ""
        ):
            LOGGER.info("Skipping non-HTML page: %s", url)
            return

        soup = BeautifulSoup(
            response.text,
            "lxml"
        )

        remove_unwanted_elements(soup)

        main_content = find_main_content(soup)
        remove_related_links_blocks(main_content)
        title = extract_title(main_content, soup, url)
        text = clean_text(main_content.get_text(" ", strip=True))
        text = remove_related_links_text(text)

        # Skip pages with little content
        if len(text) < 300:
            LOGGER.info("Skipping low-content page: %s", url)
            return

        data = {
            "url": url,
            "title": title,
            "content": text
        }

        output_file = DATA_DIR / output_filename(url)

        # Skip already scraped files
        if output_file.exists():
            LOGGER.info("Skipping existing page: %s", output_file.name)
            return

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

        LOGGER.info("Saved %s", output_file.name)

    except requests.exceptions.RequestException:
        LOGGER.exception("Request failed for %s", url)

    except Exception:
        LOGGER.exception("Failed to scrape %s", url)
def load_seed_urls():

    if not SEED_FILE.exists():
        raise FileNotFoundError(
            f"Seed file not found: {SEED_FILE}"
        )

    with open(
        SEED_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        urls = [
            canonicalize_url(line)
            for line in f
            if line.strip()
        ]

    return sorted(set(urls))


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    urls = load_seed_urls()

    LOGGER.info("Loaded %s URLs", len(urls))

    for url in urls:
        scrape_page(url)

    LOGGER.info("Scraping completed")


if __name__ == "__main__":
    main()
