from dataclasses import dataclass


@dataclass
class PDFDocument:
    url: str
    title: str
    source_page: str
    filename: str = ""
    local_path: str = ""
    mime_type: str = ""
    file_size: int = 0
    etag: str = ""
    last_modified: str = ""
    sha256: str = ""
    download_time: str = ""
    status: str = "pending"