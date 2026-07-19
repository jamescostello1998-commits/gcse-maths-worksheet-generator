class TopicNotFoundError(Exception):
    def __init__(self, topic_id: str):
        self.topic_id = topic_id
        super().__init__(f"Unknown topic '{topic_id}'")


class WorksheetGenerationError(Exception):
    def __init__(self, topic_id: str, tier: str, attempts: int, produced: int):
        self.topic_id = topic_id
        self.tier = tier
        self.attempts = attempts
        self.produced = produced
        super().__init__(
            f"Could not generate enough unique questions for topic '{topic_id}' "
            f"({tier}): produced {produced} after {attempts} attempts"
        )


class PdfRenderError(Exception):
    def __init__(self, cause: Exception):
        self.cause = cause
        super().__init__(f"Failed to render worksheet PDF: {cause}")
