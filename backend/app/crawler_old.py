from collections import deque
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

START_URL = "https://www.juit.ac.in/"

visited = set()
queue = deque([START_URL])

discovered = set()

MAX_PAGES = 100

while queue and len(visited) < MAX_PAGES:

    url = queue.popleft()

    if url in visited:
        continue

    visited.add(url)

    try:
        print(f"[CRAWL] {url}")

        response = requests.get(url, timeout=15)

        soup = BeautifulSoup(response.text, "lxml")

        for a in soup.find_all("a", href=True):

            href = a["href"]

            absolute_url = urljoin(url, href)

            if not absolute_url.startswith(
                "https://www.juit.ac.in"
            ):
                continue

            if (
                "webportal" in absolute_url
                or "webmail" in absolute_url
                or "lms." in absolute_url
            ):
                continue

            if absolute_url not in visited:

                discovered.add(absolute_url)
                queue.append(absolute_url)

    except Exception as e:
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
