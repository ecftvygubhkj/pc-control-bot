"""
pc_agent.py — запускається на ПК користувача

Встанови бібліотеки:
  pip install aiogram psutil pycaw comtypes Pillow pyautogui

Запуск:
  python pc_agent.py
"""

import asyncio
import platform
import socket
import time
import os
import sys
import json
import ctypes
import psutil
import io
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command

CONFIG_FILE = "config.json"
BOT_TOKEN = "ВАШ_ТОКЕН_БОТА"  # вшитий токен — люди не змінюють

PC_NAME = socket.gethostname()
USER_ID = None
CONNECTED = False
PING_INTERVAL = 15

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

def get_telegram_id():
    config = load_config()
    if config.get("telegram_id"):
        return int(config["telegram_id"])

    print("\n" + "=" * 50)
    print("  Перший запуск! Налаштування агента.")
    print("=" * 50)
    print("\n Щоб дізнатись свій Telegram ID:")
    print("  1. Відкрий Telegram")
    print("  2. Напиши боту @userinfobot команду /start")
    print("  3. Скопіюй число 'Id: XXXXXXXXXX'\n")
    tid = input("Введи свій Telegram ID: ").strip()
    if not tid.isdigit():
        print("Невірний ID!")
        sys.exit(1)
    config["telegram_id"] = tid
    save_config(config)
    print(f"ID збережено: {tid}\n")
    return int(tid)

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
                    temp_str = f"\n🌡 Темп: <b>{entries[0].current:.0f}°C</b>"
                    break
    except Exception:
        pass

    bat_str = ""
    try:
        bat = psutil.sensors_battery()
        if bat:
            plug = "🔌" if bat.power_plugged else "🔋"
            bat_str = f"\n{plug} Батарея: <b>{bat.percent:.0f}%</b>"
    except Exception:
        pass

    return (
        f"💻 <b>Статистика ПК: {PC_NAME}</b>\n\n"
        f"🔲 CPU: <b>{cpu}%</b>\n"
        f"🧠 RAM: <b>{mem.used/1e9:.1f} / {mem.total/1e9:.1f} GB</b> ({mem.percent}%)\n"
        f"💾 Диск: <b>{disk.used/1e9:.1f} / {disk.total/1e9:.1f} GB</b> ({disk.percent}%)\n"
        f"🌐 ↓ <b>{net.bytes_recv/1e6:.1f} MB</b> ↑ <b>{net.bytes_sent/1e6:.1f} MB</b>"
        f"{temp_str}{bat_str}\n"
        f"⚡ Аптайм: <b>{h}г {m}хв</b>"
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
    else:
        os.system("shutdown -h now")

def reboot_pc():
    if platform.system() == "Windows":
        os.system("shutdown /r /t 3")
    else:
        os.system("reboot")

# ─── Бот і диспетчер ─────────────────────────────────────────────────────────

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("cmd"))
async def handle_cmd(message: Message):
    global CONNECTED, USER_ID
    if not CONNECTED:
        return
    if message.chat.id != USER_ID:
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        return

    action = parts[1]
    data = parts[2] if len(parts) > 2 else ""

    async def reply(text):
        await message.answer(f"/agent_response {text}")

    if action == "stats":
        await reply(get_stats())

    elif action == "get_volume":
        await reply(str(get_volume()))

    elif action == "vol_up":
        vol = get_volume()
        set_volume(vol + 10)
        await reply(str(min(vol + 10, 100)))

    elif action == "vol_down":
        vol = get_volume()
        set_volume(vol - 10)
        await reply(str(max(vol - 10, 0)))

    elif action == "vol_mute":
        toggle_mute()
        await reply(str(get_volume()))

    elif action == "music_playpause":
        media_key(0xB3)
        await reply("ok")

    elif action == "music_next":
        media_key(0xB0)
        await reply("ok")

    elif action == "music_prev":
        media_key(0xB1)
        await reply("ok")

    elif action == "mic_toggle":
        await reply(toggle_mic())

    elif action == "screenshot":
        img_data = take_screenshot()
        if img_data:
            await bot.send_photo(
                chat_id=USER_ID,
                photo=BufferedInputFile(img_data, filename="screenshot.jpg"),
                caption=f"📸 {PC_NAME}"
            )
        await reply("ok")

    elif action == "lock":
        lock_screen()
        await reply("ok")

    elif action == "sleep":
        await reply("ok")
        await asyncio.sleep(1)
        sleep_pc()

    elif action == "shutdown":
        await reply("ok")
        await asyncio.sleep(1)
        shutdown_pc()

    elif action == "reboot":
        await reply("ok")
        await asyncio.sleep(1)
        reboot_pc()

@dp.message(Command("agent_ok"))
async def on_connected(message: Message):
    global CONNECTED
    if message.chat.id != USER_ID:
        return
    CONNECTED = True
    print(f"\n✅ Підключено до бота!")
    print(f"💻 ПК: {PC_NAME}")
    print("\n🟢 Агент працює. Не закривай це вікно!")
    print("   Telegram → бот → 🖥 Комп'ютер → керуй ПК")
    print("\nCtrl+C для зупинки\n")

# ─── Heartbeat ────────────────────────────────────────────────────────────────

async def heartbeat_loop():
    while True:
        await asyncio.sleep(PING_INTERVAL)
        if CONNECTED and USER_ID:
            try:
                await bot.send_message(USER_ID, f"/agent_ping")
            except Exception:
                pass

# ─── Головна функція ──────────────────────────────────────────────────────────

async def main():
    global USER_ID

    TELEGRAM_ID = get_telegram_id()
    USER_ID = TELEGRAM_ID

    print("\n" + "=" * 50)
    print("  PC Agent — Telegram PC Control")
    print("=" * 50)

    code = input("\n🔑 Введи код підключення з бота: ").strip().upper()
    if not code:
        print("❌ Код не введено!")
        return

    print(f"\n📡 Підключення...")

    try:
        await bot.send_message(USER_ID, f"/agent_connect {code} {PC_NAME}")
    except Exception as e:
        print(f"❌ Помилка: {e}")
        print("\nПеревір:")
        print("  • Токен бота правильний (в коді)")
        print("  • Ти писав /start боту в Telegram?")
        print("  • Telegram ID правильний?")
        # Скидаємо ID щоб можна було ввести новий
        config = load_config()
        config.pop("telegram_id", None)
        save_config(config)
        return

    print("⏳ Очікую підтвердження від бота...")

    connected_event = asyncio.Event()

    @dp.message(Command("agent_ok"))
    async def _on_ok(msg: Message):
        global CONNECTED
        if msg.chat.id != USER_ID:
            return
        CONNECTED = True
        connected_event.set()
        print(f"\n✅ Підключено!")
        print(f"💻 ПК: {PC_NAME}")
        print("\n🟢 Агент працює. Не закривай це вікно!")
        print("   Telegram → бот → 🖥 Комп'ютер → керуй ПК")
        print("\nCtrl+C для зупинки\n")

    polling_task = asyncio.create_task(dp.start_polling(bot, handle_as_tasks=True))

    try:
        await asyncio.wait_for(connected_event.wait(), timeout=20)
    except asyncio.TimeoutError:
        print("❌ Таймаут! Перевір:")
        print("  • Код правильний?")
        print("  • Код не прострочений? (дійсний 24г)")
        print("  • Бот запущений на Railway?")
        polling_task.cancel()
        return

    heartbeat_task = asyncio.create_task(heartbeat_loop())

    try:
        await polling_task
    except asyncio.CancelledError:
        pass
    finally:
        heartbeat_task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Агент зупинено.")
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        input("\nНатисни Enter щоб закрити...")
