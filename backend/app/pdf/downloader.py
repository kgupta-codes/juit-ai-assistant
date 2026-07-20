from pathlib import Path
import hashlib
import json
import mimetypes
import requests
from tqdm import tqdm

from app.database.database import get_connection

ROOT = Path(__file__).resolve().parents[3]

PDF_DIR = ROOT / "data" / "documents" / "pdf"
PDF_DIR.mkdir(parents=True, exist_ok=True)

PDF_METADATA = ROOT / "data" / "pdf_metadata" / "pdf_links.json"


def filename_from_url(url: str):
    ext = Path(url).suffix

    if not ext:
        ext = ".pdf"

    h = hashlib.sha256(url.encode()).hexdigest()

    return h + ext


def register_pdf(conn, url, file_path):

    conn.execute(
        """
        INSERT OR IGNORE INTO documents
        (
            url,
            title,
            document_type,
            status,
            indexed_at,
            chunks
        )
        VALUES
        (?, ?, ?, ?, datetime('now'), 0)
        """,
        (
            url,
            Path(file_path).name,
            "pdf",
            "downloaded",
        ),
    )

    conn.commit()


def download():

    conn = get_connection()

    with open(PDF_METADATA, "r", encoding="utf-8") as f:
        pdfs = json.load(f)

    downloaded = 0
    skipped = 0
    failed = 0

    session = requests.Session()

    for pdf in tqdm(pdfs):

        url = pdf["url"]

        filename = filename_from_url(url)

        output = PDF_DIR / filename

        if output.exists():

            skipped += 1

            register_pdf(
                conn,
                url,
                output
            )

            continue

        try:

            response = session.get(
                url,
                timeout=60
            )

            if response.status_code != 200:

                failed += 1

                continue

            content_type = response.headers.get(
                "content-type",
                ""
            )

            if (
                "pdf" not in content_type.lower()
                and not output.suffix.lower() == ".pdf"
            ):
                failed += 1
                continue

            with open(output, "wb") as f:
                f.write(response.content)

            register_pdf(
                conn,
                url,
                output
            )

            downloaded += 1

        except Exception as e:
            failed += 1
            print(f"\nERROR downloading: {url}")
            print(e)

    conn.close()

    print()

    print(f"Downloaded : {downloaded}")
    print(f"Skipped     : {skipped}")
    print(f"Failed      : {failed}")


if __name__ == "__main__":
    download()