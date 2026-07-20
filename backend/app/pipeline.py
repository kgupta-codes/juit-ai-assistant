from app.pdf.service import pdf_service


class KnowledgePipeline:

    def run(self):

        print("\n==============================")
        print(" JUIT AI KNOWLEDGE PIPELINE ")
        print("==============================\n")

        pdf_service.sync()

        print("\nKnowledge pipeline completed.\n")


pipeline = KnowledgePipeline()


if __name__ == "__main__":
    pipeline.run()