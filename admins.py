"""Управление списком админов.

Владельцы (OWNER_IDS из .env) — «железные» админы, их нельзя удалить.
Остальные админы регистрируются по запросу и хранятся в data/admins.json."""
from __future__ import annotations

import json
import threading
from datetime import datetime

from config import DATA_DIR, OWNER_IDS

ADMINS_FILE = DATA_DIR / "admins.json"
_lock = threading.Lock()


def _load() -> dict:
    if ADMINS_FILE.exists():
        try:
            return json.loads(ADMINS_FILE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    return {"admins": []}


def _save(data: dict) -> None:
    ADMINS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def is_owner(user_id: int | None) -> bool:
    return user_id in OWNER_IDS


def approved_ids() -> set[int]:
    with _lock:
        return {a["id"] for a in _load()["admins"]}


def is_admin(user_id: int | None) -> bool:
    if user_id is None:
        return False
    return user_id in OWNER_IDS or user_id in approved_ids()


def add_admin(user_id: int, name: str = "") -> bool:
    with _lock:
        data = _load()
        if any(a["id"] == user_id for a in data["admins"]):
            return False
        data["admins"].append(
            {"id": user_id, "name": name, "added": datetime.now().strftime("%Y-%m-%d %H:%M")}
        )
        _save(data)
        return True


def remove_admin(user_id: int) -> bool:
    with _lock:
        data = _load()
        before = len(data["admins"])
        data["admins"] = [a for a in data["admins"] if a["id"] != user_id]
        if len(data["admins"]) != before:
            _save(data)
            return True
        return False


def list_all() -> list[dict]:
    """Все админы: сначала владельцы, затем зарегистрированные."""
    owners = [{"id": oid, "name": "владелец", "owner": True} for oid in sorted(OWNER_IDS)]
    with _lock:
        extra = [{**a, "owner": False} for a in _load()["admins"]]
    return owners + extra
