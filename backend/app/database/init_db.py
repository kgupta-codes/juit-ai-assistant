from app.database.database import get_connection


def initialize_database():
    conn = get_connection()

    conn.executescript("""
    CREATE TABLE IF NOT EXISTS documents (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    url TEXT UNIQUE,

    title TEXT,

    document_type TEXT,

    source_type TEXT,

    local_path TEXT,

    content_hash TEXT,

    mime_type TEXT,

    file_size INTEGER,

    last_modified TEXT,

    indexed_at TEXT,

    crawl_time TEXT,

    status TEXT,

    chunks INTEGER DEFAULT 0,

    priority INTEGER DEFAULT 0,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
    CREATE TABLE IF NOT EXISTS crawl_history (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        started_at TEXT,

        finished_at TEXT,

        pages_checked INTEGER,

        pages_updated INTEGER,

        pdfs_checked INTEGER,

        pdfs_updated INTEGER,

        errors INTEGER
    );

    CREATE TABLE IF NOT EXISTS failed_jobs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        url TEXT,

        reason TEXT,

        retry_count INTEGER DEFAULT 0,

        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS system_stats (

        key TEXT PRIMARY KEY,

        value TEXT
    );
    """)

    conn.commit()
    conn.close()

    print("Knowledge database initialized.")


if __name__ == "__main__":
    initialize_database()