import uuid
from datetime import date, datetime, timedelta, timezone
from src.foundation import json_store, fsrs_engine
from src.entity.vocab import Vocab
from src.mediator.session_cache import SessionCache
from src.control.settings_controller import SettingsController


class VocabController:
    def __init__(self, cache: SessionCache, settings_ctrl: SettingsController):
        self._cache = cache
        self._settings_ctrl = settings_ctrl

    def get_all_vocab(self) -> list[Vocab]:
        return [Vocab.from_dict(v) for v in json_store.load_vocab()]

    def get_today_vocab_for_review(self, today: date) -> list[Vocab]:
        cached = self._cache.get_due_vocab()
        if cached is not None:
            return cached

        settings = self._settings_ctrl.get_settings()
        limit = settings.daily_new_vocab_limit
        today_str = today.isoformat()
        now_utc_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        all_vocab = [Vocab.from_dict(v) for v in json_store.load_vocab()]

        review_due = [v for v in all_vocab
                      if v.fsrs_state != "new" and v.fsrs_due <= now_utc_str]
        new_cards = [v for v in all_vocab if v.fsrs_state == "new"]
        new_today_count = sum(
            1 for v in all_vocab
            if v.fsrs_state != "new" and v.learned_date == today_str
        )
        allowed_new = max(0, limit - new_today_count)
        new_to_add = new_cards[:allowed_new]

        due = review_due + new_to_add
        self._cache.set_due_vocab(due)
        return due

    def add_vocab(self, language: str, word: str, reading: str,
                  meaning: str, example: str, learned_date: date) -> Vocab:
        tomorrow = (learned_date + timedelta(days=1)).isoformat()
        vocab = Vocab(
            id=str(uuid.uuid4()),
            language=language,
            word=word,
            reading=reading,
            meaning=meaning,
            example=example,
            learned_date=learned_date.isoformat(),
            reviews=[],
            next_review=tomorrow,
            fsrs_state="new",
            fsrs_stability=None,
            fsrs_difficulty=None,
            fsrs_due=tomorrow,
        )
        all_raw = json_store.load_vocab()
        all_raw.append(vocab.to_dict())
        json_store.save_vocab(all_raw)
        self._cache.invalidate()
        return vocab

    def rate_vocab(self, vocab_id: str, rating: str, today: date) -> Vocab:
        all_raw = json_store.load_vocab()
        for i, v in enumerate(all_raw):
            if v["id"] == vocab_id:
                updated = fsrs_engine.apply_fsrs(v, rating, today)
                all_raw[i] = updated
                json_store.save_vocab(all_raw)
                self._cache.invalidate()
                return Vocab.from_dict(updated)
        raise ValueError(f"Vocab {vocab_id} not found")

    def get_new_vocab_today_count(self, today: date) -> tuple[int, int]:
        """Return (new_cards_used_today, daily_limit)."""
        settings = self._settings_ctrl.get_settings()
        limit = settings.daily_new_vocab_limit
        today_str = today.isoformat()
        new_used = sum(
            1 for v in json_store.load_vocab()
            if v.get("fsrs_state") != "new" and v.get("learned_date") == today_str
        )
        return new_used, limit

    def get_fsrs_preview(self, vocab: Vocab) -> dict[str, str]:
        return fsrs_engine.get_fsrs_preview(vocab.to_dict())
