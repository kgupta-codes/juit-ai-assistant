import fitz


def is_valid_pdf(path):

    try:

        doc = fitz.open(path)

        pages = len(doc)

        doc.close()

        return pages > 0

    except Exception:

        return False