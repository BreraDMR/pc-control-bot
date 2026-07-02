"""PC Control Bot — управление личным ПК из Telegram (только кнопки).

Возможности: статус ПК, скриншот, фото с вебки, статус Docker-контейнеров,
топ процессов, звук/медиа, блокировка/сон/мониторы, питание (с подтверждением),
TTS, запуск URL/команд, авто-снимки вебки, выбор языка (en/ru/cs).

Доступ строго по OWNER_IDS + подтверждённым админам (см. security)."""
import asyncio
import html
import logging
from datetime import datetime
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
import prefs
import record
import stats
import sysinfo
from config import AUTO_SNAP_MINUTES, BOT_TOKEN, DATA_DIR, OWNER_IDS
from i18n import LANG_NAMES, t
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

AUTO_JOB = "autosnap"


async def _global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Логировать любые необработанные ошибки, чтобы бот не падал молча."""
    log.error("Необработанная ошибка при обработке апдейта", exc_info=context.error)


# ── helpers ──────────────────────────────────────────────────────────────
def _lang(update: Update) -> str:
    return prefs.get_lang(update.effective_user.id if update.effective_user else None)


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
    return text if len(text) <= limit else text[:limit] + "\n…"


# ── команды ──────────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Стартовое меню зависит от роли: админ — пульт, гость — демо/запрос доступа."""
    uid = update.effective_user.id if update.effective_user else None
    lang = prefs.get_lang(uid)
    stats.bump("start")
    if admins.is_admin(uid):
        await update.message.reply_text(
            t("welcome", lang), parse_mode=ParseMode.HTML, reply_markup=kb.main_menu(lang)
        )
    else:
        await update.message.reply_text(
            t("guest_welcome", lang), parse_mode=ParseMode.HTML, reply_markup=kb.guest_menu(lang)
        )


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ввод текста для режимов TTS / URL / выполнить команду (только для админов)."""
    uid = update.effective_user.id if update.effective_user else None
    lang = prefs.get_lang(uid)
    if not admins.is_admin(uid):
        await update.message.reply_text(t("no_access_text", lang), reply_markup=kb.guest_menu(lang))
        return
    mode = context.user_data.pop("await", None)
    text = update.message.text or ""
    if mode == "tts":
        await asyncio.to_thread(media.speak, text)
        stats.bump("tts")
        await update.message.reply_text(t("tts_done", lang), reply_markup=kb.main_menu(lang))
    elif mode == "url":
        await asyncio.to_thread(media.open_url, text)
        stats.bump("open_url", text[:60])
        await update.message.reply_text(t("url_opening", lang, text=text), reply_markup=kb.main_menu(lang))
    elif mode == "exec":
        out = await asyncio.to_thread(media.run_powershell, text)
        stats.bump("exec", text[:40])
        await update.message.reply_text(
            f"💻 <code>{html.escape(text)}</code>\n<pre>{html.escape(_chunk(out))}</pre>",
            parse_mode=ParseMode.HTML,
            reply_markup=kb.main_menu(lang),
        )
    else:
        await update.message.reply_text(
            t("welcome", lang), parse_mode=ParseMode.HTML, reply_markup=kb.main_menu(lang)
        )


# ── обработка кнопок (только админы) ─────────────────────────────────────
@restricted
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    data = q.data or ""
    lang = _lang(update)
    await q.answer()

    # --- навигация по меню ---
    if data == "menu:main":
        await _edit(update, t("welcome", lang), kb.main_menu(lang))
    elif data == "menu:power":
        await _edit(update, t("title_power", lang), kb.power_menu(lang))
    elif data == "menu:screen":
        await _edit(update, t("title_screen", lang), kb.screen_menu(lang))
    elif data == "menu:sound":
        await _edit(update, t("title_sound", lang), kb.sound_menu(lang))
    elif data == "menu:proc":
        await _edit(update, t("title_proc", lang), kb.proc_menu(lang))
    elif data == "menu:more":
        is_owner = admins.is_owner(update.effective_user.id)
        await _edit(update, t("title_more", lang),
                    kb.more_menu(lang, context.bot_data.get("auto_on", False), is_owner))
    elif data == "menu:lang":
        await _edit(update, t("title_language", lang), kb.language_menu(lang, "menu:more"))
    elif data == "menu:admins":
        if not admins.is_owner(update.effective_user.id):
            await q.answer(t("owner_only_short", lang), show_alert=True)
            return
        await _edit(update, _admins_text(lang), kb.admins_menu(lang, admins.list_all()))
    elif data == "menu:docker":
        await _cb_docker(update, context, lang)

    # --- простые действия ---
    elif data == "act:status":
        stats.bump("status")
        text = await asyncio.to_thread(sysinfo.stats_text, lang)
        await _edit(update, text, kb.back_only(lang))
    elif data == "act:botstats":
        stats.bump("botstats")
        await _edit(update, stats.text(lang), kb.back_only(lang))
    elif data == "act:screenshot":
        await _cb_screenshot(update, context, lang)
    elif data == "act:webcam":
        await _cb_webcam(update, context, lang)

    # --- питание ---
    elif data == "power:shutdown":
        await _edit(update, t("q_shutdown", lang), kb.confirm_menu(lang, "shutdown"))
    elif data == "power:reboot":
        await _edit(update, t("q_reboot", lang), kb.confirm_menu(lang, "reboot"))
    elif data == "power:shutdown15":
        await asyncio.to_thread(power.shutdown, 900)
        stats.bump("shutdown15")
        await _edit(update, t("shutdown15_ok", lang), kb.power_menu(lang))
    elif data == "power:abort":
        ok = await asyncio.to_thread(power.abort)
        stats.bump("abort")
        await _edit(update, t("abort_ok", lang) if ok else t("abort_none", lang), kb.power_menu(lang))
    elif data == "confirm:shutdown":
        await asyncio.to_thread(power.shutdown, 5)
        stats.bump("shutdown")
        await _edit(update, t("shutting_down", lang), kb.back_only(lang))
    elif data == "confirm:reboot":
        await asyncio.to_thread(power.reboot, 5)
        stats.bump("reboot")
        await _edit(update, t("rebooting", lang), kb.back_only(lang))

    # --- экран/сон ---
    elif data == "screen:lock":
        await asyncio.to_thread(power.lock)
        stats.bump("lock")
        await _edit(update, t("lock_ok", lang), kb.screen_menu(lang))
    elif data == "screen:sleep":
        stats.bump("sleep")
        await _edit(update, t("sleep_ok", lang), kb.back_only(lang))
        await asyncio.to_thread(power.sleep)
    elif data == "screen:monoff":
        await asyncio.to_thread(power.monitors_off)
        stats.bump("monitors_off")
        await _edit(update, t("monoff_ok", lang), kb.screen_menu(lang))

    # --- звук/медиа ---
    elif data.startswith("sound:"):
        await _cb_sound(update, context, data.split(":", 1)[1], lang)

    # --- процессы ---
    elif data == "proc:cpu":
        stats.bump("proc_cpu")
        text = await asyncio.to_thread(sysinfo.top_processes, "cpu", lang)
        await _edit(update, text, kb.proc_menu(lang))
    elif data == "proc:ram":
        stats.bump("proc_ram")
        text = await asyncio.to_thread(sysinfo.top_processes, "ram", lang)
        await _edit(update, text, kb.proc_menu(lang))

    # --- docker логи ---
    elif data.startswith("docker:logs:"):
        name = data.split(":", 2)[2]
        stats.bump("docker_logs", name)
        text = await asyncio.to_thread(dockerinfo.logs, name, 30, lang)
        await _edit(
            update,
            t("docker_logs_title", lang, name=html.escape(name)) + f"\n<pre>{html.escape(_chunk(text))}</pre>",
            kb.back_only(lang, "menu:docker"),
        )

    # --- ещё ---
    elif data == "more:gallery":
        await _cb_gallery(update, context, lang)
    elif data == "more:tts":
        context.user_data["await"] = "tts"
        await _edit(update, t("ask_tts", lang), kb.back_only(lang, "menu:more"))
    elif data == "more:url":
        context.user_data["await"] = "url"
        await _edit(update, t("ask_url", lang), kb.back_only(lang, "menu:more"))
    elif data == "more:exec":
        context.user_data["await"] = "exec"
        await _edit(update, t("ask_exec", lang), kb.back_only(lang, "menu:more"))
    elif data == "more:autotoggle":
        await _cb_auto_toggle(update, context, lang)

    # --- запись видео/аудио ---
    elif data == "menu:record":
        await _edit(update, t("title_record", lang), kb.record_menu(lang))
    elif data == "rec:vmenu":
        await _edit(update, t("title_rec_vdur", lang), kb.rec_duration_menu(lang, "v"))
    elif data == "rec:amenu":
        await _edit(update, t("title_rec_adur", lang), kb.rec_duration_menu(lang, "a"))
    elif data.startswith("rec:v:"):
        await _cb_record_video(update, context, int(data.split(":")[2]), lang)
    elif data.startswith("rec:a:"):
        await _cb_record_audio(update, context, int(data.split(":")[2]), lang)

    else:
        await q.answer(t("unknown_cmd", lang), show_alert=False)


# ── отдельные обработчики ────────────────────────────────────────────────
async def _cb_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str) -> None:
    await update.callback_query.answer(t("ans_screenshot", lang))
    stats.bump("screenshot")
    path = await asyncio.to_thread(capture.screenshot)
    with path.open("rb") as f:
        await context.bot.send_photo(
            update.effective_chat.id, photo=f, caption=t("cap_screenshot", lang),
            reply_markup=kb.main_menu(lang),
        )


async def _cb_webcam(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str) -> None:
    await update.callback_query.answer(t("ans_webcam", lang))
    stats.bump("webcam")
    path = await asyncio.to_thread(capture.webcam_snapshot)
    if path is None:
        await context.bot.send_message(
            update.effective_chat.id, t("webcam_none", lang), reply_markup=kb.main_menu(lang)
        )
        return
    with path.open("rb") as f:
        await context.bot.send_photo(
            update.effective_chat.id, photo=f, caption=t("cap_webcam", lang),
            reply_markup=kb.main_menu(lang),
        )


async def _cb_record_video(update: Update, context: ContextTypes.DEFAULT_TYPE, sec: int, lang: str) -> None:
    await _edit(update, t("rec_working", lang, sec=sec), kb.back_only(lang, "menu:record"))
    stats.bump("rec_video", str(sec))
    path = await asyncio.to_thread(record.record_video, sec)
    if path is None:
        await context.bot.send_message(update.effective_chat.id, t("webcam_none", lang), reply_markup=kb.main_menu(lang))
        return
    with path.open("rb") as f:
        await context.bot.send_video(
            update.effective_chat.id, video=f, caption=t("rec_video_cap", lang, sec=sec),
            reply_markup=kb.main_menu(lang),
        )


async def _cb_record_audio(update: Update, context: ContextTypes.DEFAULT_TYPE, sec: int, lang: str) -> None:
    await _edit(update, t("rec_working", lang, sec=sec), kb.back_only(lang, "menu:record"))
    stats.bump("rec_audio", str(sec))
    path = await asyncio.to_thread(record.record_audio, sec)
    if path is None:
        await context.bot.send_message(update.effective_chat.id, t("rec_no_mic", lang), reply_markup=kb.main_menu(lang))
        return
    with path.open("rb") as f:
        await context.bot.send_voice(
            update.effective_chat.id, voice=f, caption=t("rec_audio_cap", lang, sec=sec),
            reply_markup=kb.main_menu(lang),
        )


async def _cb_docker(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str) -> None:
    await update.callback_query.answer(t("ans_docker", lang))
    stats.bump("docker")
    items = await asyncio.to_thread(dockerinfo.list_containers)
    text = await asyncio.to_thread(dockerinfo.overview_text, lang)
    await _edit(update, text, kb.docker_menu(lang, items))


async def _cb_sound(update: Update, context: ContextTypes.DEFAULT_TYPE, what: str, lang: str) -> None:
    actions = {
        "up": (media.volume_up, "ans_louder"),
        "down": (media.volume_down, "ans_quieter"),
        "mute": (media.mute, "ans_mute"),
        "play": (media.media_playpause, "ans_play"),
        "next": (media.media_next, "ans_next"),
        "prev": (media.media_prev, "ans_prev"),
    }
    fn, key = actions[what]
    await asyncio.to_thread(fn)
    stats.bump(f"sound_{what}")
    await update.callback_query.answer(t(key, lang))


async def _cb_gallery(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str) -> None:
    stats.bump("gallery")
    files = await asyncio.to_thread(capture.recent_webcam, 5)
    if not files:
        await _edit(update, t("gallery_empty", lang), kb.back_only(lang, "menu:more"))
        return
    await update.callback_query.answer(t("gallery_sending", lang))
    for path in reversed(files):
        with path.open("rb") as f:
            await context.bot.send_photo(update.effective_chat.id, photo=f, caption=path.name)
    await context.bot.send_message(update.effective_chat.id, t("done", lang), reply_markup=kb.main_menu(lang))


async def _cb_auto_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str) -> None:
    jq = context.application.job_queue
    on = context.bot_data.get("auto_on", False)
    if on:
        for job in jq.get_jobs_by_name(AUTO_JOB):
            job.schedule_removal()
        context.bot_data["auto_on"] = False
        text = t("auto_off_msg", lang)
    else:
        jq.run_repeating(auto_snap_job, interval=AUTO_SNAP_MINUTES * 60, first=10, name=AUTO_JOB)
        context.bot_data["auto_on"] = True
        text = t("auto_on_msg", lang, n=AUTO_SNAP_MINUTES)
    stats.bump("auto_toggle")
    await _edit(update, text, kb.more_menu(lang, context.bot_data["auto_on"],
                                           admins.is_owner(update.effective_user.id)))


def _admins_text(lang: str) -> str:
    lines = [t("admins_head", lang), ""]
    for a in admins.list_all():
        tag = t("admins_owner_tag", lang) if a.get("owner") else t("admins_admin_tag", lang)
        lines.append(f"• {tag} — <code>{a['id']}</code>")
    lines.append(t("admins_hint", lang))
    return "\n".join(lines)


# ── публичные (гость / демо / язык / регистрация) ────────────────────────
async def on_public(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    data = q.data or ""
    lang = _lang(update)
    await q.answer()
    user = update.effective_user

    if data == "guest:home":
        await _edit(update, t("guest_home", lang), kb.guest_menu(lang))
    elif data == "guest:demo":
        stats.bump("demo")
        await _edit(update, demo.response("intro", lang), kb.demo_menu(lang))
    elif data.startswith("demo:"):
        key = data.split(":", 1)[1]
        await _edit(update, demo.response(key, lang), kb.demo_menu(lang))
    elif data == "guest:lang":
        await _edit(update, t("title_language", lang), kb.language_menu(lang, "guest:home"))
    elif data.startswith("lang:set:"):
        await _cb_set_lang(update, context, data.split(":", 2)[2])
    elif data == "guest:request":
        if admins.is_admin(user.id):
            await q.answer(t("already_access", lang), show_alert=True)
            return
        await _request_access(update, context, lang)


async def _cb_set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE, code: str) -> None:
    user = update.effective_user
    if code not in LANG_NAMES:
        return
    prefs.set_lang(user.id, code)
    stats.bump("lang_set", code)
    # перерисовать домашний экран в новом языке по роли
    if admins.is_admin(user.id):
        await _edit(update, t("welcome", code), kb.main_menu(code))
    else:
        await _edit(update, t("guest_home", code), kb.guest_menu(code))


async def _request_access(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str) -> None:
    user = update.effective_user
    name = (user.full_name or "").strip() or "—"
    uname = f"@{user.username}" if user.username else "—"
    context.bot_data[f"reqname:{user.id}"] = name
    stats.bump("access_request", str(user.id))
    sent = 0
    for oid in OWNER_IDS:
        olang = prefs.get_lang(oid)
        try:
            await context.bot.send_message(
                oid,
                t("req_title", olang, name=html.escape(name), uname=html.escape(uname), id=user.id),
                parse_mode=ParseMode.HTML,
                reply_markup=kb.approval_menu(olang, user.id),
            )
            sent += 1
        except Exception as e:  # noqa: BLE001
            log.warning("request notify failed for %s: %s", oid, e)
    await _edit(update, t("req_sent", lang) if sent else t("req_failed", lang), kb.guest_menu(lang))


@owner_only
async def on_owner_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    data = q.data or ""
    lang = _lang(update)
    await q.answer()

    if data.startswith("approve:") or data.startswith("deny:"):
        action, uid_s = data.split(":", 1)
        uid = int(uid_s)
        name = context.bot_data.pop(f"reqname:{uid}", "")
        if action == "approve":
            admins.add_admin(uid, name)
            stats.bump("admin_approved", str(uid))
            await q.edit_message_text(
                t("approved_owner", lang, name=html.escape(name or str(uid)), id=uid),
                parse_mode=ParseMode.HTML,
            )
            try:
                ulang = prefs.get_lang(uid)
                await context.bot.send_message(uid, t("approved_user", ulang), reply_markup=kb.main_menu(ulang))
            except Exception:  # noqa: BLE001
                pass
        else:
            stats.bump("admin_denied", str(uid))
            await q.edit_message_text(t("denied_owner", lang, id=uid), parse_mode=ParseMode.HTML)
            try:
                await context.bot.send_message(uid, t("denied_user", prefs.get_lang(uid)))
            except Exception:  # noqa: BLE001
                pass

    elif data.startswith("admin:rm:"):
        uid = int(data.split(":", 2)[2])
        admins.remove_admin(uid)
        stats.bump("admin_removed", str(uid))
        await _edit(update, _admins_text(lang), kb.admins_menu(lang, admins.list_all()))


# ── фоновые задачи / старт ──────────────────────────────────────────────
async def auto_snap_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    path = await asyncio.to_thread(capture.webcam_snapshot)
    if path is None:
        return
    for oid in OWNER_IDS:
        try:
            with path.open("rb") as f:
                await context.bot.send_photo(
                    oid, photo=f, caption=t("autosnap_cap", prefs.get_lang(oid), time=f"{datetime.now():%H:%M}")
                )
        except Exception as e:  # noqa: BLE001
            log.warning("auto-snap send failed for %s: %s", oid, e)


async def post_init(app: Application) -> None:
    stats.bump("boot")
    for oid in OWNER_IDS:
        olang = prefs.get_lang(oid)
        try:
            text = await asyncio.to_thread(sysinfo.stats_text, olang)
        except Exception:  # noqa: BLE001
            text = ""
        try:
            await app.bot.send_message(
                oid, t("startup", olang) + text, parse_mode=ParseMode.HTML, reply_markup=kb.main_menu(olang)
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
    _SINGLE_INSTANCE_SOCK = s


def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN не задан в .env")
    if not OWNER_IDS:
        raise SystemExit("OWNER_IDS не заданы в .env — без владельцев бот управлять не даст")
    _ensure_single_instance()

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_start))
    # публичные: демо, запрос доступа, выбор языка
    app.add_handler(CallbackQueryHandler(on_public, pattern=r"^(guest|demo|lang):"))
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
