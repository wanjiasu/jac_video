class ProgressManager:
    _progress = 0

    @classmethod
    def get_progress(cls) -> int:
        return cls._progress

    @classmethod
    def update_progress(cls, new_progress: int) -> None:
        cls._progress = min(100, max(0, new_progress))

    @classmethod
    def reset_progress(cls) -> None:
        cls._progress = 0