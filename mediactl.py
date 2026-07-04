"""Изолированный помощник звука/медиа — выполняет ВСЮ нативную работу
(Core Audio через pycaw/comtypes и SMTC через winrt) в СВОЁМ процессе.

media.py вызывает его через subprocess, поэтому нативный сбой (access
violation в _ctypes.pyd при работе comtypes из пула потоков) или зависание
winrt на Python 3.14 убивают только этот короткоживущий процесс, а сам бот
остаётся цел. Каждый запуск — один вызов в одном главном потоке с одним
CoInitialize, что снимает проблему межпоточного COM.

Использование:
  mediactl.py volup <steps>   — громче
  mediactl.py voldown <steps> — тише
  mediactl.py mute            — переключить mute
  mediactl.py play|next|prev  — медиа (SMTC, откат на мультимедиа-клавишу)
Код возврата 0 — успех, иначе != 0.
"""
import sys

VOL_STEP = 0.02  # доля громкости (0..1) на один «шаг»
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001
_MEDIA_VK = {"play": 0xB3, "next": 0xB0, "prev": 0xB1}


def _volume(delta):
    """delta=None → переключить mute; иначе изменить громкость на delta."""
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
    v = cast(dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None), POINTER(IAudioEndpointVolume))
    if delta is None:
        v.SetMute(0 if v.GetMute() else 1, None)
    else:
        if v.GetMute():
            v.SetMute(0, None)
        new = min(1.0, max(0.0, v.GetMasterVolumeLevelScalar() + delta))
        v.SetMasterVolumeLevelScalar(new, None)


def _tap(vk):
    import ctypes

    ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_EXTENDEDKEY, 0)
    ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)


async def _smtc(action):
    from winrt.windows.media.control import (
        GlobalSystemMediaTransportControlsSessionManager as Manager,
    )

    mgr = await Manager.request_async()
    session = mgr.get_current_session()
    if session is None:
        return False
    if action == "play":
        return bool(await session.try_toggle_play_pause_async())
    if action == "next":
        return bool(await session.try_skip_next_async())
    if action == "prev":
        return bool(await session.try_skip_previous_async())
    return False


def _media(action):
    import asyncio

    try:
        ok = asyncio.run(asyncio.wait_for(_smtc(action), timeout=6))
    except Exception:
        ok = False
    if not ok:
        _tap(_MEDIA_VK[action])  # фолбэк тоже в этом изолированном процессе


def main():
    if len(sys.argv) < 2:
        return 2
    cmd = sys.argv[1]
    if cmd == "volup":
        _volume(int(sys.argv[2]) * VOL_STEP)
    elif cmd == "voldown":
        _volume(-int(sys.argv[2]) * VOL_STEP)
    elif cmd == "mute":
        _volume(None)
    elif cmd in _MEDIA_VK:
        _media(cmd)
    else:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
