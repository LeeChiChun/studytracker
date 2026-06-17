"""
Coordinates a flashcard review session for vocab.
"""
from datetime import date
from src.entity.vocab import Vocab
from src.control.vocab_controller import VocabController


class ReviewController:
    def __init__(self, vocab_ctrl: VocabController):
        self._vocab_ctrl = vocab_ctrl
        self._queue: list[Vocab] = []
        self._current_index: int = 0
        self._completed_count: int = 0

    def start_session(self, today: date) -> int:
        self._queue = self._vocab_ctrl.get_today_vocab_for_review(today)
        self._current_index = 0
        self._completed_count = 0
        return len(self._queue)

    def total(self) -> int:
        return len(self._queue)

    def current_position(self) -> int:
        return self._current_index + 1

    def current_vocab(self) -> Vocab | None:
        if self._current_index < len(self._queue):
            return self._queue[self._current_index]
        return None

    def get_preview(self) -> dict[str, str]:
        vocab = self.current_vocab()
        if vocab is None:
            return {}
        return self._vocab_ctrl.get_fsrs_preview(vocab)

    def rate_current(self, rating: str, today: date) -> bool:
        """Rate current card. Returns True if session is complete."""
        vocab = self.current_vocab()
        if vocab is None:
            return True
        self._vocab_ctrl.rate_vocab(vocab.id, rating, today)
        self._current_index += 1
        self._completed_count += 1
        return self._current_index >= len(self._queue)

    def completed_count(self) -> int:
        return self._completed_count

    def is_done(self) -> bool:
        return self._current_index >= len(self._queue)
