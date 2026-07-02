"""Питание и экран Windows: выключение, перезагрузка, блокировка, сон, мониторы."""
import ctypes
import subprocess

# Не показывать всплывающее консольное окно при вызове дочерних процессов.
NO_WINDOW = 0x08000000


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        args, capture_output=True, text=True, creationflags=NO_WINDOW
    )


def shutdown(delay_sec: int = 5) -> None:
    _run(["shutdown", "/s", "/f", "/t", str(delay_sec)])


def reboot(delay_sec: int = 5) -> None:
    _run(["shutdown", "/r", "/f", "/t", str(delay_sec)])


def abort() -> bool:
    """Отменить запланированное выключение/перезагрузку."""
    return _run(["shutdown", "/a"]).returncode == 0


def lock() -> None:
    ctypes.windll.user32.LockWorkStation()


def sleep() -> None:
    # SetSuspendState(bHibernate=0, bForce=1, bWakeupEventsDisabled=0)
    subprocess.run(
        ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
        creationflags=NO_WINDOW,
    )


def monitors_off() -> None:
    HWND_BROADCAST = 0xFFFF
    WM_SYSCOMMAND = 0x0112
    SC_MONITORPOWER = 0xF170
    MONITOR_OFF = 2
    ctypes.windll.user32.SendMessageW(
        HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, MONITOR_OFF
    )
