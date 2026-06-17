from dataclasses import dataclass, field
from src.entity.subject import Subject


@dataclass
class Settings:
    subjects: list[Subject] = field(default_factory=list)
    daily_new_vocab_limit: int = 10
    target_retention: float = 0.90
    fsrs_weights: list = field(default_factory=list)
    exam_dates: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "subjects": [s.to_dict() for s in self.subjects],
            "daily_new_vocab_limit": self.daily_new_vocab_limit,
            "target_retention": self.target_retention,
            "fsrs_weights": self.fsrs_weights,
            "exam_dates": self.exam_dates,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        return cls(
            subjects=[Subject.from_dict(s) for s in data.get("subjects", [])],
            daily_new_vocab_limit=data.get("daily_new_vocab_limit", 10),
            target_retention=data.get("target_retention", 0.90),
            fsrs_weights=data.get("fsrs_weights", []),
            exam_dates=data.get("exam_dates", {}),
        )
