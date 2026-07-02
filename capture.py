"""Снимки: скриншот рабочего стола (mss) и фото с вебки (ffmpeg/dshow).

Вебка сделана через ffmpeg из imageio-ffmpeg, чтобы не тянуть opencv
(у которого на Python 3.14 может не быть колёс)."""
import re
import subprocess
from datetime import datetime
from pathlib import Path

import imageio_ffmpeg
import mss
from PIL import Image

from config import SCREENSHOT_DIR, WEBCAM_DIR

NO_WINDOW = 0x08000000


def screenshot() -> Path:
    """Скриншот всех мониторов, сохраняется в JPEG, возвращается путь."""
    path = SCREENSHOT_DIR / f"screen_{datetime.now():%Y%m%d_%H%M%S}.jpg"
    with mss.mss() as sct:
        raw = sct.grab(sct.monitors[0])  # 0 = виртуальный экран (все мониторы)
    img = Image.frombytes("RGB", raw.size, raw.rgb)
    img.save(path, "JPEG", quality=80)
    return path


def _ffmpeg() -> str:
    return imageio_ffmpeg.get_ffmpeg_exe()


def list_cameras() -> list[str]:
    """Список имён видеоустройств DirectShow."""
    r = subprocess.run(
        [_ffmpeg(), "-hide_banner", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=NO_WINDOW,
    )
    names: list[str] = []
    for line in r.stderr.splitlines():
        m = re.search(r'"([^"]+)"\s*\(video\)', line)
        if not m:
            m = re.search(r'"([^"]+)".*\(video\)', line)
        if m and m.group(1) not in names:
            names.append(m.group(1))
    return names


def webcam_snapshot(camera: str | None = None) -> Path | None:
    """Один кадр с вебки в JPEG. None, если камеры нет или захват не удался."""
    cams = list_cameras()
    if not cams:
        return None
    cam = camera or cams[0]
    path = WEBCAM_DIR / f"webcam_{datetime.now():%Y%m%d_%H%M%S}.jpg"
    subprocess.run(
        [
            _ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
            "-f", "dshow", "-rtbufsize", "100M", "-i", f"video={cam}",
            "-frames:v", "1", str(path),
        ],
        capture_output=True,
        creationflags=NO_WINDOW,
        timeout=30,
    )
    if path.exists() and path.stat().st_size > 0:
        return path
    return None


def recent_webcam(n: int = 10) -> list[Path]:
    return sorted(WEBCAM_DIR.glob("webcam_*.jpg"), reverse=True)[:n]
