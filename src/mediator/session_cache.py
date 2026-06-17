"""
In-memory cache for the current session's dashboard data.
Invalidated whenever chapters or vocab are modified.
"""
from datetime import date


class SessionCache:
    def __init__(self):
        self._due_chapters: list | None = None
        self._due_vocab: list | None = None
        self._cache_date: date | None = None

    def _is_valid(self) -> bool:
        return self._cache_date == date.today()

    def get_due_chapters(self) -> list | None:
        return self._due_chapters if self._is_valid() else None

    def set_due_chapters(self, chapters: list) -> None:
        self._due_chapters = chapters
        self._cache_date = date.today()

    def get_due_vocab(self) -> list | None:
        return self._due_vocab if self._is_valid() else None

    def set_due_vocab(self, vocab: list) -> None:
        self._due_vocab = vocab
        self._cache_date = date.today()

    def invalidate(self) -> None:
        self._due_chapters = None
        self._due_vocab = None
        self._cache_date = None
