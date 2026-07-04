"""Звук/медиа и запуск команд на Windows.

ГРОМКОСТЬ — через выделенный постоянный COM-поток (`_audio_worker`): endpoint
Core Audio (pycaw/comtypes) создаётся один раз и живёт в этом же потоке, все
запросы идут через очередь и обрабатываются последовательно. Так снимаются
СРАЗУ две проблемы: (1) межпоточный COM у comtypes при вызове из пула потоков
бота давал access violation 0xc0000005 в _ctypes.pyd и ронял процесс;
(2) запуск тяжёлого Python-подпроцесса на каждый тап (импорт pycaw ~0.5 c)
при мэшинге кнопок спайкал CPU и подвешивал event loop до таймаута Telegram.
Теперь нажатие громкости — это мгновенный `queue.put`, никакого спавна.

МЕДИА (play/pause/next/prev) — через System Media Transport Controls (winrt
SMTC) в ИЗОЛИРОВАННОМ подпроцессе `mediactl.py` с таймаутом: winrt на py3.14
может нативно упасть/зависнуть, изоляция не даёт уронить бот; жмут редко, так
что стоимость запуска процесса не критична. Фолбэк — мультимедиа-клавиша.

TTS — через System.Speech, произвольные команды — через PowerShell."""
import base64
import logging
import os
import queue
import subprocess
import sys
import threading

log = logging.getLogger("pc-control-bot")

NO_WINDOW = 0x08000000
VOL_STEP = 0.02  # доля громкости (0..1) на один «шаг»
_HELPER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mediactl.py")

# --- Громкость: единственный постоянный COM-поток -------------------------
_MUTE = object()  # маркер операции «переключить mute» в очереди
_audio_q: "queue.Queue" = queue.Queue()


def _build_endpoint():
    import comtypes
    from ctypes import POINTER, cast

    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import (
        AudioUtilities,
        EDataFlow,
        ERole,
        IAudioEndpointVolume,
    )

    comtypes.CoInitialize()
    enum = AudioUtilities.GetDeviceEnumerator()
    dev = enum.GetDefaultAudioEndpoint(EDataFlow.eRender.value, ERole.eMultimedia.value)
    return cast(dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None), POINTER(IAudioEndpointVolume))


def _audio_worker():
    vol = None
    while True:
        op = _audio_q.get()
        for attempt in range(2):  # при сбое (сменилось устройство) пересоздаём endpoint
            try:
                if vol is None:
                    vol = _build_endpoint()
                if op is _MUTE:
                    vol.SetMute(0 if vol.GetMute() else 1, None)
                else:
                    if vol.GetMute():
                        vol.SetMute(0, None)
                    new = min(1.0, max(0.0, vol.GetMasterVolumeLevelScalar() + op))
                    vol.SetMasterVolumeLevelScalar(new, None)
                break
            except Exception:
                log.exception("volume op failed (attempt %d)", attempt)
                vol = None  # заставить пересоздать endpoint на второй попытке


threading.Thread(target=_audio_worker, name="audio", daemon=True).start()


def volume_up(steps: int = 4) -> None:
    _audio_q.put(steps * VOL_STEP)


def volume_down(steps: int = 4) -> None:
    _audio_q.put(-steps * VOL_STEP)


def mute() -> None:
    _audio_q.put(_MUTE)


# --- Медиа: изолированный подпроцесс mediactl.py --------------------------
def _media(action: str) -> None:
    try:
        subprocess.run(
            [sys.executable, _HELPER, action],
            timeout=8,
            creationflags=NO_WINDOW,
        )
    except Exception:
        log.exception("mediactl failed: %s", action)


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
