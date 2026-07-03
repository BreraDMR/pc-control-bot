"""Звук/медиа и запуск команд на Windows.

Громкость управляется через Core Audio API (pycaw/IAudioEndpointVolume) —
это задаёт системную громкость напрямую, не завися от фокуса окна.
Медиа (play/pause/next/prev) — через System Media Transport Controls (SMTC):
команда идёт прямо в активную медиасессию (YouTube в браузере, плеер и т.п.).
SMTC вызывается в ОТДЕЛЬНОМ процессе (mediactl.py) с таймаутом — winrt на
py3.14 может нативно упасть/зависнуть, и изоляция не даёт уронить бот. Если
дочерний процесс не справился, откатываемся на мультимедиа-клавишу.
TTS — через System.Speech, произвольные команды — через PowerShell."""
import asyncio  # noqa: F401  (оставлено для совместимости импортов)
import base64
import ctypes
import logging
import os
import subprocess
import sys
from ctypes import POINTER, cast

from comtypes import CLSCTX_ALL, CoInitialize
from pycaw.pycaw import (
    AudioUtilities,
    EDataFlow,
    ERole,
    IAudioEndpointVolume,
)

log = logging.getLogger("pc-control-bot")

NO_WINDOW = 0x08000000
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001
VOL_STEP = 0.02  # доля громкости (0..1) на один «шаг»

_MEDIA_VK = {"play": 0xB3, "next": 0xB0, "prev": 0xB1}
_HELPER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mediactl.py")


# --- Громкость через Core Audio (pycaw) -----------------------------------
def _endpoint():
    CoInitialize()
    enum = AudioUtilities.GetDeviceEnumerator()
    dev = enum.GetDefaultAudioEndpoint(EDataFlow.eRender.value, ERole.eMultimedia.value)
    ptr = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(ptr, POINTER(IAudioEndpointVolume))


def _add_volume(delta: float) -> None:
    try:
        v = _endpoint()
        if v.GetMute():
            v.SetMute(0, None)
        new = min(1.0, max(0.0, v.GetMasterVolumeLevelScalar() + delta))
        v.SetMasterVolumeLevelScalar(new, None)
    except Exception:
        log.exception("volume change failed")


def volume_up(steps: int = 4) -> None:
    _add_volume(steps * VOL_STEP)


def volume_down(steps: int = 4) -> None:
    _add_volume(-steps * VOL_STEP)


def mute() -> None:
    try:
        v = _endpoint()
        v.SetMute(0 if v.GetMute() else 1, None)
    except Exception:
        log.exception("mute toggle failed")


# --- Медиа через SMTC в отдельном процессе, откат на мультимедиа-клавиши ---
def _tap(vk: int) -> None:
    ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_EXTENDEDKEY, 0)
    ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)


def _media(action: str) -> None:
    ok = False
    try:
        r = subprocess.run(
            [sys.executable, _HELPER, action],
            timeout=8,
            creationflags=NO_WINDOW,
        )
        ok = r.returncode == 0
    except Exception:
        log.exception("SMTC helper failed for %s", action)
    if not ok:
        _tap(_MEDIA_VK[action])


def media_playpause() -> None:
    _media("play")


def media_next() -> None:
    _media("next")


def media_prev() -> None:
    _media("prev")


def speak(text: str) -> None:
    """Озвучить текст на колонках ПК (кириллице нужен русский голос в системе)."""
    b64 = base64.b64encode(text.encode("utf-8")).decode()
    script = (
        "Add-Type -AssemblyName System.Speech; "
        f"$t=[System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{b64}')); "
        "(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak($t)"
    )
    subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", script],
        creationflags=NO_WINDOW,
        timeout=60,
    )


def open_url(target: str) -> None:
    """Открыть URL или запустить приложение через Start-Process."""
    subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-Command", f'Start-Process "{target}"'],
        creationflags=NO_WINDOW,
    )


def run_powershell(command: str, timeout: int = 30) -> str:
    """Выполнить произвольную PowerShell-команду, вернуть вывод (обрезается вызывающим)."""
    try:
        r = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            creationflags=NO_WINDOW,
        )
    except subprocess.TimeoutExpired:
        return f"⏱ Команда не завершилась за {timeout} с (прервана)."
    out = (r.stdout or "").strip()
    err = (r.stderr or "").strip()
    if err:
        out = (out + "\n[stderr]\n" + err).strip()
    return out or "(пустой вывод)"
