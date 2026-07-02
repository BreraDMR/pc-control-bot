"""PC Control Bot — управление личным ПК из Telegram (только кнопки).

Возможности: статус ПК, скриншот, фото с вебки, статус Docker-контейнеров,
топ процессов, звук/медиа, блокировка/сон/мониторы, питание (с подтверждением),
TTS, запуск URL/приложений, произвольные команды, авто-снимки вебки.

Доступ строго по OWNER_IDS (см. security.restricted)."""
import asyncio
import html
import logging
from logging.handlers import RotatingFileHandler

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import admins
import capture
import demo
import dockerinfo
import keyboards as kb
import media
import power
import stats
import sysinfo
from config import AUTO_SNAP_MINUTES, BOT_TOKEN, DATA_DIR, OWNER_IDS
from security import owner_only, restricted

_fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
_file_handler = RotatingFileHandler(
    DATA_DIR / "bot.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
)
_file_handler.setFormatter(_fmt)
_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(_fmt)
logging.basicConfig(level=logging.INFO, handlers=[_file_handler, _stream_handler])
log = logging.getLogger("pc-control-bot")


async def _global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Логировать любые необработанные ошибки, чтобы бот не падал молча."""
    log.error("Необработанная ошибка при обработке апдейта", exc_info=context.error)

WELCOME = (
    "🎛 <b>Пульт управления ПК</b>\n"
    "Выбирай действие кнопками ниже."
)
AUTO_JOB = "autosnap"


# ── helpers ──────────────────────────────────────────────────────────────
async def _edit(update: Update, text: str, markup) -> None:
    """Отредактировать сообщение с меню; при неудаче — отправить новое."""
    q = update.callback_query
    try:
        await q.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=markup)
    except BadRequest as e:
        if "not modified" in str(e).lower():
            return
        await q.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=markup)


def _chunk(text: str, limit: int = 3500) -> str:
    return text if len(text) <= limit else text[:limit] + "\n…(обрезано)"


# ── команды ──────────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Стартовое меню зависит от роли: админ — пульт, гость — демо/запрос доступа."""
    uid = update.effective_user.id if update.effective_user else None
    stats.bump("start")
    if admins.is_admin(uid):
        await update.message.reply_text(
            WELCOME, parse_mode=ParseMode.HTML, reply_markup=kb.main_menu()
        )
    else:
        await update.message.reply_text(
            "👋 <b>Бот управления личным ПК.</b>\n\n"
            "У тебя пока нет доступа. Можешь посмотреть демо или запросить доступ у владельца.",
            parse_mode=ParseMode.HTML,
            reply_markup=kb.guest_menu(),
        )


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ввод текста для режимов TTS / URL / выполнить команду (только для админов)."""
    uid = update.effective_user.id if update.effective_user else None
    if not admins.is_admin(uid):
        await update.message.reply_text(
            "👋 Нет доступа. Посмотри демо или запроси доступ.",
            reply_markup=kb.guest_menu(),
        )
        return
    mode = context.user_data.pop("await", None)
    text = update.message.text or ""
    if mode == "tts":
        await asyncio.to_thread(media.speak, text)
        stats.bump("tts")
        await update.message.reply_text("🗣 Озвучено на ПК.", reply_markup=kb.main_menu())
    elif mode == "url":
        await asyncio.to_thread(media.open_url, text)
        stats.bump("open_url", text[:60])
        await update.message.reply_text(f"🌐 Открываю: {text}", reply_markup=kb.main_menu())
    elif mode == "exec":
        out = await asyncio.to_thread(media.run_powershell, text)
        stats.bump("exec", text[:40])
        await update.message.reply_text(
            f"💻 <code>{html.escape(text)}</code>\n<pre>{html.escape(_chunk(out))}</pre>",
            parse_mode=ParseMode.HTML,
            reply_markup=kb.main_menu(),
        )
    else:
        await update.message.reply_text(WELCOME, parse_mode=ParseMode.HTML,
                                        reply_markup=kb.main_menu())


# ── обработка кнопок ─────────────────────────────────────────────────────
@restricted
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    data = q.data or ""
    await q.answer()

    # --- навигация по меню ---
    if data == "menu:main":
        await _edit(update, WELCOME, kb.main_menu())
    elif data == "menu:power":
        await _edit(update, "⚡ <b>Питание</b>", kb.power_menu())
    elif data == "menu:screen":
        await _edit(update, "🔒 <b>Экран / Сон</b>", kb.screen_menu())
    elif data == "menu:sound":
        await _edit(update, "🔊 <b>Звук / Медиа</b>", kb.sound_menu())
    elif data == "menu:proc":
        await _edit(update, "⚙️ <b>Процессы</b>", kb.proc_menu())
    elif data == "menu:more":
        is_owner = admins.is_owner(update.effective_user.id)
        await _edit(update, "🛠 <b>Дополнительно</b>",
                    kb.more_menu(context.bot_data.get("auto_on", False), is_owner))
    elif data == "menu:admins":
        if not admins.is_owner(update.effective_user.id):
            await q.answer("Только для владельца", show_alert=True)
            return
        await _edit(update, _admins_text(), kb.admins_menu(admins.list_all()))
    elif data == "menu:docker":
        await _cb_docker(update, context)

    # --- простые действия ---
    elif data == "act:status":
        stats.bump("status")
        text = await asyncio.to_thread(sysinfo.stats_text)
        await _edit(update, text, kb.back_only())
    elif data == "act:botstats":
        stats.bump("botstats")
        await _edit(update, stats.text(), kb.back_only())
    elif data == "act:screenshot":
        await _cb_screenshot(update, context)
    elif data == "act:webcam":
        await _cb_webcam(update, context)

    # --- питание ---
    elif data == "power:shutdown":
        await _edit(update, "⏻ Выключить ПК <b>сейчас</b>?", kb.confirm_menu("shutdown", "выключить"))
    elif data == "power:reboot":
        await _edit(update, "🔁 Перезагрузить ПК <b>сейчас</b>?", kb.confirm_menu("reboot", "перезагрузить"))
    elif data == "power:shutdown15":
        await asyncio.to_thread(power.shutdown, 900)
        stats.bump("shutdown15")
        await _edit(update, "⏳ Выключение через 15 минут запланировано.\n"
                            "Нажми «Отменить выключение», чтобы отменить.", kb.power_menu())
    elif data == "power:abort":
        ok = await asyncio.to_thread(power.abort)
        stats.bump("abort")
        await _edit(update, "❌ Выключение отменено." if ok else "ℹ️ Отменять нечего.", kb.power_menu())
    elif data == "confirm:shutdown":
        await asyncio.to_thread(power.shutdown, 5)
        stats.bump("shutdown")
        await _edit(update, "⏻ Выключаюсь…", kb.back_only())
    elif data == "confirm:reboot":
        await asyncio.to_thread(power.reboot, 5)
        stats.bump("reboot")
        await _edit(update, "🔁 Перезагружаюсь…", kb.back_only())

    # --- экран/сон ---
    elif data == "screen:lock":
        await asyncio.to_thread(power.lock)
        stats.bump("lock")
        await _edit(update, "🔒 Экран заблокирован.", kb.screen_menu())
    elif data == "screen:sleep":
        stats.bump("sleep")
        await _edit(update, "😴 Отправляю ПК в сон…", kb.back_only())
        await asyncio.to_thread(power.sleep)
    elif data == "screen:monoff":
        await asyncio.to_thread(power.monitors_off)
        stats.bump("monitors_off")
        await _edit(update, "🌙 Мониторы выключены.", kb.screen_menu())

    # --- звук/медиа ---
    elif data.startswith("sound:"):
        await _cb_sound(update, context, data.split(":", 1)[1])

    # --- процессы ---
    elif data == "proc:cpu":
        stats.bump("proc_cpu")
        text = await asyncio.to_thread(sysinfo.top_processes, "cpu")
        await _edit(update, text, kb.proc_menu())
    elif data == "proc:ram":
        stats.bump("proc_ram")
        text = await asyncio.to_thread(sysinfo.top_processes, "ram")
        await _edit(update, text, kb.proc_menu())

    # --- docker логи ---
    elif data.startswith("docker:logs:"):
        name = data.split(":", 2)[2]
        stats.bump("docker_logs", name)
        text = await asyncio.to_thread(dockerinfo.logs, name, 30)
        await _edit(
            update,
            f"📄 <b>{html.escape(name)}</b> (хвост логов):\n<pre>{html.escape(_chunk(text))}</pre>",
            kb.back_only("menu:docker"),
        )

    # --- ещё ---
    elif data == "more:gallery":
        await _cb_gallery(update, context)
    elif data == "more:tts":
        context.user_data["await"] = "tts"
        await _edit(update, "🗣 Пришли текст — озвучу его на колонках ПК.", kb.back_only("menu:more"))
    elif data == "more:url":
        context.user_data["await"] = "url"
        await _edit(update, "🌐 Пришли URL или имя приложения для запуска.", kb.back_only("menu:more"))
    elif data == "more:exec":
        context.user_data["await"] = "exec"
        await _edit(update, "💻 Пришли PowerShell-команду для выполнения на ПК.", kb.back_only("menu:more"))
    elif data == "more:autotoggle":
        await _cb_auto_toggle(update, context)
    else:
        await q.answer("Неизвестная команда", show_alert=False)


# ── отдельные обработчики ────────────────────────────────────────────────
async def _cb_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer("Делаю скриншот…")
    stats.bump("screenshot")
    path = await asyncio.to_thread(capture.screenshot)
    with path.open("rb") as f:
        await context.bot.send_photo(
            update.effective_chat.id, photo=f, caption="📸 Скриншот рабочего стола",
            reply_markup=kb.main_menu(),
        )


async def _cb_webcam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer("Снимаю с вебки…")
    stats.bump("webcam")
    path = await asyncio.to_thread(capture.webcam_snapshot)
    if path is None:
        await context.bot.send_message(
            update.effective_chat.id,
            "📷 Камера не найдена. Подключи USB-вебку и попробуй снова.",
            reply_markup=kb.main_menu(),
        )
        return
    with path.open("rb") as f:
        await context.bot.send_photo(
            update.effective_chat.id, photo=f, caption="📷 Фото с вебки (сохранено в captures/webcam)",
            reply_markup=kb.main_menu(),
        )


async def _cb_docker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer("Опрашиваю Docker…")
    stats.bump("docker")
    items = await asyncio.to_thread(dockerinfo.list_containers)
    text = await asyncio.to_thread(dockerinfo.overview_text)
    await _edit(update, text, kb.docker_menu(items))


async def _cb_sound(update: Update, context: ContextTypes.DEFAULT_TYPE, what: str) -> None:
    actions = {
        "up": (media.volume_up, "🔊 Громче"),
        "down": (media.volume_down, "🔉 Тише"),
        "mute": (media.mute, "🔇 Mute"),
        "play": (media.media_playpause, "⏯ Play/Pause"),
        "next": (media.media_next, "⏭ Дальше"),
        "prev": (media.media_prev, "⏮ Назад"),
    }
    fn, label = actions[what]
    await asyncio.to_thread(fn)
    stats.bump(f"sound_{what}")
    await update.callback_query.answer(label)


async def _cb_gallery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    stats.bump("gallery")
    files = await asyncio.to_thread(capture.recent_webcam, 5)
    if not files:
        await _edit(update, "🖼 Пока нет снимков с вебки.", kb.back_only("menu:more"))
        return
    await update.callback_query.answer("Отправляю последние снимки…")
    for path in reversed(files):
        with path.open("rb") as f:
            await context.bot.send_photo(update.effective_chat.id, photo=f, caption=path.name)
    await context.bot.send_message(
        update.effective_chat.id, "Готово.", reply_markup=kb.main_menu()
    )


async def _cb_auto_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    jq = context.application.job_queue
    on = context.bot_data.get("auto_on", False)
    if on:
        for job in jq.get_jobs_by_name(AUTO_JOB):
            job.schedule_removal()
        context.bot_data["auto_on"] = False
        text = "⚪️ Авто-снимки вебки выключены."
    else:
        jq.run_repeating(auto_snap_job, interval=AUTO_SNAP_MINUTES * 60, first=10, name=AUTO_JOB)
        context.bot_data["auto_on"] = True
        text = f"🟢 Авто-снимки вебки включены (каждые {AUTO_SNAP_MINUTES} мин)."
    stats.bump("auto_toggle")
    await _edit(update, text, kb.more_menu(context.bot_data["auto_on"]))


# ── гость / демо / регистрация (публичные, без restricted) ──────────────
async def on_public(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    data = q.data or ""
    await q.answer()
    user = update.effective_user

    if data == "guest:home":
        await _edit(
            update,
            "👋 <b>Бот управления личным ПК.</b>\n\nПосмотри демо или запроси доступ.",
            kb.guest_menu(),
        )
    elif data == "guest:demo":
        stats.bump("demo")
        await _edit(update, demo.response("intro"), kb.demo_menu())
    elif data.startswith("demo:"):
        key = data.split(":", 1)[1]
        await _edit(update, demo.response(key), kb.demo_menu())
    elif data == "guest:request":
        # владелец не должен «запрашивать доступ»
        if admins.is_admin(user.id):
            await q.answer("У тебя уже есть доступ. Нажми /start", show_alert=True)
            return
        await _request_access(update, context)


async def _request_access(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    name = (user.full_name or "").strip() or "без имени"
    uname = f"@{user.username}" if user.username else "(нет username)"
    context.bot_data[f"reqname:{user.id}"] = name
    stats.bump("access_request", str(user.id))
    sent = 0
    for oid in OWNER_IDS:
        try:
            await context.bot.send_message(
                oid,
                f"🔐 <b>Запрос доступа</b>\n"
                f"Имя: <b>{html.escape(name)}</b>\n"
                f"Username: {html.escape(uname)}\n"
                f"ID: <code>{user.id}</code>",
                parse_mode=ParseMode.HTML,
                reply_markup=kb.approval_menu(user.id),
            )
            sent += 1
        except Exception as e:  # noqa: BLE001
            log.warning("request notify failed for %s: %s", oid, e)
    await _edit(
        update,
        "📨 Запрос отправлен владельцу. Дождись подтверждения — придёт уведомление."
        if sent else "⚠️ Не удалось связаться с владельцем. Попробуй позже.",
        kb.guest_menu(),
    )


@owner_only
async def on_owner_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    data = q.data or ""
    await q.answer()

    if data.startswith("approve:") or data.startswith("deny:"):
        action, uid_s = data.split(":", 1)
        uid = int(uid_s)
        name = context.bot_data.pop(f"reqname:{uid}", "")
        if action == "approve":
            admins.add_admin(uid, name)
            stats.bump("admin_approved", str(uid))
            await q.edit_message_text(
                f"✅ Доступ выдан: <b>{html.escape(name or str(uid))}</b> (<code>{uid}</code>)",
                parse_mode=ParseMode.HTML,
            )
            try:
                await context.bot.send_message(
                    uid,
                    "✅ Доступ одобрен! Теперь ты можешь управлять ПК.",
                    reply_markup=kb.main_menu(),
                )
            except Exception:  # noqa: BLE001
                pass
        else:
            stats.bump("admin_denied", str(uid))
            await q.edit_message_text(
                f"🚫 Запрос отклонён: <code>{uid}</code>", parse_mode=ParseMode.HTML
            )
            try:
                await context.bot.send_message(uid, "🚫 В доступе отказано.")
            except Exception:  # noqa: BLE001
                pass

    elif data.startswith("admin:rm:"):
        uid = int(data.split(":", 2)[2])
        admins.remove_admin(uid)
        stats.bump("admin_removed", str(uid))
        await _edit(update, _admins_text(), kb.admins_menu(admins.list_all()))


def _admins_text() -> str:
    lines = ["👥 <b>Админы</b>", ""]
    for a in admins.list_all():
        tag = "👑 владелец" if a.get("owner") else f"🔑 {a.get('name') or 'админ'}"
        lines.append(f"• {tag} — <code>{a['id']}</code>")
    lines.append("\nВладельцев удалять нельзя. Нажми 🗑, чтобы убрать обычного админа.")
    return "\n".join(lines)


# ── фоновые задачи / старт ──────────────────────────────────────────────
async def auto_snap_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    path = await asyncio.to_thread(capture.webcam_snapshot)
    if path is None:
        return
    from datetime import datetime
    for oid in OWNER_IDS:
        try:
            with path.open("rb") as f:
                await context.bot.send_photo(
                    oid, photo=f, caption=f"🕒 Авто-снимок {datetime.now():%H:%M}"
                )
        except Exception as e:  # noqa: BLE001
            log.warning("auto-snap send failed for %s: %s", oid, e)


async def post_init(app: Application) -> None:
    stats.bump("boot")
    try:
        text = await asyncio.to_thread(sysinfo.stats_text)
    except Exception:  # noqa: BLE001
        text = ""
    for oid in OWNER_IDS:
        try:
            await app.bot.send_message(
                oid,
                "🟢 <b>ПК загружен, бот на связи.</b>\n\n" + text,
                parse_mode=ParseMode.HTML,
                reply_markup=kb.main_menu(),
            )
        except Exception as e:  # noqa: BLE001
            log.warning("startup notify failed for %s: %s", oid, e)


_SINGLE_INSTANCE_SOCK = None


def _ensure_single_instance() -> None:
    """Не дать запуститься второму экземпляру (иначе конфликт polling)."""
    global _SINGLE_INSTANCE_SOCK
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", 47654))
    except OSError:
        log.warning("Другой экземпляр бота уже запущен — выхожу.")
        raise SystemExit(0)
    _SINGLE_INSTANCE_SOCK = s  # держим сокет открытым на всё время жизни процесса


def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN не задан в .env")
    if not OWNER_IDS:
        raise SystemExit("OWNER_IDS не заданы в .env — без владельцев бот управлять не даст")
    _ensure_single_instance()

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_start))
    # публичные: демо и запрос доступа
    app.add_handler(CallbackQueryHandler(on_public, pattern=r"^(guest|demo):"))
    # только владелец: аппрув запросов и управление админами
    app.add_handler(CallbackQueryHandler(on_owner_cb, pattern=r"^(approve|deny|admin):"))
    # управление ПК: только админы
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_error_handler(_global_error_handler)

    log.info("PC Control Bot запущен. Владельцев: %d", len(OWNER_IDS))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
