"""Системная статистика ПК через psutil: CPU, RAM, диски, аптайм, процессы."""
import platform
import time
from datetime import timedelta

import psutil

from i18n import t

_UNITS = {
    "en": ("B", "KB", "MB", "GB", "TB"),
    "ru": ("Б", "КБ", "МБ", "ГБ", "ТБ"),
    "cs": ("B", "KB", "MB", "GB", "TB"),
}


def fmt_bytes(n: float, lang: str = "en") -> str:
    units = _UNITS.get(lang, _UNITS["en"])
    for unit in units:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def stats_text(lang: str = "en") -> str:
    cpu = psutil.cpu_percent(interval=0.5)
    vm = psutil.virtual_memory()
    uptime = timedelta(seconds=int(time.time() - psutil.boot_time()))
    lines = [
        f"🖥 <b>{platform.node()}</b>",
        t("sys_cpu", lang, cpu=f"{cpu:.0f}", cores=psutil.cpu_count()),
        t("sys_ram", lang, p=f"{vm.percent:.0f}", used=fmt_bytes(vm.used, lang), total=fmt_bytes(vm.total, lang)),
    ]
    for part in psutil.disk_partitions(all=False):
        if "cdrom" in part.opts or not part.fstype:
            continue
        try:
            du = psutil.disk_usage(part.mountpoint)
        except Exception:  # noqa: BLE001
            continue
        lines.append(t("sys_disk", lang, dev=part.device, p=f"{du.percent:.0f}",
                       used=fmt_bytes(du.used, lang), total=fmt_bytes(du.total, lang)))
    lines.append(t("sys_uptime", lang, up=uptime))
    return "\n".join(lines)


def top_processes(by: str = "cpu", lang: str = "en", n: int = 6) -> str:
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
        head = t("top_cpu_head", lang)
        body = [f"• {name} (pid {pid}) — {val:.0f}%" for pid, name, val in rows[:n]]
    else:
        rows = []
        for p in procs:
            try:
                rows.append((p.info["pid"], p.info["name"], p.info["memory_info"].rss))
            except Exception:  # noqa: BLE001
                pass
        rows.sort(key=lambda x: x[2], reverse=True)
        head = t("top_ram_head", lang)
        body = [f"• {name} (pid {pid}) — {fmt_bytes(val, lang)}" for pid, name, val in rows[:n]]
    return head + "\n" + "\n".join(body)
