from pathlib import Path

from app.pdf.index import pdf_index

pdf_dir = Path("data/documents/pdf")

pdf = next(pdf_dir.glob("*.pdf"))

print("Filename:")
print(pdf.name)

print("\nMetadata:")
print(pdf_index.lookup(pdf.name))