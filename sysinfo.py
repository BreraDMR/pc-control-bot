"""Системная статистика ПК через psutil: CPU, RAM, диски, аптайм, процессы."""
import platform
import time
from datetime import timedelta

import psutil


def fmt_bytes(n: float) -> str:
    for unit in ("Б", "КБ", "МБ", "ГБ", "ТБ"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} ПБ"


def stats_text() -> str:
    cpu = psutil.cpu_percent(interval=0.5)
    vm = psutil.virtual_memory()
    uptime = timedelta(seconds=int(time.time() - psutil.boot_time()))
    lines = [
        f"🖥 <b>{platform.node()}</b>",
        f"⚙️ CPU: <b>{cpu:.0f}%</b> · {psutil.cpu_count()} ядер",
        f"🧠 RAM: <b>{vm.percent:.0f}%</b> — {fmt_bytes(vm.used)} / {fmt_bytes(vm.total)}",
    ]
    for part in psutil.disk_partitions(all=False):
        if "cdrom" in part.opts or not part.fstype:
            continue
        try:
            du = psutil.disk_usage(part.mountpoint)
        except Exception:  # noqa: BLE001
            continue
        lines.append(
            f"💽 {part.device} <b>{du.percent:.0f}%</b> — "
            f"{fmt_bytes(du.used)} / {fmt_bytes(du.total)}"
        )
    lines.append(f"⏱ Аптайм: <b>{uptime}</b>")
    return "\n".join(lines)


def top_processes(by: str = "cpu", n: int = 6) -> str:
    procs = list(psutil.process_iter(["pid", "name", "memory_info"]))
    if by == "cpu":
        for p in procs:
            try:
                p.cpu_percent(None)  # прайминг
            except Exception:  # noqa: BLE001
                pass
        time.sleep(0.7)
        rows = []
        for p in procs:
            try:
                rows.append((p.info["pid"], p.info["name"], p.cpu_percent(None)))
            except Exception:  # noqa: BLE001
                pass
        rows.sort(key=lambda x: x[2], reverse=True)
        head = "🔥 <b>Топ процессов по CPU</b>"
        body = [f"• {name} (pid {pid}) — {val:.0f}%" for pid, name, val in rows[:n]]
    else:
        rows = []
        for p in procs:
            try:
                rows.append((p.info["pid"], p.info["name"], p.info["memory_info"].rss))
            except Exception:  # noqa: BLE001
                pass
        rows.sort(key=lambda x: x[2], reverse=True)
        head = "🧠 <b>Топ процессов по RAM</b>"
        body = [f"• {name} (pid {pid}) — {fmt_bytes(val)}" for pid, name, val in rows[:n]]
    return head + "\n" + "\n".join(body)
