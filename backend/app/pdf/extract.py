from pathlib import Path
import json
import hashlib
import fitz

BASE_DIR = Path(__file__).resolve().parents[3]

PDF_DIR = BASE_DIR / "data" / "documents" / "pdf"
OUTPUT_DIR = BASE_DIR / "data" / "pdf_text"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def sha256(path: Path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            block = f.read(65536)
            if not block:
                break
            h.update(block)

    return h.hexdigest()


def extract_text(pdf_path: Path):

    doc = fitz.open(pdf_path)

    total_pages = len(doc)

    pages = []

    image_pages = 0

    for page in doc:

        text = page.get_text("text").strip()

        if text:
            pages.append(text)

        if page.get_images():
            image_pages += 1

    doc.close()

    return {

        "text": "\n".join(pages),

        "pages": total_pages,

        "image_pages": image_pages,

    }

def process_pdf(pdf):

    result = extract_text(pdf)

    out = {

        "url": "",

        "title": pdf.stem,

        "content": result["text"],

        "pdf": True,

        "needs_ocr": len(result["text"]) < 100,

        "pages": result["pages"],

        "image_pages": result["image_pages"],

        "sha256": sha256(pdf)

    }

    outfile = OUTPUT_DIR / (pdf.stem + ".json")

    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    return out


def main():

    total = 0

    scanned = 0

    text = 0

    for pdf in sorted(PDF_DIR.glob("*.pdf")):

        data = process_pdf(pdf)

        total += 1

        if data["needs_ocr"]:
            scanned += 1
        else:
            text += 1

    print()

    print("=" * 60)

    print("PDF Extraction Complete")

    print()

    print("Total PDFs :", total)

    print("Text PDFs  :", text)

    print("OCR PDFs   :", scanned)

    print()

    print("=" * 60)


if __name__ == "__main__":
    main()