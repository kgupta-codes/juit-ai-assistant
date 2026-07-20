from app.pdf.downloader import download
from app.pdf.extract import main as extract_pdfs


class PDFService:
    def download(self):
        print("\n========== PDF DOWNLOAD ==========\n")
        download()
        print("\n==================================\n")

    def extract(self):
        print("\n========== PDF EXTRACTION ==========\n")
        extract_pdfs()
        print("\n====================================\n")

    def sync(self):
        self.download()
        self.extract()


pdf_service = PDFService()

if __name__ == "__main__":
    pdf_service.sync()