"""
pc_agent.py — запускається на ПК користувача
Підключається до бота через унікальний код і виконує команди.

Встанови бібліотеки:
  pip install aiogram psutil pycaw comtypes Pillow pyautogui

Запуск:
  python pc_agent.py
"""

import asyncio
import platform
import subprocess
import socket
import time
import os
import sys
import ctypes
import psutil
import io
import base64
import tempfile
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command

# ─────────────────────────────────────────────────────────────────────────────
BOT_TOKEN = "ВАШ_ТОКЕН_ТУТ"   # <-- вставте токен бота
# ─────────────────────────────────────────────────────────────────────────────

PC_NAME = socket.gethostname()
USER_ID = None          # буде заповнено після підключення
CONNECTED = False
PING_INTERVAL = 15      # секунди між пінгами

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ─── Системні функції ─────────────────────────────────────────────────────────

def get_stats() -> str:
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net = psutil.net_io_counters()
    uptime_sec = int(time.time() - psutil.boot_time())
    h, rem = divmod(uptime_sec, 3600)
    m = rem // 60

    # Температура (тільки якщо доступна)
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

    # Батарея
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
        f"🧠 RAM: <b>{mem.used / 1e9:.1f} / {mem.total / 1e9:.1f} GB</b> ({mem.percent}%)\n"
        f"💾 Диск: <b>{disk.used / 1e9:.1f} / {disk.total / 1e9:.1f} GB</b> ({disk.percent}%)\n"
        f"🌐 ↓ <b>{net.bytes_recv / 1e6:.1f} MB</b> ↑ <b>{net.bytes_sent / 1e6:.1f} MB</b>"
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
        level = max(0, min(100, level))
        volume.SetMasterVolumeLevelScalar(level / 100, None)
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
        muted = volume.GetMute()
        volume.SetMute(not muted, None)
    except Exception:
        pass

def media_key(vk_code):
    """Надіслати медіа-клавішу через Windows API"""
    if platform.system() != "Windows":
        return
    VK_MEDIA_PLAY_PAUSE = 0xB3
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1
    
    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP = 0x0002
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)

def toggle_mic() -> str:
    """Вмикає/вимикає мікрофон"""
    if platform.system() != "Windows":
        return "Не підтримується"
    try:
        from pycaw.pycaw import AudioUtilities
        mic = AudioUtilities.GetMicrophone()
        if not mic:
            return "Мікрофон не знайдено"
        
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import IAudioEndpointVolume
        
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

# ─── Обробка команд від бота ──────────────────────────────────────────────────

@dp.message(Command("cmd"))
async def handle_cmd(message: Message):
    global CONNECTED, USER_ID
    if not CONNECTED:
        return
    
    # Формат: /cmd USER_ID ACTION [DATA]
    parts = message.text.split(maxsplit=3)
    if len(parts) < 3:
        return
    
    try:
        uid = int(parts[1])
        if uid != USER_ID:
            return
        action = parts[2]
        data = parts[3] if len(parts) > 3 else ""
    except Exception:
        return
    
    async def reply(resp_type, resp_data):
        await message.answer(f"/agent_response {USER_ID} {resp_type} {resp_data}")
    
    # ── Статистика
    if action == "stats":
        stats = get_stats()
        await reply("text", stats)
    
    # ── Гучність
    elif action == "get_volume":
        vol = get_volume()
        await reply("text", str(vol))
    
    elif action == "vol_up":
        vol = get_volume()
        set_volume(vol + 10)
        await reply("text", str(min(vol + 10, 100)))
    
    elif action == "vol_down":
        vol = get_volume()
        set_volume(vol - 10)
        await reply("text", str(max(vol - 10, 0)))
    
    elif action == "vol_mute":
        toggle_mute()
        vol = get_volume()
        await reply("text", str(vol))
    
    # ── Музика
    elif action == "music_playpause":
        media_key(0xB3)
        await reply("text", "ok")
    
    elif action == "music_next":
        media_key(0xB0)
        await reply("text", "ok")
    
    elif action == "music_prev":
        media_key(0xB1)
        await reply("text", "ok")
    
    # ── Мікрофон
    elif action == "mic_toggle":
        status = toggle_mic()
        await reply("text", status)
    
    # ── Скріншот
    elif action == "screenshot":
        img_data = take_screenshot()
        if img_data:
            from aiogram.types import BufferedInputFile
            await bot.send_photo(
                chat_id=USER_ID,
                photo=BufferedInputFile(img_data, filename="screenshot.jpg"),
                caption=f"📸 {PC_NAME}"
            )
        await reply("text", "ok")
    
    # ── Блокування
    elif action == "lock":
        lock_screen()
        await reply("text", "ok")
    
    # ── Сон
    elif action == "sleep":
        await reply("text", "ok")
        await asyncio.sleep(1)
        sleep_pc()
    
    # ── Вимкнення
    elif action == "shutdown":
        await reply("text", "ok")
        await asyncio.sleep(1)
        shutdown_pc()
    
    # ── Перезавантаження
    elif action == "reboot":
        await reply("text", "ok")
        await asyncio.sleep(1)
        reboot_pc()

# ─── Пінг (heartbeat) ─────────────────────────────────────────────────────────

async def heartbeat_loop():
    """Кожні 15 секунд надсилає пінг до бота"""
    global CONNECTED
    while True:
        await asyncio.sleep(PING_INTERVAL)
        if CONNECTED and USER_ID:
            try:
                await bot.send_message(
                    bot.id if hasattr(bot, '_id') else (await bot.me()).id,
                    f"/agent_ping {USER_ID}"
                )
            except Exception:
                pass

async def send_ping():
    me = await bot.get_me()
    bot_chat_id = "@" + me.username
    await bot.send_message(bot_chat_id, f"/agent_ping {USER_ID}")

# ─── Підключення до бота ──────────────────────────────────────────────────────

async def connect_to_bot(code: str):
    global CONNECTED, USER_ID
    print(f"🔌 Підключення з кодом {code}...")
    me = await bot.get_me()
    
    try:
        result = await bot.send_message(f"@{me.username}", f"/agent_connect {code} {PC_NAME}")
    except Exception as e:
        print(f"❌ Помилка надсилання: {e}")
        return False
    
    # Чекаємо відповідь
    await asyncio.sleep(3)
    return True

# ─── Хендлер відповіді на підключення ───────────────────────────────────────

@dp.message(Command("agent_connect"))
async def on_connect_response(message: Message):
    """Отримуємо відповідь від бота після підключення"""
    # Цей хендлер не потрібен на стороні агента, але залишаємо для сумісності
    pass

# ─── Головна функція ──────────────────────────────────────────────────────────

async def main():
    global CONNECTED, USER_ID
    
    print("=" * 50)
    print("🖥  PC Agent — Telegram PC Control")
    print("=" * 50)
    
    # Запитуємо код
    code = input("\n🔑 Введи код підключення з бота: ").strip().upper()
    if not code:
        print("❌ Код не введено!")
        return
    
    # Підключаємось
    me = await bot.get_me()
    print(f"\n📡 Підключення до @{me.username}...")
    
    try:
        response = await bot.send_message(
            f"@{me.username}",
            f"/agent_connect {code} {PC_NAME}"
        )
    except Exception as e:
        print(f"❌ Помилка: {e}")
        print("\n📋 Перевір:")
        print("  • Токен правильний?")
        print("  • Бот запущений на Railway?")
        print("  • Ти писав /start боту в Telegram?")
        return
    
    # Чекаємо підтвердження (через polling)
    print("⏳ Очікую підтвердження...")
    
    connected_event = asyncio.Event()
    original_user_id = None
    
    @dp.message(lambda m: m.text and m.text.startswith("OK:connected:"))
    async def on_connected(msg: Message):
        global CONNECTED, USER_ID
        try:
            USER_ID = int(msg.text.split(":")[-1])
            CONNECTED = True
            connected_event.set()
            print(f"\n✅ Підключено! User ID: {USER_ID}")
            print(f"💻 ПК: {PC_NAME}")
            print("\n🟢 Агент працює. Не закривай це вікно!")
            print("   Telegram → бот → 🖥 Комп'ютер → керуй ПК")
            print("\nCtrl+C для зупинки\n")
        except Exception:
            pass
    
    # Запускаємо polling
    async def start_polling():
        await dp.start_polling(bot, handle_as_tasks=True)
    
    # Таймаут на підключення
    polling_task = asyncio.create_task(start_polling())
    
    try:
        await asyncio.wait_for(connected_event.wait(), timeout=15)
    except asyncio.TimeoutError:
        print("❌ Таймаут! Перевір:")
        print("  • Код правильний?")
        print("  • Код не прострочений? (дійсний 24г)")
        print("  • Бот запущений?")
        polling_task.cancel()
        return
    
    # Запускаємо heartbeat
    heartbeat_task = asyncio.create_task(heartbeat_loop_direct())
    
    try:
        await polling_task
    except asyncio.CancelledError:
        pass
    finally:
        heartbeat_task.cancel()

async def heartbeat_loop_direct():
    """Пінг напряму через бот"""
    global CONNECTED, USER_ID
    me = await bot.get_me()
    while True:
        await asyncio.sleep(PING_INTERVAL)
        if CONNECTED and USER_ID:
            try:
                await bot.send_message(f"@{me.username}", f"/agent_ping {USER_ID}")
            except Exception:
                pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Агент зупинено.")
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        input("\nНатисни Enter щоб закрити...")