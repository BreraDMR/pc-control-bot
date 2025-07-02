# 🎛 PC Control Bot

A Telegram bot for remotely controlling a personal Windows PC — **everything via buttons**,
no typed commands. It can shut down / reboot the machine, take a desktop screenshot and a
webcam photo, show the status of Docker containers (running in WSL2), list top processes,
control sound and media, lock the screen, and much more.

> Built for a headless under-the-desk PC reachable over Tailscale/SSH: phone in hand —
> and you fully control the machine.

## ✨ Features

| Section | What it does |
|---|---|
| 🖥 **PC status** | CPU, RAM, disks, uptime |
| 📊 **Bot stats** | how many times each action was used, bot uptime, action log |
| 📸 **Screenshot** | snapshot of all monitors, saved to `captures/screenshots` |
| 📷 **Webcam** | frame from a USB camera into `captures/webcam`; scheduled auto-snapshots |
| 🎥 **Record** | short webcam video (+mic) and mic-only audio clips sent to Telegram; pick the length (5–60 s) and, if several cameras are connected, the source camera |
| 🐳 **Docker** | container list (✅/⛔/⚠️) + tail of any container's logs |
| ⚙️ **Processes** | top by CPU and by RAM |
| 🔊 **Sound/Media** | volume ±, mute, play/pause, next/previous |
| 🔒 **Screen/Sleep** | lock, sleep, turn monitors off |
| ⚡ **Power** | shutdown/reboot (with confirmation), shutdown in 15 min + cancel |
| 🌐 **Language** | switch UI language on the fly (English / Russian / Czech) |
| 🛠 **More** | webcam gallery, text-to-speech, launch URL/app, arbitrary PowerShell command |

## 🔐 Access & Security

Only the owner can control the PC — the access model is layered:

- **Owners** (`OWNER_IDS` in `.env`) — hard-wired admins with full access, including granting
  and revoking rights. They cannot be removed from the bot.
- **Admins** — registered on request: a guest taps "🔐 Request access", an owner approves with
  a button. Stored in `data/admins.json`.
- **Guest** — any other user sees only a welcome screen with **🎬 Demo** (shows the interface
  on fake data, with no real control) and **🔐 Request access**.

Additionally:
- The token and owner list live in `.env`, which is **never committed** (see `.gitignore`).
- Dangerous actions (shutdown/reboot) require a "Yes" confirmation.
- The bot only does outbound polling — no open inbound ports.
- All access denials are logged.

## 🌐 Localization

The interface is available in **English (default)**, **Russian** and **Czech**, switchable
right in the bot (🌐 Language). The choice is per-user and persisted in `data/prefs.json`.
Demo mode is shown in English by default. Strings live in `i18n.py`.

## 🧩 Architecture

The bot runs **natively on Windows** (it needs access to the GUI session for screenshots,
the camera and power control). The Docker containers, meanwhile, live in **WSL2**, so their
status is queried via `wsl.exe docker ...`.

```
Telegram  ──polling──>  bot.py (Windows, Python)
                          ├─ power.py      shutdown / reboot / lock / sleep / monitors
                          ├─ capture.py    mss (screenshot) + ffmpeg/dshow (webcam)
                          ├─ record.py     ffmpeg/dshow short video (H.264) + mic audio (Opus)
                          ├─ sysinfo.py    psutil (CPU/RAM/disks/processes)
                          ├─ dockerinfo.py wsl.exe docker ...  ──>  WSL2 Ubuntu
                          ├─ media.py      volume/media/TTS/commands
                          ├─ admins.py     owners + admin registration
                          ├─ demo.py       demo mode on fake data
                          └─ i18n.py/prefs.py  en/ru/cs strings + per-user language
```

Dependencies are minimal and compatible with Python 3.14: `python-telegram-bot`, `mss`,
`Pillow`, `psutil`, `imageio-ffmpeg` (webcam via ffmpeg — no heavyweight opencv).

## 🚀 Setup (Windows)

```powershell
git clone https://github.com/BreraDMR/pc-control-bot.git
cd pc-control-bot
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt

copy .env.example .env
notepad .env          # fill in BOT_TOKEN and OWNER_IDS

.venv\Scripts\python test_capabilities.py   # self-check
.venv\Scripts\python bot.py                 # run
```

You can find your own Telegram ID via [@userinfobot](https://t.me/userinfobot).

### Autostart at logon

Screenshots and the webcam require an interactive session, so the bot starts **at user
logon** via Task Scheduler:

```powershell
schtasks /Create /TN "PC Control Bot" /SC ONLOGON ^
  /TR "\"%CD%\.venv\Scripts\pythonw.exe\" \"%CD%\bot.py\"" /RL LIMITED /F
```

## ⚙️ `.env` settings

| Variable | Purpose |
|---|---|
| `BOT_TOKEN` | token from @BotFather |
| `OWNER_IDS` | owner IDs, comma-separated |
| `WSL_DISTRO` | WSL distro with docker (empty = default) |
| `AUTO_SNAP_MINUTES` | webcam auto-snapshot interval (default 30) |

## 📄 License

MIT.
