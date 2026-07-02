"""Статистика бота: счётчики действий + журнал последних, хранится в JSON."""
import json
import threading
import time
from datetime import datetime, timedelta

from config import STATS_FILE

_lock = threading.Lock()
_START = time.time()


def _load() -> dict:
    if STATS_FILE.exists():
        try:
            return json.loads(STATS_FILE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    return {"counters": {}, "last_actions": [], "total": 0}


def _save(data: dict) -> None:
    STATS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def bump(action: str, meta: str = "") -> None:
    with _lock:
        data = _load()
        data["counters"][action] = data["counters"].get(action, 0) + 1
        data["total"] = data.get("total", 0) + 1
        entry = {"t": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "action": action}
        if meta:
            entry["meta"] = meta
        data["last_actions"] = ([entry] + data.get("last_actions", []))[:15]
        _save(data)


def text() -> str:
    with _lock:
        data = _load()
    uptime = timedelta(seconds=int(time.time() - _START))
    lines = [
        "📊 <b>Статистика бота</b>",
        f"⏱ Бот работает: <b>{uptime}</b>",
        f"🔢 Всего действий: <b>{data.get('total', 0)}</b>",
        "",
        "<b>По типам:</b>",
    ]
    counters = data.get("counters", {})
    if counters:
        for name, cnt in sorted(counters.items(), key=lambda x: -x[1]):
            lines.append(f"• {name}: {cnt}")
    else:
        lines.append("• пока пусто")
    last = data.get("last_actions", [])
    if last:
        lines.append("\n<b>Последние действия:</b>")
        for e in last[:8]:
            meta = f" ({e['meta']})" if e.get("meta") else ""
            lines.append(f"• {e['t']} — {e['action']}{meta}")
    return "\n".join(lines)
