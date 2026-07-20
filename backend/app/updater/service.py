from app.pipeline import pipeline


class UpdateService:
    """
    Executes one complete knowledge synchronization.
    """

    def run(self):
        print("\n========== DAILY UPDATE ==========\n")

        pipeline.run()

        print("\n========== UPDATE COMPLETE ==========\n")


update_service = UpdateService()


if __name__ == "__main__":
    update_service.run()