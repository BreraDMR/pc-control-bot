"""Инлайн-клавиатуры (всё управление кнопками, без / команд)."""
from telegram import InlineKeyboardButton as B
from telegram import InlineKeyboardMarkup as M


def _back(to: str = "menu:main") -> B:
    return B("◀️ Назад", callback_data=to)


def main_menu() -> M:
    return M(
        [
            [B("🖥 Статус ПК", callback_data="act:status"),
             B("📊 Стата бота", callback_data="act:botstats")],
            [B("📸 Скриншот", callback_data="act:screenshot"),
             B("📷 Вебка", callback_data="act:webcam")],
            [B("🐳 Docker", callback_data="menu:docker"),
             B("⚙️ Процессы", callback_data="menu:proc")],
            [B("🔊 Звук/Медиа", callback_data="menu:sound"),
             B("🔒 Экран/Сон", callback_data="menu:screen")],
            [B("⚡ Питание", callback_data="menu:power"),
             B("🛠 Ещё", callback_data="menu:more")],
        ]
    )


def power_menu() -> M:
    return M(
        [
            [B("⏻ Выключить", callback_data="power:shutdown"),
             B("🔁 Перезагрузить", callback_data="power:reboot")],
            [B("⏳ Выключить через 15 мин", callback_data="power:shutdown15")],
            [B("❌ Отменить выключение", callback_data="power:abort")],
            [_back()],
        ]
    )


def confirm_menu(action: str, label: str) -> M:
    return M(
        [
            [B(f"✅ Да, {label}", callback_data=f"confirm:{action}")],
            [B("◀️ Отмена", callback_data="menu:power")],
        ]
    )


def screen_menu() -> M:
    return M(
        [
            [B("🔒 Заблокировать", callback_data="screen:lock"),
             B("😴 Сон", callback_data="screen:sleep")],
            [B("🌙 Мониторы выкл", callback_data="screen:monoff")],
            [_back()],
        ]
    )


def sound_menu() -> M:
    return M(
        [
            [B("🔉 −", callback_data="sound:down"),
             B("🔇 Mute", callback_data="sound:mute"),
             B("🔊 +", callback_data="sound:up")],
            [B("⏮", callback_data="sound:prev"),
             B("⏯", callback_data="sound:play"),
             B("⏭", callback_data="sound:next")],
            [_back()],
        ]
    )


def proc_menu() -> M:
    return M(
        [
            [B("🔥 Топ CPU", callback_data="proc:cpu"),
             B("🧠 Топ RAM", callback_data="proc:ram")],
            [_back()],
        ]
    )


def docker_menu(containers: list[dict]) -> M:
    rows = []
    for c in containers:
        icon = "✅" if c["state"] == "running" else "⛔"
        rows.append([B(f"{icon} {c['name']} — логи", callback_data=f"docker:logs:{c['name']}")])
    rows.append([B("🔄 Обновить", callback_data="menu:docker")])
    rows.append([_back()])
    return M(rows)


def more_menu(auto_on: bool = False, is_owner: bool = False) -> M:
    auto = "🟢 Автоснимки: ВКЛ" if auto_on else "⚪️ Автоснимки: ВЫКЛ"
    rows = [
        [B("🖼 Галерея вебки", callback_data="more:gallery")],
        [B("🗣 Озвучить текст", callback_data="more:tts")],
        [B("🌐 Открыть URL/приложение", callback_data="more:url")],
        [B("💻 Выполнить команду", callback_data="more:exec")],
        [B(auto, callback_data="more:autotoggle")],
    ]
    if is_owner:
        rows.append([B("👥 Админы", callback_data="menu:admins")])
    rows.append([_back()])
    return M(rows)


def back_only(to: str = "menu:main") -> M:
    return M([[_back(to)]])


# ── гость / демо / регистрация / админы ──────────────────────────────────
def guest_menu() -> M:
    return M(
        [
            [B("🎬 Посмотреть демо", callback_data="guest:demo")],
            [B("🔐 Запросить доступ", callback_data="guest:request")],
        ]
    )


def demo_menu() -> M:
    return M(
        [
            [B("🖥 Статус ПК", callback_data="demo:status"),
             B("📊 Стата бота", callback_data="demo:botstats")],
            [B("📸 Скриншот", callback_data="demo:photo"),
             B("📷 Вебка", callback_data="demo:photo")],
            [B("🐳 Docker", callback_data="demo:docker"),
             B("⚙️ Процессы", callback_data="demo:proc")],
            [B("⚡ Питание", callback_data="demo:action"),
             B("🔊 Звук/Медиа", callback_data="demo:action")],
            [B("🔐 Запросить доступ", callback_data="guest:request")],
            [B("◀️ Закрыть демо", callback_data="guest:home")],
        ]
    )


def approval_menu(user_id: int) -> M:
    return M(
        [
            [B("✅ Одобрить", callback_data=f"approve:{user_id}"),
             B("🚫 Отклонить", callback_data=f"deny:{user_id}")],
        ]
    )


def admins_menu(admin_list: list[dict]) -> M:
    rows = []
    for a in admin_list:
        if a.get("owner"):
            continue  # владельцев удалять нельзя
        label = a.get("name") or str(a["id"])
        rows.append([B(f"🗑 {label} ({a['id']})", callback_data=f"admin:rm:{a['id']}")])
    rows.append([_back("menu:more")])
    return M(rows)
