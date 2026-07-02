"""Локализация интерфейса: en (по умолчанию), ru, cs.

t(key, lang, **kwargs) — вернуть строку; при отсутствии перевода откат на en, затем на ключ.
Демо-строки (demo_*) тоже здесь."""

LANG_NAMES = {"en": "🇬🇧 English", "ru": "🇷🇺 Русский", "cs": "🇨🇿 Čeština"}

STR: dict[str, dict[str, str]] = {
    # ── общие меню / приветствия ─────────────────────────────────────────
    "welcome": {
        "en": "🎛 <b>PC control panel</b>\nPick an action with the buttons below.",
        "ru": "🎛 <b>Пульт управления ПК</b>\nВыбирай действие кнопками ниже.",
        "cs": "🎛 <b>Ovládací panel PC</b>\nVyber akci pomocí tlačítek níže.",
    },
    "guest_welcome": {
        "en": "👋 <b>Personal PC control bot.</b>\n\nYou don't have access yet. You can view the demo or request access from the owner.",
        "ru": "👋 <b>Бот управления личным ПК.</b>\n\nУ тебя пока нет доступа. Можешь посмотреть демо или запросить доступ у владельца.",
        "cs": "👋 <b>Bot pro ovládání osobního PC.</b>\n\nZatím nemáš přístup. Můžeš si prohlédnout demo nebo požádat majitele o přístup.",
    },
    "guest_home": {
        "en": "👋 <b>Personal PC control bot.</b>\n\nView the demo or request access.",
        "ru": "👋 <b>Бот управления личным ПК.</b>\n\nПосмотри демо или запроси доступ.",
        "cs": "👋 <b>Bot pro ovládání osobního PC.</b>\n\nZobraz demo nebo požádej o přístup.",
    },
    "no_access_text": {
        "en": "👋 No access. Check the demo or request access.",
        "ru": "👋 Нет доступа. Посмотри демо или запроси доступ.",
        "cs": "👋 Nemáš přístup. Zobraz demo nebo požádej o přístup.",
    },
    "title_power": {"en": "⚡ <b>Power</b>", "ru": "⚡ <b>Питание</b>", "cs": "⚡ <b>Napájení</b>"},
    "title_screen": {"en": "🔒 <b>Screen / Sleep</b>", "ru": "🔒 <b>Экран / Сон</b>", "cs": "🔒 <b>Obrazovka / Spánek</b>"},
    "title_sound": {"en": "🔊 <b>Sound / Media</b>", "ru": "🔊 <b>Звук / Медиа</b>", "cs": "🔊 <b>Zvuk / Média</b>"},
    "title_proc": {"en": "⚙️ <b>Processes</b>", "ru": "⚙️ <b>Процессы</b>", "cs": "⚙️ <b>Procesy</b>"},
    "title_more": {"en": "🛠 <b>More</b>", "ru": "🛠 <b>Дополнительно</b>", "cs": "🛠 <b>Více</b>"},
    "title_language": {"en": "🌐 <b>Choose language</b>", "ru": "🌐 <b>Выбор языка</b>", "cs": "🌐 <b>Volba jazyka</b>"},

    # ── кнопки главного меню ──────────────────────────────────────────────
    "btn_status": {"en": "🖥 PC status", "ru": "🖥 Статус ПК", "cs": "🖥 Stav PC"},
    "btn_botstats": {"en": "📊 Bot stats", "ru": "📊 Стата бота", "cs": "📊 Statistika bota"},
    "btn_screenshot": {"en": "📸 Screenshot", "ru": "📸 Скриншот", "cs": "📸 Snímek obrazovky"},
    "btn_webcam": {"en": "📷 Webcam", "ru": "📷 Вебка", "cs": "📷 Webkamera"},
    "btn_docker": {"en": "🐳 Docker", "ru": "🐳 Docker", "cs": "🐳 Docker"},
    "btn_proc": {"en": "⚙️ Processes", "ru": "⚙️ Процессы", "cs": "⚙️ Procesy"},
    "btn_sound": {"en": "🔊 Sound/Media", "ru": "🔊 Звук/Медиа", "cs": "🔊 Zvuk/Média"},
    "btn_screen": {"en": "🔒 Screen/Sleep", "ru": "🔒 Экран/Сон", "cs": "🔒 Obrazovka/Spánek"},
    "btn_power": {"en": "⚡ Power", "ru": "⚡ Питание", "cs": "⚡ Napájení"},
    "btn_more": {"en": "🛠 More", "ru": "🛠 Ещё", "cs": "🛠 Více"},
    "btn_back": {"en": "◀️ Back", "ru": "◀️ Назад", "cs": "◀️ Zpět"},

    # ── питание ───────────────────────────────────────────────────────────
    "btn_shutdown": {"en": "⏻ Shut down", "ru": "⏻ Выключить", "cs": "⏻ Vypnout"},
    "btn_reboot": {"en": "🔁 Reboot", "ru": "🔁 Перезагрузить", "cs": "🔁 Restartovat"},
    "btn_shutdown15": {"en": "⏳ Shut down in 15 min", "ru": "⏳ Выключить через 15 мин", "cs": "⏳ Vypnout za 15 min"},
    "btn_abort": {"en": "❌ Cancel shutdown", "ru": "❌ Отменить выключение", "cs": "❌ Zrušit vypnutí"},
    "btn_confirm_shutdown": {"en": "✅ Yes, shut down", "ru": "✅ Да, выключить", "cs": "✅ Ano, vypnout"},
    "btn_confirm_reboot": {"en": "✅ Yes, reboot", "ru": "✅ Да, перезагрузить", "cs": "✅ Ano, restartovat"},
    "btn_cancel": {"en": "◀️ Cancel", "ru": "◀️ Отмена", "cs": "◀️ Zrušit"},
    "q_shutdown": {"en": "⏻ Shut down the PC <b>now</b>?", "ru": "⏻ Выключить ПК <b>сейчас</b>?", "cs": "⏻ Vypnout PC <b>teď</b>?"},
    "q_reboot": {"en": "🔁 Reboot the PC <b>now</b>?", "ru": "🔁 Перезагрузить ПК <b>сейчас</b>?", "cs": "🔁 Restartovat PC <b>teď</b>?"},
    "shutdown15_ok": {
        "en": "⏳ Shutdown scheduled in 15 minutes.\nTap “Cancel shutdown” to cancel.",
        "ru": "⏳ Выключение через 15 минут запланировано.\nНажми «Отменить выключение», чтобы отменить.",
        "cs": "⏳ Vypnutí naplánováno za 15 minut.\nKlikni na „Zrušit vypnutí“ pro zrušení.",
    },
    "abort_ok": {"en": "❌ Shutdown canceled.", "ru": "❌ Выключение отменено.", "cs": "❌ Vypnutí zrušeno."},
    "abort_none": {"en": "ℹ️ Nothing to cancel.", "ru": "ℹ️ Отменять нечего.", "cs": "ℹ️ Není co rušit."},
    "shutting_down": {"en": "⏻ Shutting down…", "ru": "⏻ Выключаюсь…", "cs": "⏻ Vypínám…"},
    "rebooting": {"en": "🔁 Rebooting…", "ru": "🔁 Перезагружаюсь…", "cs": "🔁 Restartuji…"},

    # ── экран / сон ───────────────────────────────────────────────────────
    "btn_lock": {"en": "🔒 Lock", "ru": "🔒 Заблокировать", "cs": "🔒 Zamknout"},
    "btn_sleep": {"en": "😴 Sleep", "ru": "😴 Сон", "cs": "😴 Spánek"},
    "btn_monoff": {"en": "🌙 Monitors off", "ru": "🌙 Мониторы выкл", "cs": "🌙 Vypnout monitory"},
    "lock_ok": {"en": "🔒 Screen locked.", "ru": "🔒 Экран заблокирован.", "cs": "🔒 Obrazovka uzamčena."},
    "sleep_ok": {"en": "😴 Putting the PC to sleep…", "ru": "😴 Отправляю ПК в сон…", "cs": "😴 Uspávám PC…"},
    "monoff_ok": {"en": "🌙 Monitors turned off.", "ru": "🌙 Мониторы выключены.", "cs": "🌙 Monitory vypnuty."},

    # ── звук / медиа ──────────────────────────────────────────────────────
    "btn_mute": {"en": "🔇 Mute", "ru": "🔇 Mute", "cs": "🔇 Ztlumit"},
    "ans_louder": {"en": "🔊 Louder", "ru": "🔊 Громче", "cs": "🔊 Hlasitěji"},
    "ans_quieter": {"en": "🔉 Quieter", "ru": "🔉 Тише", "cs": "🔉 Tišeji"},
    "ans_mute": {"en": "🔇 Mute", "ru": "🔇 Mute", "cs": "🔇 Ztlumit"},
    "ans_play": {"en": "⏯ Play/Pause", "ru": "⏯ Play/Pause", "cs": "⏯ Přehrát/Pauza"},
    "ans_next": {"en": "⏭ Next", "ru": "⏭ Дальше", "cs": "⏭ Další"},
    "ans_prev": {"en": "⏮ Previous", "ru": "⏮ Назад", "cs": "⏮ Předchozí"},

    # ── процессы ──────────────────────────────────────────────────────────
    "btn_topcpu": {"en": "🔥 Top CPU", "ru": "🔥 Топ CPU", "cs": "🔥 Top CPU"},
    "btn_topram": {"en": "🧠 Top RAM", "ru": "🧠 Топ RAM", "cs": "🧠 Top RAM"},
    "top_cpu_head": {"en": "🔥 <b>Top processes by CPU</b>", "ru": "🔥 <b>Топ процессов по CPU</b>", "cs": "🔥 <b>Top procesy podle CPU</b>"},
    "top_ram_head": {"en": "🧠 <b>Top processes by RAM</b>", "ru": "🧠 <b>Топ процессов по RAM</b>", "cs": "🧠 <b>Top procesy podle RAM</b>"},

    # ── docker ────────────────────────────────────────────────────────────
    "btn_refresh": {"en": "🔄 Refresh", "ru": "🔄 Обновить", "cs": "🔄 Obnovit"},
    "logs_suffix": {"en": "logs", "ru": "логи", "cs": "logy"},
    "docker_head": {"en": "🐳 <b>Docker</b> — running {r}/{n}", "ru": "🐳 <b>Docker</b> — запущено {r}/{n}", "cs": "🐳 <b>Docker</b> — běží {r}/{n}"},
    "docker_not_running": {"en": "⚠️ Not running: ", "ru": "⚠️ Не запущены: ", "cs": "⚠️ Neběží: "},
    "docker_unavailable": {
        "en": "🐳 No containers found or docker is unavailable from WSL.",
        "ru": "🐳 Контейнеры не найдены или docker недоступен из WSL.",
        "cs": "🐳 Kontejnery nenalezeny nebo docker není z WSL dostupný.",
    },
    "logs_empty": {"en": "(logs are empty)", "ru": "(логи пусты)", "cs": "(logy jsou prázdné)"},
    "docker_logs_title": {"en": "📄 <b>{name}</b> (log tail):", "ru": "📄 <b>{name}</b> (хвост логов):", "cs": "📄 <b>{name}</b> (konec logů):"},
    "ans_docker": {"en": "Querying Docker…", "ru": "Опрашиваю Docker…", "cs": "Dotazuji se Dockeru…"},

    # ── captures ──────────────────────────────────────────────────────────
    "ans_screenshot": {"en": "Taking a screenshot…", "ru": "Делаю скриншот…", "cs": "Dělám snímek…"},
    "ans_webcam": {"en": "Taking a webcam photo…", "ru": "Снимаю с вебки…", "cs": "Fotím z webkamery…"},
    "cap_screenshot": {"en": "📸 Desktop screenshot", "ru": "📸 Скриншот рабочего стола", "cs": "📸 Snímek plochy"},
    "webcam_none": {
        "en": "📷 No camera found. Plug in a USB webcam and try again.",
        "ru": "📷 Камера не найдена. Подключи USB-вебку и попробуй снова.",
        "cs": "📷 Kamera nenalezena. Připoj USB webkameru a zkus to znovu.",
    },
    "cap_webcam": {
        "en": "📷 Webcam photo (saved to captures/webcam)",
        "ru": "📷 Фото с вебки (сохранено в captures/webcam)",
        "cs": "📷 Foto z webkamery (uloženo do captures/webcam)",
    },
    "autosnap_cap": {"en": "🕒 Auto-snapshot {time}", "ru": "🕒 Авто-снимок {time}", "cs": "🕒 Auto-snímek {time}"},

    # ── ещё / more ────────────────────────────────────────────────────────
    "btn_gallery": {"en": "🖼 Webcam gallery", "ru": "🖼 Галерея вебки", "cs": "🖼 Galerie webkamery"},
    "btn_tts": {"en": "🗣 Speak text", "ru": "🗣 Озвучить текст", "cs": "🗣 Přečíst text"},
    "btn_url": {"en": "🌐 Open URL/app", "ru": "🌐 Открыть URL/приложение", "cs": "🌐 Otevřít URL/aplikaci"},
    "btn_exec": {"en": "💻 Run command", "ru": "💻 Выполнить команду", "cs": "💻 Spustit příkaz"},
    "btn_auto_on": {"en": "🟢 Auto-snapshots: ON", "ru": "🟢 Автоснимки: ВКЛ", "cs": "🟢 Auto-snímky: ZAP"},
    "btn_auto_off": {"en": "⚪️ Auto-snapshots: OFF", "ru": "⚪️ Автоснимки: ВЫКЛ", "cs": "⚪️ Auto-snímky: VYP"},
    "btn_admins": {"en": "👥 Admins", "ru": "👥 Админы", "cs": "👥 Správci"},
    "btn_language": {"en": "🌐 Language", "ru": "🌐 Язык", "cs": "🌐 Jazyk"},
    "gallery_empty": {"en": "🖼 No webcam snapshots yet.", "ru": "🖼 Пока нет снимков с вебки.", "cs": "🖼 Zatím žádné snímky z webkamery."},
    "gallery_sending": {"en": "Sending the latest snapshots…", "ru": "Отправляю последние снимки…", "cs": "Posílám nejnovější snímky…"},
    "done": {"en": "Done.", "ru": "Готово.", "cs": "Hotovo."},
    "ask_tts": {
        "en": "🗣 Send text — I'll read it aloud on the PC speakers.",
        "ru": "🗣 Пришли текст — озвучу его на колонках ПК.",
        "cs": "🗣 Pošli text — přečtu ho nahlas z reproduktorů PC.",
    },
    "ask_url": {
        "en": "🌐 Send a URL or an app name to launch.",
        "ru": "🌐 Пришли URL или имя приложения для запуска.",
        "cs": "🌐 Pošli URL nebo název aplikace ke spuštění.",
    },
    "ask_exec": {
        "en": "💻 Send a PowerShell command to run on the PC.",
        "ru": "💻 Пришли PowerShell-команду для выполнения на ПК.",
        "cs": "💻 Pošli PowerShell příkaz ke spuštění na PC.",
    },
    "tts_done": {"en": "🗣 Spoken on the PC.", "ru": "🗣 Озвучено на ПК.", "cs": "🗣 Přehráno na PC."},
    "url_opening": {"en": "🌐 Opening: {text}", "ru": "🌐 Открываю: {text}", "cs": "🌐 Otevírám: {text}"},
    "auto_off_msg": {"en": "⚪️ Webcam auto-snapshots turned off.", "ru": "⚪️ Авто-снимки вебки выключены.", "cs": "⚪️ Auto-snímky webkamery vypnuty."},
    "auto_on_msg": {
        "en": "🟢 Webcam auto-snapshots turned on (every {n} min).",
        "ru": "🟢 Авто-снимки вебки включены (каждые {n} мин).",
        "cs": "🟢 Auto-snímky webkamery zapnuty (každých {n} min).",
    },

    # ── запись видео/аудио ────────────────────────────────────────────────
    "btn_record": {"en": "🎥 Record", "ru": "🎥 Запись", "cs": "🎥 Nahrávka"},
    "title_record": {"en": "🎥 <b>Record</b>\nChoose what to capture.", "ru": "🎥 <b>Запись</b>\nВыбери, что снять.", "cs": "🎥 <b>Nahrávka</b>\nVyber, co zachytit."},
    "btn_rec_video": {"en": "🎥 Video (cam+mic)", "ru": "🎥 Видео (вебка+микро)", "cs": "🎥 Video (kamera+mikro)"},
    "btn_rec_audio": {"en": "🎤 Audio (mic)", "ru": "🎤 Аудио (микро)", "cs": "🎤 Zvuk (mikrofon)"},
    "title_rec_vdur": {"en": "🎥 <b>Video</b> — choose length:", "ru": "🎥 <b>Видео</b> — выбери длительность:", "cs": "🎥 <b>Video</b> — vyber délku:"},
    "title_rec_adur": {"en": "🎤 <b>Audio</b> — choose length:", "ru": "🎤 <b>Аудио</b> — выбери длительность:", "cs": "🎤 <b>Zvuk</b> — vyber délku:"},
    "rec_working": {"en": "⏺ Recording {sec}s… please wait", "ru": "⏺ Записываю {sec} сек… подожди", "cs": "⏺ Nahrávám {sec}s… počkej"},
    "rec_video_cap": {"en": "🎥 {sec}s clip", "ru": "🎥 Клип {sec} сек", "cs": "🎥 Klip {sec}s"},
    "rec_audio_cap": {"en": "🎤 {sec}s audio", "ru": "🎤 Аудио {sec} сек", "cs": "🎤 Zvuk {sec}s"},
    "rec_no_mic": {
        "en": "🎤 No microphone found. Connect a mic and try again.",
        "ru": "🎤 Микрофон не найден. Подключи микрофон и попробуй снова.",
        "cs": "🎤 Mikrofon nenalezen. Připoj mikrofon a zkus to znovu.",
    },
    "rec_failed": {"en": "⚠️ Recording failed.", "ru": "⚠️ Не удалось записать.", "cs": "⚠️ Nahrávání selhalo."},
    "cam_label": {"en": "Camera", "ru": "Камера", "cs": "Kamera"},
    "title_camera": {"en": "📷 <b>Choose camera</b>\nThe active camera is used for photos and video.", "ru": "📷 <b>Выбор камеры</b>\nАктивная камера используется для фото и видео.", "cs": "📷 <b>Volba kamery</b>\nAktivní kamera se použije pro foto i video."},
    "cam_none": {"en": "📷 No cameras connected.", "ru": "📷 Камеры не подключены.", "cs": "📷 Nejsou připojeny žádné kamery."},
    "cam_selected": {"en": "✅ Camera: {name}", "ru": "✅ Камера: {name}", "cs": "✅ Kamera: {name}"},

    # ── старт / уведомления ───────────────────────────────────────────────
    "startup": {"en": "🟢 <b>PC booted, bot is online.</b>\n\n", "ru": "🟢 <b>ПК загружен, бот на связи.</b>\n\n", "cs": "🟢 <b>PC nastartoval, bot je online.</b>\n\n"},
    "language_set": {"en": "✅ Language set: {lang}", "ru": "✅ Язык установлен: {lang}", "cs": "✅ Jazyk nastaven: {lang}"},
    "unknown_cmd": {"en": "Unknown command", "ru": "Неизвестная команда", "cs": "Neznámý příkaz"},

    # ── доступ / безопасность ─────────────────────────────────────────────
    "no_access_alert": {
        "en": "⛔ No access. Request access from the owner or open the demo.",
        "ru": "⛔ Нет доступа. Запроси доступ у владельца или открой демо.",
        "cs": "⛔ Nemáš přístup. Požádej majitele o přístup nebo otevři demo.",
    },
    "owner_only_alert": {"en": "⛔ Owner only.", "ru": "⛔ Только для владельца.", "cs": "⛔ Pouze pro majitele."},
    "owner_only_short": {"en": "Owner only", "ru": "Только для владельца", "cs": "Pouze pro majitele"},

    # ── регистрация / админы ──────────────────────────────────────────────
    "btn_demo": {"en": "🎬 View demo", "ru": "🎬 Посмотреть демо", "cs": "🎬 Zobrazit demo"},
    "btn_request": {"en": "🔐 Request access", "ru": "🔐 Запросить доступ", "cs": "🔐 Požádat o přístup"},
    "btn_close_demo": {"en": "◀️ Close demo", "ru": "◀️ Закрыть демо", "cs": "◀️ Zavřít demo"},
    "btn_approve": {"en": "✅ Approve", "ru": "✅ Одобрить", "cs": "✅ Schválit"},
    "btn_deny": {"en": "🚫 Deny", "ru": "🚫 Отклонить", "cs": "🚫 Zamítnout"},
    "already_access": {"en": "You already have access. Tap /start", "ru": "У тебя уже есть доступ. Нажми /start", "cs": "Přístup už máš. Klikni /start"},
    "req_title": {
        "en": "🔐 <b>Access request</b>\nName: <b>{name}</b>\nUsername: {uname}\nID: <code>{id}</code>",
        "ru": "🔐 <b>Запрос доступа</b>\nИмя: <b>{name}</b>\nUsername: {uname}\nID: <code>{id}</code>",
        "cs": "🔐 <b>Žádost o přístup</b>\nJméno: <b>{name}</b>\nUsername: {uname}\nID: <code>{id}</code>",
    },
    "req_sent": {
        "en": "📨 Request sent to the owner. Wait for approval — you'll get a notification.",
        "ru": "📨 Запрос отправлен владельцу. Дождись подтверждения — придёт уведомление.",
        "cs": "📨 Žádost odeslána majiteli. Počkej na schválení — přijde oznámení.",
    },
    "req_failed": {
        "en": "⚠️ Couldn't reach the owner. Try again later.",
        "ru": "⚠️ Не удалось связаться с владельцем. Попробуй позже.",
        "cs": "⚠️ Nepodařilo se spojit s majitelem. Zkus to později.",
    },
    "approved_owner": {"en": "✅ Access granted: <b>{name}</b> (<code>{id}</code>)", "ru": "✅ Доступ выдан: <b>{name}</b> (<code>{id}</code>)", "cs": "✅ Přístup udělen: <b>{name}</b> (<code>{id}</code>)"},
    "approved_user": {
        "en": "✅ Access approved! You can now control the PC.",
        "ru": "✅ Доступ одобрен! Теперь ты можешь управлять ПК.",
        "cs": "✅ Přístup schválen! Teď můžeš ovládat PC.",
    },
    "denied_owner": {"en": "🚫 Request denied: <code>{id}</code>", "ru": "🚫 Запрос отклонён: <code>{id}</code>", "cs": "🚫 Žádost zamítnuta: <code>{id}</code>"},
    "denied_user": {"en": "🚫 Access denied.", "ru": "🚫 В доступе отказано.", "cs": "🚫 Přístup zamítnut."},
    "admins_head": {"en": "👥 <b>Admins</b>", "ru": "👥 <b>Админы</b>", "cs": "👥 <b>Správci</b>"},
    "admins_owner_tag": {"en": "👑 owner", "ru": "👑 владелец", "cs": "👑 majitel"},
    "admins_admin_tag": {"en": "🔑 admin", "ru": "🔑 админ", "cs": "🔑 správce"},
    "admins_hint": {
        "en": "\nOwners cannot be removed. Tap 🗑 to remove a regular admin.",
        "ru": "\nВладельцев удалять нельзя. Нажми 🗑, чтобы убрать обычного админа.",
        "cs": "\nMajitele nelze odebrat. Klikni 🗑 pro odebrání běžného správce.",
    },

    # ── системная статистика (sysinfo) ────────────────────────────────────
    "sys_cpu": {"en": "⚙️ CPU: <b>{cpu}%</b> · {cores} cores", "ru": "⚙️ CPU: <b>{cpu}%</b> · {cores} ядер", "cs": "⚙️ CPU: <b>{cpu}%</b> · {cores} jader"},
    "sys_ram": {"en": "🧠 RAM: <b>{p}%</b> — {used} / {total}", "ru": "🧠 RAM: <b>{p}%</b> — {used} / {total}", "cs": "🧠 RAM: <b>{p}%</b> — {used} / {total}"},
    "sys_disk": {"en": "💽 {dev} <b>{p}%</b> — {used} / {total}", "ru": "💽 {dev} <b>{p}%</b> — {used} / {total}", "cs": "💽 {dev} <b>{p}%</b> — {used} / {total}"},
    "sys_uptime": {"en": "⏱ Uptime: <b>{up}</b>", "ru": "⏱ Аптайм: <b>{up}</b>", "cs": "⏱ Doba běhu: <b>{up}</b>"},

    # ── статистика бота (stats) ───────────────────────────────────────────
    "stats_head": {"en": "📊 <b>Bot statistics</b>", "ru": "📊 <b>Статистика бота</b>", "cs": "📊 <b>Statistika bota</b>"},
    "stats_uptime": {"en": "⏱ Bot uptime: <b>{u}</b>", "ru": "⏱ Бот работает: <b>{u}</b>", "cs": "⏱ Bot běží: <b>{u}</b>"},
    "stats_total": {"en": "🔢 Total actions: <b>{n}</b>", "ru": "🔢 Всего действий: <b>{n}</b>", "cs": "🔢 Celkem akcí: <b>{n}</b>"},
    "stats_by_type": {"en": "<b>By type:</b>", "ru": "<b>По типам:</b>", "cs": "<b>Podle typu:</b>"},
    "stats_empty": {"en": "• empty so far", "ru": "• пока пусто", "cs": "• zatím prázdné"},
    "stats_recent": {"en": "<b>Recent actions:</b>", "ru": "<b>Последние действия:</b>", "cs": "<b>Poslední akce:</b>"},

    # ── демо (по умолчанию en) ────────────────────────────────────────────
    "demo_tag": {
        "en": "🎬 <b>DEMO</b> — data is fictional, no real control.\n\n",
        "ru": "🎬 <b>ДЕМО</b> — данные вымышленные, реального управления нет.\n\n",
        "cs": "🎬 <b>DEMO</b> — data jsou smyšlená, žádné skutečné ovládání.\n\n",
    },
    "demo_intro": {
        "en": ("🎬 <b>PC control panel demo</b>\n\n"
               "This is how the bot works. The real buttons can:\n"
               "• 🖥 PC status, 📊 statistics\n"
               "• 📸 screenshot, 📷 webcam photo\n"
               "• 🐳 Docker container status and logs\n"
               "• ⚙️ top processes\n"
               "• 🔊 sound/media, 🔒 lock/sleep/monitors\n"
               "• ⚡ shutdown/reboot (with confirmation)\n\n"
               "Tap the buttons below — all on demo data."),
        "ru": ("🎬 <b>Демо пульта управления ПК</b>\n\n"
               "Так выглядит бот в работе. Реальные кнопки умеют:\n"
               "• 🖥 статус ПК, 📊 статистика\n"
               "• 📸 скриншот, 📷 фото с вебки\n"
               "• 🐳 статус Docker-контейнеров и их логи\n"
               "• ⚙️ топ процессов\n"
               "• 🔊 звук/медиа, 🔒 блокировка/сон/мониторы\n"
               "• ⚡ выключение/перезагрузка (с подтверждением)\n\n"
               "Потыкай кнопки ниже — всё на демо-данных."),
        "cs": ("🎬 <b>Demo ovládacího panelu PC</b>\n\n"
               "Takto bot funguje. Skutečná tlačítka umí:\n"
               "• 🖥 stav PC, 📊 statistika\n"
               "• 📸 snímek obrazovky, 📷 foto z webkamery\n"
               "• 🐳 stav Docker kontejnerů a jejich logy\n"
               "• ⚙️ top procesy\n"
               "• 🔊 zvuk/média, 🔒 zámek/spánek/monitory\n"
               "• ⚡ vypnutí/restart (s potvrzením)\n\n"
               "Zkus tlačítka níže — vše na demo datech."),
    },
    "demo_status": {
        "en": ("🖥 <b>HOME-PC</b>\n⚙️ CPU: <b>17%</b> · 8 cores\n"
               "🧠 RAM: <b>42%</b> — 6.7 GB / 16.0 GB\n"
               "💽 C:\\ <b>63%</b> — 297 GB / 465 GB\n⏱ Uptime: <b>2 days, 4:11:37</b>"),
        "ru": ("🖥 <b>HOME-PC</b>\n⚙️ CPU: <b>17%</b> · 8 ядер\n"
               "🧠 RAM: <b>42%</b> — 6.7 ГБ / 16.0 ГБ\n"
               "💽 C:\\ <b>63%</b> — 297 ГБ / 465 ГБ\n⏱ Аптайм: <b>2 days, 4:11:37</b>"),
        "cs": ("🖥 <b>HOME-PC</b>\n⚙️ CPU: <b>17%</b> · 8 jader\n"
               "🧠 RAM: <b>42%</b> — 6.7 GB / 16.0 GB\n"
               "💽 C:\\ <b>63%</b> — 297 GB / 465 GB\n⏱ Doba běhu: <b>2 days, 4:11:37</b>"),
    },
    "demo_docker": {
        "en": ("🐳 <b>Docker</b> — running 4/5\n\n"
               "✅ <b>finance-bot</b>\n    <i>Up 2 hours</i>\n"
               "✅ <b>site</b>\n    <i>Up 2 hours</i>\n"
               "✅ <b>ollama</b>\n    <i>Up 2 hours</i>\n"
               "✅ <b>caddy</b>\n    <i>Up 2 hours</i>\n"
               "⛔ <b>backup-job</b>\n    <i>Exited (0) 5 minutes ago</i>\n\n"
               "⚠️ Not running: backup-job"),
        "ru": ("🐳 <b>Docker</b> — запущено 4/5\n\n"
               "✅ <b>finance-bot</b>\n    <i>Up 2 hours</i>\n"
               "✅ <b>site</b>\n    <i>Up 2 hours</i>\n"
               "✅ <b>ollama</b>\n    <i>Up 2 hours</i>\n"
               "✅ <b>caddy</b>\n    <i>Up 2 hours</i>\n"
               "⛔ <b>backup-job</b>\n    <i>Exited (0) 5 minutes ago</i>\n\n"
               "⚠️ Не запущены: backup-job"),
        "cs": ("🐳 <b>Docker</b> — běží 4/5\n\n"
               "✅ <b>finance-bot</b>\n    <i>Up 2 hours</i>\n"
               "✅ <b>site</b>\n    <i>Up 2 hours</i>\n"
               "✅ <b>ollama</b>\n    <i>Up 2 hours</i>\n"
               "✅ <b>caddy</b>\n    <i>Up 2 hours</i>\n"
               "⛔ <b>backup-job</b>\n    <i>Exited (0) 5 minutes ago</i>\n\n"
               "⚠️ Neběží: backup-job"),
    },
    "demo_proc": {
        "en": ("🔥 <b>Top processes by CPU</b>\n"
               "• chrome.exe (pid 4821) — 14%\n• python.exe (pid 1337) — 6%\n"
               "• Code.exe (pid 9002) — 4%\n• dwm.exe (pid 1120) — 2%\n• explorer.exe (pid 764) — 1%"),
        "ru": ("🔥 <b>Топ процессов по CPU</b>\n"
               "• chrome.exe (pid 4821) — 14%\n• python.exe (pid 1337) — 6%\n"
               "• Code.exe (pid 9002) — 4%\n• dwm.exe (pid 1120) — 2%\n• explorer.exe (pid 764) — 1%"),
        "cs": ("🔥 <b>Top procesy podle CPU</b>\n"
               "• chrome.exe (pid 4821) — 14%\n• python.exe (pid 1337) — 6%\n"
               "• Code.exe (pid 9002) — 4%\n• dwm.exe (pid 1120) — 2%\n• explorer.exe (pid 764) — 1%"),
    },
    "demo_botstats": {
        "en": ("📊 <b>Bot statistics</b>\n⏱ Bot uptime: <b>1 day, 3:22:10</b>\n"
               "🔢 Total actions: <b>128</b>\n\n<b>By type:</b>\n"
               "• status: 34\n• screenshot: 22\n• webcam: 18\n• docker: 15\n• shutdown: 3"),
        "ru": ("📊 <b>Статистика бота</b>\n⏱ Бот работает: <b>1 day, 3:22:10</b>\n"
               "🔢 Всего действий: <b>128</b>\n\n<b>По типам:</b>\n"
               "• status: 34\n• screenshot: 22\n• webcam: 18\n• docker: 15\n• shutdown: 3"),
        "cs": ("📊 <b>Statistika bota</b>\n⏱ Bot běží: <b>1 day, 3:22:10</b>\n"
               "🔢 Celkem akcí: <b>128</b>\n\n<b>Podle typu:</b>\n"
               "• status: 34\n• screenshot: 22\n• webcam: 18\n• docker: 15\n• shutdown: 3"),
    },
    "demo_photo": {
        "en": "📸 A real photo (screenshot/webcam) would arrive here.\nNot taken in demo.",
        "ru": "📸 Здесь пришло бы реальное фото (скриншот/вебка).\nВ демо оно не делается.",
        "cs": "📸 Zde by přišla skutečná fotka (snímek/webkamera).\nV demu se nepořizuje.",
    },
    "demo_action": {
        "en": "A real action on the PC would run here. Disabled in demo.",
        "ru": "Здесь выполнилось бы реальное действие на ПК. В демо оно отключено.",
        "cs": "Zde by proběhla skutečná akce na PC. V demu je vypnutá.",
    },
}


def t(key: str, lang: str = "en", **kwargs) -> str:
    entry = STR.get(key)
    if not entry:
        return key
    s = entry.get(lang) or entry.get("en") or key
    if kwargs:
        try:
            s = s.format(**kwargs)
        except Exception:  # noqa: BLE001
            pass
    return s
