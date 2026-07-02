"""Демо-режим: показывает, как выглядит бот, на выдуманных данных.

Никаких реальных действий с ПК — только заранее заготовленные тексты."""

TAG = "🎬 <b>ДЕМО</b> — данные вымышленные, реального управления нет.\n\n"

STATUS = TAG + (
    "🖥 <b>HOME-PC</b>\n"
    "⚙️ CPU: <b>17%</b> · 8 ядер\n"
    "🧠 RAM: <b>42%</b> — 6.7 ГБ / 16.0 ГБ\n"
    "💽 C:\\ <b>63%</b> — 297 ГБ / 465 ГБ\n"
    "⏱ Аптайм: <b>2 days, 4:11:37</b>"
)

DOCKER = TAG + (
    "🐳 <b>Docker</b> — запущено 4/5\n\n"
    "✅ <b>finance-bot</b>\n    <i>Up 2 hours</i>\n"
    "✅ <b>site</b>\n    <i>Up 2 hours</i>\n"
    "✅ <b>ollama</b>\n    <i>Up 2 hours</i>\n"
    "✅ <b>caddy</b>\n    <i>Up 2 hours</i>\n"
    "⛔ <b>backup-job</b>\n    <i>Exited (0) 5 minutes ago</i>\n\n"
    "⚠️ Не запущены: backup-job"
)

PROC = TAG + (
    "🔥 <b>Топ процессов по CPU</b>\n"
    "• chrome.exe (pid 4821) — 14%\n"
    "• python.exe (pid 1337) — 6%\n"
    "• Code.exe (pid 9002) — 4%\n"
    "• dwm.exe (pid 1120) — 2%\n"
    "• explorer.exe (pid 764) — 1%"
)

BOTSTATS = TAG + (
    "📊 <b>Статистика бота</b>\n"
    "⏱ Бот работает: <b>1 day, 3:22:10</b>\n"
    "🔢 Всего действий: <b>128</b>\n\n"
    "<b>По типам:</b>\n"
    "• status: 34\n• screenshot: 22\n• webcam: 18\n• docker: 15\n• shutdown: 3"
)

PHOTO = TAG + "📸 Здесь пришло бы реальное фото (скриншот/вебка).\nВ демо оно не делается."

ACTION = TAG + "Здесь выполнилось бы реальное действие на ПК. В демо оно отключено."

INTRO = (
    "🎬 <b>Демо пульта управления ПК</b>\n\n"
    "Так выглядит бот в работе. Реальные кнопки умеют:\n"
    "• 🖥 статус ПК, 📊 статистика\n"
    "• 📸 скриншот, 📷 фото с вебки\n"
    "• 🐳 статус Docker-контейнеров и их логи\n"
    "• ⚙️ топ процессов\n"
    "• 🔊 звук/медиа, 🔒 блокировка/сон/мониторы\n"
    "• ⚡ выключение/перезагрузка (с подтверждением)\n\n"
    "Потыкай кнопки ниже — всё на демо-данных."
)


def response(key: str) -> str:
    return {
        "status": STATUS,
        "docker": DOCKER,
        "proc": PROC,
        "botstats": BOTSTATS,
        "photo": PHOTO,
        "action": ACTION,
        "intro": INTRO,
    }.get(key, INTRO)
