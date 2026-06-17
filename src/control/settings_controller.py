import uuid
from src.foundation import json_store
from src.entity.settings_model import Settings
from src.entity.subject import Subject


class SettingsController:
    def get_settings(self) -> Settings:
        return Settings.from_dict(json_store.load_settings())

    def save_settings(self, settings: Settings) -> None:
        json_store.save_settings(settings.to_dict())

    def get_subjects(self) -> list[Subject]:
        return self.get_settings().subjects

    def add_subject(self, name: str, color: str) -> Subject:
        settings = self.get_settings()
        subject = Subject(id=f"s-{str(uuid.uuid4())[:8]}", name=name, color=color)
        settings.subjects.append(subject)
        self.save_settings(settings)
        return subject

    def delete_subject(self, subject_id: str) -> None:
        settings = self.get_settings()
        settings.subjects = [s for s in settings.subjects if s.id != subject_id]
        self.save_settings(settings)

    def update_review_settings(self, daily_new_vocab_limit: int, target_retention: float) -> None:
        settings = self.get_settings()
        settings.daily_new_vocab_limit = daily_new_vocab_limit
        settings.target_retention = target_retention
        self.save_settings(settings)

    def subject_has_chapters(self, subject_name: str) -> bool:
        chapters = json_store.load_chapters()
        return any(c["subject"] == subject_name for c in chapters)

    def get_exam_dates(self) -> dict:
        return self.get_settings().exam_dates

    def update_exam_dates(self, exam_dates: dict) -> None:
        settings = self.get_settings()
        settings.exam_dates = exam_dates
        self.save_settings(settings)
