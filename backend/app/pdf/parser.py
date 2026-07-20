from pathlib import Path
import fitz


class PDFParser:

    def parse(self, pdf_path: str):

        doc = fitz.open(pdf_path)

        pages = len(doc)

        text_parts = []

        image_pages = 0

        for page in doc:

            text = page.get_text("text").strip()

            if text:
                text_parts.append(text)

            if len(page.get_images()) > 0:
                image_pages += 1

        doc.close()

        full_text = "\n".join(text_parts).strip()

        return {

            "pages": pages,

            "characters": len(full_text),

            "images": image_pages,

            "needs_ocr": len(full_text) < 100,

            "text": full_text

        }


if __name__ == "__main__":

    parser = PDFParser()

    pdf_dir = Path("data/documents/pdf")

    for pdf in pdf_dir.glob("*.pdf"):

        result = parser.parse(str(pdf))

        print("=" * 80)

        print(pdf.name)

        print(result)

        break