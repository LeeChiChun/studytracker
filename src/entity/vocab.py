from dataclasses import dataclass, field


@dataclass
class Vocab:
    id: str
    language: str
    word: str
    reading: str
    meaning: str
    example: str
    learned_date: str
    reviews: list = field(default_factory=list)
    next_review: str = ""
    fsrs_state: str = "new"
    fsrs_stability: float = None
    fsrs_difficulty: float = None
    fsrs_due: str = ""
    fsrs_step: int = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "language": self.language,
            "word": self.word,
            "reading": self.reading,
            "meaning": self.meaning,
            "example": self.example,
            "learned_date": self.learned_date,
            "reviews": self.reviews,
            "next_review": self.next_review,
            "fsrs_state": self.fsrs_state,
            "fsrs_stability": self.fsrs_stability,
            "fsrs_difficulty": self.fsrs_difficulty,
            "fsrs_due": self.fsrs_due,
            "fsrs_step": self.fsrs_step,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Vocab":
        return cls(
            id=data["id"],
            language=data["language"],
            word=data["word"],
            reading=data.get("reading", ""),
            meaning=data["meaning"],
            example=data.get("example", ""),
            learned_date=data["learned_date"],
            reviews=data.get("reviews", []),
            next_review=data.get("next_review", ""),
            fsrs_state=data.get("fsrs_state", "new"),
            fsrs_stability=data.get("fsrs_stability"),
            fsrs_difficulty=data.get("fsrs_difficulty"),
            fsrs_due=data.get("fsrs_due", ""),
            fsrs_step=data.get("fsrs_step"),
        )
