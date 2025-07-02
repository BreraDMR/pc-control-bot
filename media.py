"""Звук/медиа и запуск команд на Windows — без сторонних зависимостей.

Громкость и медиа управляются через виртуальные мультимедийные клавиши
(keybd_event), TTS — через System.Speech PowerShell, произвольные команды —
через PowerShell (доступно только владельцу, см. security.restricted)."""
import base64
import ctypes
import subprocess

NO_WINDOW = 0x08000000
KEYEVENTF_KEYUP = 0x0002

VK = {
    "vol_up": 0xAF,
    "vol_down": 0xAE,
    "mute": 0xAD,
    "play": 0xB3,
    "next": 0xB0,
    "prev": 0xB1,
}


def _tap(vk: int, times: int = 1) -> None:
    for _ in range(times):
        ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
        ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def volume_up(steps: int = 4) -> None:
    _tap(VK["vol_up"], steps)


def volume_down(steps: int = 4) -> None:
    _tap(VK["vol_down"], steps)


def mute() -> None:
    _tap(VK["mute"])


def media_playpause() -> None:
    _tap(VK["play"])


def media_next() -> None:
    _tap(VK["next"])


def media_prev() -> None:
    _tap(VK["prev"])


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
