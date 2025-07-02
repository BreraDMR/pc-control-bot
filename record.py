"""Короткая запись видео (вебка+микрофон) и аудио (микрофон) через ffmpeg/dshow.

Видео → H.264/AAC .mp4 (Telegram-видео), аудио → Opus .ogg (голосовое сообщение).
Длительность задаётся вызывающим. Если устройства нет — возвращается None."""
from __future__ import annotations

import re
import subprocess
from datetime import datetime
from pathlib import Path

import imageio_ffmpeg

from config import REC_DIR

NO_WINDOW = 0x08000000


def _ffmpeg() -> str:
    return imageio_ffmpeg.get_ffmpeg_exe()


def _list_devices(kind: str) -> list[str]:
    """kind = 'video' | 'audio' — имена dshow-устройств."""
    r = subprocess.run(
        [_ffmpeg(), "-hide_banner", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        creationflags=NO_WINDOW,
    )
    names: list[str] = []
    for line in r.stderr.splitlines():
        m = re.search(rf'"([^"]+)"\s*\({kind}\)', line) or re.search(rf'"([^"]+)".*\({kind}\)', line)
        if m and m.group(1) not in names:
            names.append(m.group(1))
    return names


def list_cameras() -> list[str]:
    return _list_devices("video")


def list_microphones() -> list[str]:
    return _list_devices("audio")


def record_video(seconds: int, camera: str | None = None, mic: str | None = None) -> Path | None:
    """Записать клип с вебки (+микрофон, если есть). None, если нет камеры/ошибка."""
    cams = list_cameras()
    if not cams:
        return None
    cam = camera or cams[0]
    mics = list_microphones()
    use_mic = mic or (mics[0] if mics else None)
    out = REC_DIR / f"video_{datetime.now():%Y%m%d_%H%M%S}.mp4"

    cmd = [_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-f", "dshow"]
    if use_mic:
        cmd += ["-i", f"video={cam}:audio={use_mic}"]
    else:
        cmd += ["-i", f"video={cam}"]
    cmd += ["-t", str(seconds), "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p"]
    if use_mic:
        cmd += ["-c:a", "aac", "-b:a", "128k"]
    else:
        cmd += ["-an"]
    cmd += ["-movflags", "+faststart", str(out)]

    try:
        subprocess.run(cmd, capture_output=True, creationflags=NO_WINDOW, timeout=seconds + 40)
    except subprocess.TimeoutExpired:
        return None
    return out if out.exists() and out.stat().st_size > 0 else None


def record_audio(seconds: int, mic: str | None = None) -> Path | None:
    """Записать аудио с микрофона в Opus/OGG (голосовое). None, если нет микрофона/ошибка."""
    mics = list_microphones()
    if not mics:
        return None
    use_mic = mic or mics[0]
    out = REC_DIR / f"audio_{datetime.now():%Y%m%d_%H%M%S}.ogg"
    cmd = [
        _ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
        "-f", "dshow", "-i", f"audio={use_mic}",
        "-t", str(seconds), "-c:a", "libopus", "-b:a", "64k", str(out),
    ]
    try:
        subprocess.run(cmd, capture_output=True, creationflags=NO_WINDOW, timeout=seconds + 40)
    except subprocess.TimeoutExpired:
        return None
    return out if out.exists() and out.stat().st_size > 0 else None
