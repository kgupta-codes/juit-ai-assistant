from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

START_URL = "https://www.juit.ac.in/"

visited = set()
queue = deque([START_URL])

discovered = set()

MAX_PAGES = 500

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

while queue and len(visited) < MAX_PAGES:

    url = queue.popleft()

    if url in visited:
        continue

    visited.add(url)

    try:
        print(f"[CRAWL] {url}")

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "JUIT-AI-Assistant/1.0"
            }
        )

        soup = BeautifulSoup(
            response.text,
            "lxml"
        )

        for a in soup.find_all("a", href=True):

            href = a["href"]

            absolute_url = urljoin(
                url,
                href
            )

            absolute_url = absolute_url.split("#")[0]

            parsed = urlparse(
                absolute_url
            )

            absolute_url = (
                parsed.scheme
                + "://"
                + parsed.netloc
                + parsed.path
            )

            if not absolute_url.startswith(
                "https://www.juit.ac.in"
            ):
                continue

            if absolute_url.endswith(
                SKIP_EXTENSIONS
            ):
                continue

            if any(
                x in absolute_url.lower()
                for x in [
                    "webmail",
                    "webportal",
                    "login",
                    "logout",
                    "facebook",
                    "twitter",
                    "instagram",
                    "linkedin",
                    "youtube",
                ]
            ):
                continue

            if (
                absolute_url
                not in visited
            ):
                discovered.add(
                    absolute_url
                )
                queue.append(
                    absolute_url
                )

    except Exception as e:
        print(
            f"[ERROR] {url}"
        )
        print(e)

with open(
    "data/discovered_urls.txt",
    "w",
    encoding="utf-8"
) as f:

    for url in sorted(discovered):
        f.write(url + "\n")

print(
    f"\nFound {len(discovered)} URLs"
)
