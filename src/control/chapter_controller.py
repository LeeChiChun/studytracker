import uuid
from datetime import date
from typing import Optional
from src.foundation import json_store, scheduler
from src.entity.chapter import Chapter
from src.mediator.session_cache import SessionCache


class ChapterController:
    def __init__(self, cache: SessionCache, settings_ctrl=None):
        self._cache = cache
        self._settings_ctrl = settings_ctrl

    def get_due_chapters(self, today: date) -> list[Chapter]:
        cached = self._cache.get_due_chapters()
        if cached is not None:
            return cached
        all_chapters = [Chapter.from_dict(c) for c in json_store.load_chapters()]
        today_str = today.isoformat()
        due = [c for c in all_chapters if c.next_review <= today_str]
        due.sort(key=lambda c: c.learned_date)
        self._cache.set_due_chapters(due)
        return due

    def get_all_chapters(self) -> list[Chapter]:
        all_raw = json_store.load_chapters()
        chapters = [Chapter.from_dict(c) for c in all_raw]
        chapters.sort(key=lambda c: c.learned_date)
        return chapters

    def chapter_exists(self, subject: str, chapter_no: str) -> bool:
        return any(
            c["subject"] == subject and c["chapter_no"] == chapter_no
            for c in json_store.load_chapters()
        )

    def add_chapter(self, subject: str, chapter_no: str, chapter_name: str, learned_date: date) -> Chapter:
        schedule = scheduler.initial_chapter_schedule(learned_date)
        chapter = Chapter(
            id=str(uuid.uuid4()),
            subject=subject,
            chapter_no=chapter_no,
            chapter_name=chapter_name,
            learned_date=learned_date.isoformat(),
            reviews=[],
            **schedule,
        )
        all_raw = json_store.load_chapters()
        all_raw.append(chapter.to_dict())
        json_store.save_chapters(all_raw)
        self._cache.invalidate()
        return chapter

    def update_chapter(self, subject: str, chapter_no: str, chapter_name: str, learned_date: date) -> None:
        all_raw = json_store.load_chapters()
        for c in all_raw:
            if c["subject"] == subject and c["chapter_no"] == chapter_no:
                c["chapter_name"] = chapter_name
                c["learned_date"] = learned_date.isoformat()
                break
        json_store.save_chapters(all_raw)
        self._cache.invalidate()

    def rate_chapter(self, chapter_id: str, rating: str, today: date) -> Chapter:
        exam_date: Optional[date] = None
        if self._settings_ctrl is not None:
            exam_dates = self._settings_ctrl.get_settings().exam_dates
            all_raw = json_store.load_chapters()
            for c in all_raw:
                if c["id"] == chapter_id:
                    subject = c.get("subject", "")
                    raw_date = exam_dates.get(subject)
                    if raw_date:
                        try:
                            exam_date = date.fromisoformat(raw_date)
                        except ValueError:
                            pass
                    break
        all_raw = json_store.load_chapters()
        for i, c in enumerate(all_raw):
            if c["id"] == chapter_id:
                updated = scheduler.apply_sm2(c, rating, today, exam_date=exam_date)
                all_raw[i] = updated
                json_store.save_chapters(all_raw)
                self._cache.invalidate()
                return Chapter.from_dict(updated)
        raise ValueError(f"Chapter {chapter_id} not found")

    def edit_chapter(self, chapter_id: str, chapter_no: str,
                     chapter_name: str, learned_date: date) -> None:
        all_raw = json_store.load_chapters()
        for c in all_raw:
            if c["id"] == chapter_id:
                c["chapter_no"] = chapter_no
                c["chapter_name"] = chapter_name
                c["learned_date"] = learned_date.isoformat()
                break
        json_store.save_chapters(all_raw)
        self._cache.invalidate()
