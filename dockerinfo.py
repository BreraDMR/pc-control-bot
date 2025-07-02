"""Мониторинг Docker-контейнеров, живущих в WSL2, с Windows-стороны через wsl.exe."""
import json
import subprocess

from config import WSL_DISTRO
from i18n import t

NO_WINDOW = 0x08000000


def _wsl(args: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    base = ["wsl.exe"]
    if WSL_DISTRO:
        base += ["-d", WSL_DISTRO]
    return subprocess.run(
        base + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=NO_WINDOW,
        timeout=timeout,
    )


def list_containers() -> list[dict]:
    r = _wsl(["docker", "ps", "-a", "--format", "{{json .}}"])
    items: list[dict] = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        items.append(
            {
                "name": d.get("Names", ""),
                "status": d.get("Status", ""),
                "state": d.get("State", ""),
                "image": d.get("Image", ""),
            }
        )
    return items


def overview_text(lang: str = "en") -> str:
    items = list_containers()
    if not items:
        return t("docker_unavailable", lang)
    running = [c for c in items if c["state"] == "running"]
    lines = [t("docker_head", lang, r=len(running), n=len(items)), ""]
    for c in sorted(items, key=lambda x: x["state"] != "running"):
        icon = "✅" if c["state"] == "running" else "⛔"
        if "unhealthy" in c["status"].lower():
            icon = "⚠️"
        lines.append(f"{icon} <b>{c['name']}</b>\n    <i>{c['status']}</i>")
    problems = [c for c in items if c["state"] != "running"]
    if problems:
        lines.append("\n" + t("docker_not_running", lang) + ", ".join(c["name"] for c in problems))
    return "\n".join(lines)


def logs(name: str, tail: int = 30, lang: str = "en") -> str:
    r = _wsl(["docker", "logs", "--tail", str(tail), name])
    out = (r.stdout or "").strip()
    err = (r.stderr or "").strip()
    combined = (out + "\n" + err).strip() if err else out
    return combined or t("logs_empty", lang)
