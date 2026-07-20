from pathlib import Path
import json
import hashlib

BASE_DIR = Path(__file__).resolve().parents[3]

PDF_METADATA = BASE_DIR / "data" / "pdf_metadata" / "pdf_links.json"

PDF_DIR = BASE_DIR / "data" / "documents" / "pdf"


def filename_from_url(url: str):
    """
    Generates exactly the same filename used by downloader.py
    """

    return hashlib.sha256(url.encode()).hexdigest() + ".pdf"


class PDFIndex:

    def __init__(self):

        self.index = {}

        self.load()

    def load(self):

        if not PDF_METADATA.exists():
            return

        with open(PDF_METADATA, encoding="utf-8") as f:
            records = json.load(f)

        for item in records:

            filename = filename_from_url(item["url"])

            self.index[filename] = {

                "url": item["url"],

                "title": item.get("title", ""),

                "source_page": item.get("source_page", "")

            }

    def lookup(self, filename):

        return self.index.get(filename, {})


pdf_index = PDFIndex()