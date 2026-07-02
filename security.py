"""Контроль доступа.

restricted  — действие доступно любому админу (владелец или подтверждённый).
owner_only  — действие доступно только владельцам (управление админами, аппрув)."""
import functools
import logging

from telegram import Update
from telegram.ext import ContextTypes

import admins
import stats

log = logging.getLogger(__name__)


def _deny_meta(update: Update) -> str:
    u = update.effective_user
    return f"{getattr(u, 'id', None)}/{getattr(u, 'username', None)}"


def restricted(func):
    """Пропускает только админов (владельцы + подтверждённые)."""

    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        uid = update.effective_user.id if update.effective_user else None
        if not admins.is_admin(uid):
            log.warning("ОТКАЗ (не админ): %s", _deny_meta(update))
            stats.bump("denied", meta=str(uid))
            await _reject(update, "⛔ Нет доступа. Запроси доступ у владельца или открой демо.")
            return
        return await func(update, context, *args, **kwargs)

    return wrapper


def owner_only(func):
    """Пропускает только владельцев (OWNER_IDS)."""

    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        uid = update.effective_user.id if update.effective_user else None
        if not admins.is_owner(uid):
            log.warning("ОТКАЗ (не владелец): %s", _deny_meta(update))
            stats.bump("denied_owner", meta=str(uid))
            await _reject(update, "⛔ Только для владельца.")
            return
        return await func(update, context, *args, **kwargs)

    return wrapper


async def _reject(update: Update, message: str) -> None:
    try:
        if update.callback_query:
            await update.callback_query.answer(message, show_alert=True)
        elif update.message:
            await update.message.reply_text(message)
    except Exception:  # noqa: BLE001
        pass
