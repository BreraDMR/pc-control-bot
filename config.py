"""Конфигурация бота: читает .env (без сторонних зависимостей), задаёт пути."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _load_env() -> None:
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env()

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_IDS = {
    int(x) for x in os.environ.get("OWNER_IDS", "").replace(" ", "").split(",") if x
}

# Пустая строка = дистрибутив WSL по умолчанию (у нас Ubuntu).
WSL_DISTRO = os.environ.get("WSL_DISTRO", "").strip()

# Интервал авто-снимков вебки в минутах (0 = выключено по умолчанию).
AUTO_SNAP_MINUTES = int(os.environ.get("AUTO_SNAP_MINUTES", "30") or "30")

CAPTURES_DIR = BASE_DIR / "captures"
WEBCAM_DIR = CAPTURES_DIR / "webcam"
SCREENSHOT_DIR = CAPTURES_DIR / "screenshots"
REC_DIR = CAPTURES_DIR / "recordings"
DATA_DIR = BASE_DIR / "data"
STATS_FILE = DATA_DIR / "stats.json"

for _d in (WEBCAM_DIR, SCREENSHOT_DIR, REC_DIR, DATA_DIR):
    _d.mkdir(parents=True, exist_ok=True)
