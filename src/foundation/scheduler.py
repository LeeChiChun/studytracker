from datetime import date, timedelta
from typing import Optional

_MIN_EASE = 1.3
_MAX_INTERVAL = 365  # days — hard cap applied on every code path


def apply_sm2(chapter: dict, rating: str, today: date,
              exam_date: Optional[date] = None) -> dict:
    interval = chapter["interval_days"]
    ease = chapter["ease"]

    if rating == "again":
        new_interval = 1
        new_ease = round(max(_MIN_EASE, ease * 0.85), 4)
    elif rating == "hard":
        new_interval = max(1, round(interval * 1.2))
        new_ease = round(ease * 0.95, 4)
    elif rating == "good":
        new_interval = max(1, round(interval * ease))
        new_ease = round(ease, 4)
    elif rating == "easy":
        new_interval = max(1, round(interval * ease * 1.3))
        new_ease = round(ease + 0.1, 4)
    else:
        raise ValueError(f"Unknown rating: {rating!r}")

    # Hard cap
    new_interval = min(new_interval, _MAX_INTERVAL)

    # Exam date cap (overrides hard cap when exam is closer)
    if exam_date is not None:
        days_to_exam = (exam_date - today).days
        new_interval = min(new_interval, max(1, days_to_exam))

    next_review = (today + timedelta(days=new_interval)).isoformat()

    updated = {**chapter}
    updated["interval_days"] = new_interval
    updated["ease"] = new_ease
    updated["next_review"] = next_review
    updated["reviews"] = chapter.get("reviews", []) + [
        {"date": today.isoformat(), "rating": rating}
    ]
    return updated


def initial_chapter_schedule(learned_date: date) -> dict:
    return {
        "interval_days": 1,
        "ease": 2.5,
        "next_review": (learned_date + timedelta(days=1)).isoformat(),
    }
