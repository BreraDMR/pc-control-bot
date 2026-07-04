"""Звук/медиа и запуск команд на Windows.

ВСЯ нативная работа со звуком и медиа вынесена в отдельный процесс
(`mediactl.py`): Core Audio (pycaw/comtypes) для громкости и SMTC (winrt)
для медиа. Причина — comtypes/pycaw, вызванные из пула потоков бота, дают
access violation в _ctypes.pyd и роняют весь процесс; winrt на py3.14 тоже
способен нативно упасть. Изоляция в дочерний процесс с таймаутом гарантирует,
что никакой нативный сбой не может уронить или подвесить бот.

TTS — через System.Speech, произвольные команды — через PowerShell."""
import base64
import logging
import os
import subprocess
import sys

log = logging.getLogger("pc-control-bot")

NO_WINDOW = 0x08000000
_HELPER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mediactl.py")


def _run(*args, timeout: int = 8) -> bool:
    """Выполнить нативную операцию в изолированном процессе mediactl.py."""
    try:
        r = subprocess.run(
            [sys.executable, _HELPER, *args],
            timeout=timeout,
            creationflags=NO_WINDOW,
        )
        return r.returncode == 0
    except Exception:
        log.exception("mediactl failed: %s", args)
        return False


def volume_up(steps: int = 4) -> None:
    _run("volup", str(steps))


def volume_down(steps: int = 4) -> None:
    _run("voldown", str(steps))


def mute() -> None:
    _run("mute")


def media_playpause() -> None:
    _run("play")


def media_next() -> None:
    _run("next")


def media_prev() -> None:
    _run("prev")


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
