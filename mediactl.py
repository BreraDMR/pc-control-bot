"""Изолированный помощник управления медиа через SMTC (winrt).

Запускается media.py в ОТДЕЛЬНОМ процессе, чтобы возможный нативный сбой
или зависание winrt никогда не могли уронить/подвесить сам бот.
Использование:  python mediactl.py {play|next|prev}
Код возврата 0 — команда доставлена в активную медиасессию, иначе != 0."""
import asyncio
import sys


async def _control(action: str) -> bool:
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


def main() -> int:
    if len(sys.argv) < 2:
        return 2
    try:
        ok = asyncio.run(asyncio.wait_for(_control(sys.argv[1]), timeout=6))
    except Exception:
        ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
