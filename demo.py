"""Демо-режим: показывает, как выглядит бот, на выдуманных данных (по умолчанию en).

Реальных действий с ПК нет — только заготовленные тексты из i18n."""
from i18n import t

_KEYS = {
    "intro": "demo_intro",
    "status": "demo_status",
    "docker": "demo_docker",
    "proc": "demo_proc",
    "botstats": "demo_botstats",
    "photo": "demo_photo",
    "action": "demo_action",
}


def response(key: str, lang: str = "en") -> str:
    tag = t("demo_tag", lang)
    body = t(_KEYS.get(key, "demo_intro"), lang)
    # intro без «плашки», остальные экраны — с плашкой ДЕМО
    return body if key == "intro" else tag + body
