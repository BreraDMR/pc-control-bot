"""Инлайн-клавиатуры (всё управление кнопками). Все подписи локализованы через i18n."""
from __future__ import annotations

from telegram import InlineKeyboardButton as B
from telegram import InlineKeyboardMarkup as M

from i18n import LANG_NAMES, t


def _back(lang: str, to: str = "menu:main") -> B:
    return B(t("btn_back", lang), callback_data=to)


def main_menu(lang: str) -> M:
    return M(
        [
            [B(t("btn_status", lang), callback_data="act:status"),
             B(t("btn_botstats", lang), callback_data="act:botstats")],
            [B(t("btn_screenshot", lang), callback_data="act:screenshot"),
             B(t("btn_webcam", lang), callback_data="act:webcam")],
            [B(t("btn_docker", lang), callback_data="menu:docker"),
             B(t("btn_proc", lang), callback_data="menu:proc")],
            [B(t("btn_sound", lang), callback_data="menu:sound"),
             B(t("btn_screen", lang), callback_data="menu:screen")],
            [B(t("btn_power", lang), callback_data="menu:power"),
             B(t("btn_more", lang), callback_data="menu:more")],
        ]
    )


def power_menu(lang: str) -> M:
    return M(
        [
            [B(t("btn_shutdown", lang), callback_data="power:shutdown"),
             B(t("btn_reboot", lang), callback_data="power:reboot")],
            [B(t("btn_shutdown15", lang), callback_data="power:shutdown15")],
            [B(t("btn_abort", lang), callback_data="power:abort")],
            [_back(lang)],
        ]
    )


def confirm_menu(lang: str, action: str) -> M:
    label_key = "btn_confirm_shutdown" if action == "shutdown" else "btn_confirm_reboot"
    return M(
        [
            [B(t(label_key, lang), callback_data=f"confirm:{action}")],
            [B(t("btn_cancel", lang), callback_data="menu:power")],
        ]
    )


def screen_menu(lang: str) -> M:
    return M(
        [
            [B(t("btn_lock", lang), callback_data="screen:lock"),
             B(t("btn_sleep", lang), callback_data="screen:sleep")],
            [B(t("btn_monoff", lang), callback_data="screen:monoff")],
            [_back(lang)],
        ]
    )


def sound_menu(lang: str) -> M:
    return M(
        [
            [B("🔉 −", callback_data="sound:down"),
             B(t("btn_mute", lang), callback_data="sound:mute"),
             B("🔊 +", callback_data="sound:up")],
            [B("⏮", callback_data="sound:prev"),
             B("⏯", callback_data="sound:play"),
             B("⏭", callback_data="sound:next")],
            [_back(lang)],
        ]
    )


def proc_menu(lang: str) -> M:
    return M(
        [
            [B(t("btn_topcpu", lang), callback_data="proc:cpu"),
             B(t("btn_topram", lang), callback_data="proc:ram")],
            [_back(lang)],
        ]
    )


def docker_menu(lang: str, containers: list[dict]) -> M:
    rows = []
    suffix = t("logs_suffix", lang)
    for c in containers:
        icon = "✅" if c["state"] == "running" else "⛔"
        rows.append([B(f"{icon} {c['name']} — {suffix}", callback_data=f"docker:logs:{c['name']}")])
    rows.append([B(t("btn_refresh", lang), callback_data="menu:docker")])
    rows.append([_back(lang)])
    return M(rows)


def more_menu(lang: str, auto_on: bool = False, is_owner: bool = False) -> M:
    auto = t("btn_auto_on", lang) if auto_on else t("btn_auto_off", lang)
    rows = [
        [B(t("btn_record", lang), callback_data="menu:record")],
        [B(t("btn_gallery", lang), callback_data="more:gallery")],
        [B(t("btn_tts", lang), callback_data="more:tts")],
        [B(t("btn_url", lang), callback_data="more:url")],
        [B(t("btn_exec", lang), callback_data="more:exec")],
        [B(auto, callback_data="more:autotoggle")],
        [B(t("btn_language", lang), callback_data="menu:lang")],
    ]
    if is_owner:
        rows.append([B(t("btn_admins", lang), callback_data="menu:admins")])
    rows.append([_back(lang)])
    return M(rows)


REC_DURATIONS = (5, 10, 15, 30, 60)


def record_menu(lang: str, camera_name: str | None = None) -> M:
    cam = camera_name or "—"
    return M(
        [
            [B(t("btn_rec_video", lang), callback_data="rec:vmenu")],
            [B(t("btn_rec_audio", lang), callback_data="rec:amenu")],
            [B(f"📷 {t('cam_label', lang)}: {cam}", callback_data="cam:menu")],
            [_back(lang, "menu:more")],
        ]
    )


def camera_menu(lang: str, cameras: list[str], selected: str | None) -> M:
    rows = []
    for idx, name in enumerate(cameras):
        mark = "✅ " if name == selected else ""
        rows.append([B(f"{mark}{name}", callback_data=f"cam:set:{idx}")])
    rows.append([_back(lang, "menu:record")])
    return M(rows)


def rec_duration_menu(lang: str, kind: str) -> M:
    # kind: 'v' (video) | 'a' (audio)
    row = [B(f"{s}s", callback_data=f"rec:{kind}:{s}") for s in REC_DURATIONS]
    return M([row, [_back(lang, "menu:record")]])


def language_menu(lang: str, back_to: str = "menu:more") -> M:
    rows = [[B(name, callback_data=f"lang:set:{code}")] for code, name in LANG_NAMES.items()]
    rows.append([_back(lang, back_to)])
    return M(rows)


def back_only(lang: str, to: str = "menu:main") -> M:
    return M([[_back(lang, to)]])


# ── гость / демо / регистрация / админы ──────────────────────────────────
def guest_menu(lang: str) -> M:
    return M(
        [
            [B(t("btn_demo", lang), callback_data="guest:demo")],
            [B(t("btn_request", lang), callback_data="guest:request")],
            [B(t("btn_language", lang), callback_data="guest:lang")],
        ]
    )


def demo_menu(lang: str) -> M:
    return M(
        [
            [B(t("btn_status", lang), callback_data="demo:status"),
             B(t("btn_botstats", lang), callback_data="demo:botstats")],
            [B(t("btn_screenshot", lang), callback_data="demo:photo"),
             B(t("btn_webcam", lang), callback_data="demo:photo")],
            [B(t("btn_docker", lang), callback_data="demo:docker"),
             B(t("btn_proc", lang), callback_data="demo:proc")],
            [B(t("btn_power", lang), callback_data="demo:action"),
             B(t("btn_sound", lang), callback_data="demo:action")],
            [B(t("btn_request", lang), callback_data="guest:request")],
            [B(t("btn_close_demo", lang), callback_data="guest:home")],
        ]
    )


def approval_menu(lang: str, user_id: int) -> M:
    return M(
        [
            [B(t("btn_approve", lang), callback_data=f"approve:{user_id}"),
             B(t("btn_deny", lang), callback_data=f"deny:{user_id}")],
        ]
    )


def admins_menu(lang: str, admin_list: list[dict]) -> M:
    rows = []
    for a in admin_list:
        if a.get("owner"):
            continue  # владельцев удалять нельзя
        label = a.get("name") or str(a["id"])
        rows.append([B(f"🗑 {label} ({a['id']})", callback_data=f"admin:rm:{a['id']}")])
    rows.append([_back(lang, "menu:more")])
    return M(rows)
