import json
import shutil
from datetime import datetime
from pathlib import Path

_DATA_DIR = Path.home() / "Library" / "Application Support" / "習習複習習" / "data"
_BACKUP_DIR = _DATA_DIR / "backup"

_DEFAULT_SETTINGS = {
    "subjects": [
        {"id": "s-001", "name": "線性代數",      "color": "#4A90D9"},
        {"id": "s-002", "name": "作業系統",      "color": "#E67E22"},
        {"id": "s-003", "name": "離散數學",      "color": "#27AE60"},
        {"id": "s-004", "name": "演算法",        "color": "#8E44AD"},
        {"id": "s-005", "name": "資料結構",      "color": "#C0392B"},
        {"id": "s-006", "name": "計算機組織與結構", "color": "#16A085"},
        {"id": "s-007", "name": "英文",          "color": "#2980B9"},
        {"id": "s-008", "name": "日文",          "color": "#D35400"},
    ],
    "daily_new_vocab_limit": 20,
    "target_retention": 0.90,
    "fsrs_weights": [],
    "exam_dates": {},
}


def _ensure_dirs() -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    _BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not (_DATA_DIR / "settings.json").exists():
        with open(_DATA_DIR / "settings.json", "w", encoding="utf-8") as f:
            json.dump(_DEFAULT_SETTINGS, f, ensure_ascii=False, indent=2)
    for name in ("chapters.json", "vocab.json"):
        p = _DATA_DIR / name
        if not p.exists():
            with open(p, "w", encoding="utf-8") as f:
                json.dump([], f)


_ensure_dirs()


def _backup(file_path: Path) -> None:
    if not file_path.exists():
        return
    _BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = _BACKUP_DIR / f"{file_path.stem}_{ts}.json"
    shutil.copy2(file_path, dest)


def _load(filename: str) -> list | dict:
    path = _DATA_DIR / filename
    if not path.exists():
        return [] if filename != "settings.json" else {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save(filename: str, data: list | dict) -> None:
    path = _DATA_DIR / filename
    _backup(path)
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_settings() -> dict:
    return _load("settings.json")


def save_settings(data: dict) -> None:
    _save("settings.json", data)


def load_chapters() -> list:
    return _load("chapters.json")


def save_chapters(data: list) -> None:
    _save("chapters.json", data)


def load_vocab() -> list:
    return _load("vocab.json")


def save_vocab(data: list) -> None:
    _save("vocab.json", data)
