import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

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


def scrape_page(url: str):
    try:
        print(f"[INFO] Scraping: {url}")

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
            print(f"[SKIP] Not HTML: {url}")
            return

        soup = BeautifulSoup(
            response.text,
            "lxml"
        )

        # Remove unwanted tags
        for tag in soup(
            ["script", "style", "noscript"]
        ):
            tag.decompose()

        # Page title
        title = (
            soup.title.string.strip()
            if soup.title and soup.title.string
            else "Untitled"
        )

        # Try extracting main content
        main_content = (
            soup.find("div", class_="bio-left")
            or soup.find("main")
            or soup.find("article")
            or soup.find("section")
            or soup.find("div", class_="content")
            or soup.find("div", id="content")
        )
        if main_content:
            text = main_content.get_text(
                separator=" ",
                strip=True
            )
        else:
            text = soup.get_text(
                separator=" ",
                strip=True
            )

        # Skip pages with little content
        if len(text) < 300:
            print(
                f"[SKIP] Too little content: {url}"
            )
            return

        data = {
            "url": url,
            "title": title,
            "content": text
        }

        filename = (
            url.replace("https://", "")
            .replace("http://", "")
            .replace("/", "_")
            .replace("?", "_")
            .replace("&", "_")
            + ".json"
        )

        output_file = DATA_DIR / filename

        # Skip already scraped files
        if output_file.exists():
            print(
                f"[SKIP] Already exists: {output_file.name}"
            )
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

        print(
            f"[OK] Saved -> {output_file.name}"
        )

    except requests.exceptions.RequestException as e:
        print(f"[REQUEST ERROR] {url}")
        print(e)

    except Exception as e:
        print(f"[ERROR] {url}")
        print(e)


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
            line.strip()
            for line in f
            if line.strip()
        ]

    return urls


def main():

    urls = load_seed_urls()

    print(
        f"[INFO] Loaded {len(urls)} URLs"
    )

    for url in urls:
        scrape_page(url)

    print(
        "\n[INFO] Scraping completed"
    )


if __name__ == "__main__":
    main()
