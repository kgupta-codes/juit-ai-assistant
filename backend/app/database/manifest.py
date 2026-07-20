from pathlib import Path
import hashlib
import json
from datetime import datetime, UTC

from app.database.database import get_connection

ROOT = Path(__file__).resolve().parents[3]

PAGES_DIR = ROOT / "data" / "pages"


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def register_documents():

    conn = get_connection()
    cursor = conn.cursor()

    inserted = 0
    updated = 0
    skipped = 0

    now = datetime.now(UTC).isoformat()

    for file in PAGES_DIR.glob("*.json"):

        try:
            with open(file, "r", encoding="utf-8") as f:
                page = json.load(f)
        except Exception:
            continue

        url = page.get("url", "").strip()

        if not url:
            continue

        title = page.get("title", "").strip()

        content = page.get("content", "")

        content_hash = sha256(content)

        cursor.execute(
            """
            SELECT
                id,
                content_hash
            FROM documents
            WHERE url=?
            """,
            (url,),
        )

        row = cursor.fetchone()

        if row is None:

            cursor.execute(
                """
                INSERT INTO documents
                (
                    url,
                    title,
                    document_type,
                    source_type,
                    content_hash,
                    indexed_at,
                    crawl_time,
                    status,
                    chunks,
                    priority,
                    created_at,
                    updated_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    url,
                    title,
                    "html",
                    "official_juit",
                    content_hash,
                    now,
                    now,
                    "indexed",
                    0,
                    0,
                    now,
                    now,
                ),
            )

            inserted += 1

        else:

            old_hash = row["content_hash"]

            if old_hash == content_hash:
                skipped += 1
                continue

            cursor.execute(
                """
                UPDATE documents
                SET
                    title=?,
                    content_hash=?,
                    indexed_at=?,
                    crawl_time=?,
                    status=?,
                    updated_at=?
                WHERE url=?
                """,
                (
                    title,
                    content_hash,
                    now,
                    now,
                    "updated",
                    now,
                    url,
                ),
            )

            updated += 1

    conn.commit()
    conn.close()

    print()
    print("========== Manifest ==========")
    print(f"Inserted : {inserted}")
    print(f"Updated  : {updated}")
    print(f"Skipped  : {skipped}")
    print("==============================")



if __name__ == "__main__":
    register_documents()