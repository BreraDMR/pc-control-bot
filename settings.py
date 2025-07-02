"""Глобальные настройки бота (общие для всех), хранятся в data/settings.json.

Сейчас здесь — выбранная активная камера для фото/видео с вебки."""
from __future__ import annotations

import json
import threading

from config import DATA_DIR

SETTINGS_FILE = DATA_DIR / "settings.json"
_lock = threading.Lock()


def _load() -> dict:
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    return {}


def _save(data: dict) -> None:
    SETTINGS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def get(key: str, default=None):
    with _lock:
        return _load().get(key, default)


def set(key: str, value) -> None:  # noqa: A003
    with _lock:
        data = _load()
        data[key] = value
        _save(data)


def get_camera() -> str | None:
    return get("camera")


def set_camera(name: str) -> None:
    set("camera", name)
