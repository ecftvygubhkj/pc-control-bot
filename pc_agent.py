"""
pc_agent.py — запускається на ПК користувача

Встанови бібліотеки:
  pip install aiogram psutil pycaw comtypes Pillow pyautogui requests

Запуск:
  python pc_agent.py
"""

import platform
import socket
import time
import os
import sys
import json
import ctypes
import psutil
import io
import requests

CONFIG_FILE = "config.json"
PC_NAME = socket.gethostname()

# ─── Конфіг ──────────────────────────────────────────────────────────────────

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def setup():
    config = load_config()

    if not config.get("token"):
        print("=" * 50)
        print("  Перший запуск! Налаштування.")
        print("=" * 50)
        token = input("\nВведи токен бота: ").strip()
        if not token:
            print("Токен не введено!")
            sys.exit(1)
        config["token"] = token
        save_config(config)
        print("✅ Токен збережено!\n")

    if not config.get("telegram_id"):
        print("\nЩоб дізнатись свій Telegram ID:")
        print("  Напиши @userinfobot в Telegram команду /start")
        print("  Скопіюй число 'Id: XXXXXXXXXX'\n")
        tid = input("Введи свій Telegram ID: ").strip()
        if not tid.isdigit():
            print("Невірний ID!")
            sys.exit(1)
        config["telegram_id"] = tid
        save_config(config)
        print("✅ ID збережено!\n")

    return config["token"], config["telegram_id"]

# ─── Telegram API (без aiogram, просто requests) ─────────────────────────────

def tg_send(token, chat_id, text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10
        )
    except Exception as e:
        print(f"Помилка надсилання: {e}")

def tg_send_photo(token, chat_id, photo_bytes, caption=""):
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendPhoto",
            data={"chat_id": chat_id, "caption": caption},
            files={"photo": ("screenshot.jpg", photo_bytes, "image/jpeg")},
            timeout=15
        )
    except Exception as e:
        print(f"Помилка надсилання фото: {e}")

def tg_get_updates(token, offset=None):
    try:
        params = {"timeout": 20, "allowed_updates": ["message"]}
        if offset:
            params["offset"] = offset
        r = requests.get(
            f"https://api.telegram.org/bot{token}/getUpdates",
            params=params,
            timeout=25
        )
        return r.json()
    except Exception:
        return {"ok": False, "result": []}

def tg_delete_webhook(token):
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/deleteWebhook",
            json={"drop_pending_updates": False},
            timeout=10
        )
    except Exception:
        pass

# ─── Системні функції ─────────────────────────────────────────────────────────

def get_stats() -> str:
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net = psutil.net_io_counters()
    uptime_sec = int(time.time() - psutil.boot_time())
    h, rem = divmod(uptime_sec, 3600)
    m = rem // 60

    temp_str = ""
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                if entries:
                    temp_str = f"\n🌡 Темп: {entries[0].current:.0f}C"
                    break
    except Exception:
        pass

    bat_str = ""
    try:
        bat = psutil.sensors_battery()
        if bat:
            plug = "🔌" if bat.power_plugged else "🔋"
            bat_str = f"\n{plug} Батарея: {bat.percent:.0f}%"
    except Exception:
        pass

    return (
        f"💻 Статистика ПК: {PC_NAME}\n\n"
        f"🔲 CPU: {cpu}%\n"
        f"🧠 RAM: {mem.used/1e9:.1f} / {mem.total/1e9:.1f} GB ({mem.percent}%)\n"
        f"💾 Диск: {disk.used/1e9:.1f} / {disk.total/1e9:.1f} GB ({disk.percent}%)\n"
        f"🌐 ↓ {net.bytes_recv/1e6:.1f} MB ↑ {net.bytes_sent/1e6:.1f} MB"
        f"{temp_str}{bat_str}\n"
        f"⚡ Аптайм: {h}г {m}хв"
    )

def get_volume() -> int:
    if platform.system() != "Windows":
        return -1
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        return int(volume.GetMasterVolumeLevelScalar() * 100)
    except Exception:
        return -1

def set_volume(level: int):
    if platform.system() != "Windows":
        return
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(max(0, min(100, level)) / 100, None)
    except Exception:
        pass

def toggle_mute():
    if platform.system() != "Windows":
        return
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(not volume.GetMute(), None)
    except Exception:
        pass

def media_key(vk_code):
    if platform.system() != "Windows":
        return
    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP = 0x0002
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)

def toggle_mic() -> str:
    if platform.system() != "Windows":
        return "Не підтримується"
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        mic = AudioUtilities.GetMicrophone()
        if not mic:
            return "Мікрофон не знайдено"
        interface = mic.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        muted = volume.GetMute()
        volume.SetMute(not muted, None)
        return "Мікрофон вимкнено 🔇" if not muted else "Мікрофон увімкнено 🎤"
    except Exception as e:
        return f"Помилка: {e}"

def take_screenshot() -> bytes:
    try:
        import pyautogui
        img = pyautogui.screenshot()
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=60)
        return buf.getvalue()
    except Exception:
        return None

def lock_screen():
    if platform.system() == "Windows":
        ctypes.windll.user32.LockWorkStation()

def sleep_pc():
    if platform.system() == "Windows":
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def shutdown_pc():
    if platform.system() == "Windows":
        os.system("shutdown /s /t 3")

def reboot_pc():
    if platform.system() == "Windows":
        os.system("shutdown /r /t 3")

# ─── Обробка команд ──────────────────────────────────────────────────────────

def handle_command(token, chat_id, action):
    action = action.strip()
    print(f"  Команда: {action}")

    if action == "stats":
        tg_send(token, chat_id, get_stats())

    elif action == "get_volume":
        tg_send(token, chat_id, f"VOLUME:{get_volume()}")

    elif action == "vol_up":
        vol = get_volume()
        set_volume(vol + 10)
        tg_send(token, chat_id, f"VOLUME:{min(vol+10, 100)}")

    elif action == "vol_down":
        vol = get_volume()
        set_volume(vol - 10)
        tg_send(token, chat_id, f"VOLUME:{max(vol-10, 0)}")

    elif action == "vol_mute":
        toggle_mute()
        tg_send(token, chat_id, f"VOLUME:{get_volume()}")

    elif action == "music_playpause":
        media_key(0xB3)

    elif action == "music_next":
        media_key(0xB0)

    elif action == "music_prev":
        media_key(0xB1)

    elif action == "mic_toggle":
        tg_send(token, chat_id, toggle_mic())

    elif action == "screenshot":
        img = take_screenshot()
        if img:
            tg_send_photo(token, chat_id, img, f"📸 {PC_NAME}")

    elif action == "lock":
        lock_screen()

    elif action == "sleep":
        sleep_pc()

    elif action == "shutdown":
        tg_send(token, chat_id, "🔴 ПК вимикається...")
        time.sleep(1)
        shutdown_pc()

    elif action == "reboot":
        tg_send(token, chat_id, "🔄 ПК перезавантажується...")
        time.sleep(1)
        reboot_pc()

# ─── Головний цикл ───────────────────────────────────────────────────────────

def main():
    token, telegram_id = setup()
    chat_id = int(telegram_id)

    print("=" * 50)
    print("  PC Agent — Telegram PC Control")
    print("=" * 50)

    code = input("\n🔑 Введи код підключення з бота: ").strip().upper()
    if not code:
        print("Код не введено!")
        return

    print("\n📡 Підключення до бота...")

    # Видаляємо webhook щоб не було конфліктів
    tg_delete_webhook(token)

    # Надсилаємо запит на підключення
    tg_send(token, chat_id, f"/agent_connect {code} {PC_NAME}")
    print("⏳ Очікую підтвердження...")

    # Чекаємо відповідь від бота (максимум 20 секунд)
    offset = None
    start = time.time()
    connected = False

    while time.time() - start < 20:
        updates = tg_get_updates(token, offset)
        if not updates.get("ok"):
            time.sleep(1)
            continue

        for upd in updates.get("result", []):
            offset = upd["update_id"] + 1
            msg = upd.get("message", {})
            text = msg.get("text", "")
            from_id = msg.get("from", {}).get("id", 0)

            # Бот надіслав підтвердження
            if text == "/agent_ok" and from_id != chat_id:
                connected = True
                break

        if connected:
            break
        time.sleep(1)

    if not connected:
        print("❌ Таймаут! Перевір:")
        print("  • Код правильний?")
        print("  • Бот запущений?")
        return

    print(f"\n✅ Підключено!")
    print(f"💻 ПК: {PC_NAME}")
    print("\n🟢 Агент працює. Не закривай це вікно!")
    print("   Telegram → бот → 🖥 Комп'ютер → керуй ПК")
    print("\nCtrl+C для зупинки\n")

    # Головний цикл — слухаємо команди
    last_ping = time.time()

    while True:
        try:
            # Пінг кожні 15 секунд
            if time.time() - last_ping > 15:
                tg_send(token, chat_id, "/agent_ping")
                last_ping = time.time()

            updates = tg_get_updates(token, offset)
            if not updates.get("ok"):
                time.sleep(2)
                continue

            for upd in updates.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                text = msg.get("text", "")
                from_id = msg.get("from", {}).get("id", 0)

                # Команди тільки від бота (не від себе)
                if text.startswith("/cmd ") and from_id != chat_id:
                    action = text[5:]
                    handle_command(token, chat_id, action)

        except KeyboardInterrupt:
            print("\n\n👋 Агент зупинено.")
            break
        except Exception as e:
            print(f"Помилка: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
