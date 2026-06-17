from fsrs import Card, Rating, Scheduler, State
from datetime import datetime, timezone, date, timedelta

_MAX_INTERVAL = 365

_SCHEDULER = Scheduler(
    learning_steps=[timedelta(minutes=1), timedelta(days=1)],
    enable_fuzzing=False,
    # maximum_interval not set here — internal cap distorts ordering near the limit.
    # 365-day hard cap applied manually in schedule_vocab.
)

_STATE_MAP = {
    "learning":   State.Learning,
    "review":     State.Review,
    "relearning": State.Relearning,
}

_STATE_STR = {
    State.Learning:   "learning",
    State.Review:     "review",
    State.Relearning: "relearning",
}

_RATING_MAP = {
    "again": Rating.Again,
    "hard":  Rating.Hard,
    "good":  Rating.Good,
    "easy":  Rating.Easy,
}


def _build_card(vocab: dict) -> Card:
    card = Card()
    fsrs_state = vocab.get("fsrs_state", "new")
    if fsrs_state in _STATE_MAP:
        card.state = _STATE_MAP[fsrs_state]
    if vocab.get("fsrs_stability"):
        card.stability = float(vocab["fsrs_stability"])
    if vocab.get("fsrs_difficulty"):
        card.difficulty = float(vocab["fsrs_difficulty"])
    reviews = vocab.get("reviews", [])
    if reviews:
        last_raw = reviews[-1]["date"]
        base = last_raw if "T" in last_raw else last_raw + "T00:00:00"
        card.last_review = datetime.fromisoformat(base).replace(tzinfo=timezone.utc)
    else:
        card.last_review = datetime.now(timezone.utc)
    return card


def schedule_vocab(vocab: dict, rating_str: str) -> dict:
    """
    Input:  vocab dict (with fsrs_* fields), rating string
    Output: mutated vocab dict with updated fsrs_* fields + interval_days
    Note:   reviews list is NOT modified here; caller handles it.
    """
    card = _build_card(vocab)
    new_card, _ = _SCHEDULER.review_card(card, _RATING_MAP[rating_str])

    due = new_card.due
    today = date.today()
    interval_days = max(0, (due.astimezone().date() - today).days)
    interval_days = min(interval_days, _MAX_INTERVAL)

    vocab["fsrs_stability"]  = round(new_card.stability, 4) if new_card.stability is not None else None
    vocab["fsrs_difficulty"] = round(new_card.difficulty, 4) if new_card.difficulty is not None else None
    vocab["fsrs_state"]      = _STATE_STR.get(new_card.state, "learning")
    vocab["fsrs_due"]        = due.strftime("%Y-%m-%dT%H:%M:%S")
    vocab["next_review"]     = (today + timedelta(days=interval_days)).isoformat()
    vocab["interval_days"]   = interval_days

    return vocab


def preview_intervals(vocab: dict) -> dict[str, int]:
    """Returns {rating_str: days} for all 4 ratings. No side effects on original vocab."""
    result = {}
    for r_str in ["again", "hard", "good", "easy"]:
        result[r_str] = schedule_vocab(dict(vocab), r_str)["interval_days"]
    return result


# ── Backward-compatible wrappers for existing callers ──────────────────────

def apply_fsrs(vocab: dict, rating: str, today: date) -> dict:
    """Used by VocabController: schedule + append rating to reviews list."""
    updated = schedule_vocab(dict(vocab), rating)
    updated["reviews"] = vocab.get("reviews", []) + [
        {"date": today.isoformat(), "rating": rating}
    ]
    return updated


def get_fsrs_preview(vocab: dict) -> dict[str, str]:
    """Used by ReviewController: returns human-readable interval labels."""
    intervals = preview_intervals(vocab)
    now_utc = datetime.now(tz=timezone.utc)
    is_learning = vocab.get("fsrs_state") in ("new", "learning")
    result = {}
    for key, days in intervals.items():
        if days <= 0:
            if is_learning:
                v_copy = dict(vocab)
                schedule_vocab(v_copy, key)
                try:
                    due_dt = datetime.fromisoformat(
                        v_copy["fsrs_due"]
                    ).replace(tzinfo=timezone.utc)
                    minutes = max(0, int((due_dt - now_utc).total_seconds() / 60))
                    result[key] = f"今天（{minutes} 分鐘後）" if minutes > 0 else "今天"
                except Exception:
                    result[key] = "今天"
            else:
                result[key] = "今天"
        elif days == 1:
            result[key] = "明天"
        else:
            result[key] = f"{days} 天後"
    return result
