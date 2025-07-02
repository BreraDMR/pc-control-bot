"""Самотест возможностей без запуска бота и без токена.

Запуск на Windows-ПК:  python test_capabilities.py
Проверяет: импорты, скриншot, список камер, доступ к Docker через WSL, статистику."""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass


def check(name, fn):
    try:
        res = fn()
        print(f"[OK]  {name}: {res}")
        return True
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] {name}: {type(e).__name__}: {e}")
        return False


def main() -> int:
    ok = True

    def imports():
        import mss, PIL, psutil, imageio_ffmpeg  # noqa: F401
        import telegram  # noqa: F401
        return "все модули на месте"

    ok &= check("Импорты", imports)

    def screenshot():
        import capture
        p = capture.screenshot()
        return f"{p.name} ({p.stat().st_size // 1024} КБ)"

    ok &= check("Скриншот", screenshot)

    def cameras():
        import capture
        cams = capture.list_cameras()
        return cams if cams else "камер не найдено (подключи USB-вебку)"

    ok &= check("Камеры", cameras)

    def docker():
        import dockerinfo
        items = dockerinfo.list_containers()
        return f"{len(items)} контейнеров" if items else "docker недоступен из WSL"

    ok &= check("Docker/WSL", docker)

    def stats_():
        import sysinfo
        return sysinfo.stats_text().splitlines()[0]

    ok &= check("Системная статистика", stats_)

    print("\nИТОГ:", "всё готово ✅" if ok else "есть проблемы, см. выше ⚠️")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
