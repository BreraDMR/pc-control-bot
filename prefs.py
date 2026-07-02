"""Пользовательские настройки (сейчас — язык интерфейса), хранятся в data/prefs.json.

Язык по умолчанию — английский. Исключение: «старые» владельцы по умолчанию на русском."""
from __future__ import annotations

import json
import threading

from config import DATA_DIR

PREFS_FILE = DATA_DIR / "prefs.json"

# Эти два владельца исторически на русском — не трогаем их дефолт.
DEFAULT_RU_IDS = {8507082419, 590228274}

SUPPORTED = ("en", "ru", "cs")
DEFAULT_LANG = "en"

_lock = threading.Lock()


def _load() -> dict:
    if PREFS_FILE.exists():
        try:
            return json.loads(PREFS_FILE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    return {}


def _save(data: dict) -> None:
    PREFS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def get_lang(user_id: int | None) -> str:
    if user_id is None:
        return DEFAULT_LANG
    with _lock:
        stored = _load().get(str(user_id))
    if stored in SUPPORTED:
        return stored
    return "ru" if user_id in DEFAULT_RU_IDS else DEFAULT_LANG


def set_lang(user_id: int, lang: str) -> None:
    if lang not in SUPPORTED:
        return
    with _lock:
        data = _load()
        data[str(user_id)] = lang
        _save(data)
