from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Chapter:
    id: str
    subject: str
    chapter_no: str
    chapter_name: str
    learned_date: str
    reviews: list = field(default_factory=list)
    next_review: str = ""
    interval_days: int = 1
    ease: float = 2.5

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "subject": self.subject,
            "chapter_no": self.chapter_no,
            "chapter_name": self.chapter_name,
            "learned_date": self.learned_date,
            "reviews": self.reviews,
            "next_review": self.next_review,
            "interval_days": self.interval_days,
            "ease": self.ease,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Chapter":
        return cls(
            id=data["id"],
            subject=data["subject"],
            chapter_no=data["chapter_no"],
            chapter_name=data["chapter_name"],
            learned_date=data["learned_date"],
            reviews=data.get("reviews", []),
            next_review=data.get("next_review", ""),
            interval_days=data.get("interval_days", 1),
            ease=data.get("ease", 2.5),
        )
