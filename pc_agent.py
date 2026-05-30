"""
pc_agent.py — запускається на ПК користувача

Встанови бібліотеки:
  pip install psutil pycaw comtypes Pillow pyautogui requests

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
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

CONFIG_FILE = "config.json"
PC_NAME = socket.gethostname()
HTTP_PORT = 8765

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
        print("Щоб дізнатись свій Telegram ID:")
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

# ─── Telegram надсилання (тільки відправка, без читання) ──────────────────────

def tg_send(token, chat_id, text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10
        )
    except Exception as e:
        print(f"[tg_send] Помилка: {e}")

def tg_send_photo(token, chat_id, photo_bytes, caption=""):
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendPhoto",
            data={"chat_id": chat_id, "caption": caption},
            files={"photo": ("screenshot.jpg", photo_bytes, "image/jpeg")},
            timeout=15
        )
    except Exception as e:
        print(f"[tg_send_photo] Помилка: {e}")

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
                    temp_str = f"\n🌡 Темп: {entries[0].current:.0f}°C"
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

# ─── HTTP сервер — приймає команди від main.py ────────────────────────────────

# Глобальні для доступу з хендлера
g_token = None
g_chat_id = None

class CommandHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Мовчазний режим — без спаму в термінал
        pass

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            action = data.get("action", "")

            print(f"  ▶ Команда: {action}")
            result = execute_command(action)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "result": result}).encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())

    def do_GET(self):
        # Пінг для перевірки що агент живий
        if self.path == "/ping":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "pc": PC_NAME}).encode())
        else:
            self.send_response(404)
            self.end_headers()

def execute_command(action: str) -> str:
    """Виконує команду і повертає результат як текст"""
    if action == "stats":
        result = get_stats()
        tg_send(g_token, g_chat_id, result)
        return "ok"

    elif action == "get_volume":
        vol = get_volume()
        return str(vol)

    elif action == "vol_up":
        vol = get_volume()
        new_vol = min(vol + 10, 100)
        set_volume(new_vol)
        return str(new_vol)

    elif action == "vol_down":
        vol = get_volume()
        new_vol = max(vol - 10, 0)
        set_volume(new_vol)
        return str(new_vol)

    elif action == "vol_mute":
        toggle_mute()
        return str(get_volume())

    elif action == "music_playpause":
        media_key(0xB3)
        return "ok"

    elif action == "music_next":
        media_key(0xB0)
        return "ok"

    elif action == "music_prev":
        media_key(0xB1)
        return "ok"

    elif action == "mic_toggle":
        result = toggle_mic()
        tg_send(g_token, g_chat_id, f"🎤 {result}")
        return result

    elif action == "screenshot":
        img = take_screenshot()
        if img:
            tg_send_photo(g_token, g_chat_id, img, f"📸 {PC_NAME}")
        return "ok"

    elif action == "lock":
        lock_screen()
        return "ok"

    elif action == "sleep":
        sleep_pc()
        return "ok"

    elif action == "shutdown":
        tg_send(g_token, g_chat_id, "🔴 ПК вимикається...")
        threading.Timer(2, shutdown_pc).start()
        return "ok"

    elif action == "reboot":
        tg_send(g_token, g_chat_id, "🔄 ПК перезавантажується...")
        threading.Timer(2, reboot_pc).start()
        return "ok"

    return "unknown_command"

# ─── Запуск ngrok і реєстрація в боті ────────────────────────────────────────

def start_ngrok() -> str:
    """Запускає ngrok і повертає публічний URL"""
    import subprocess

    # Спочатку вбиваємо старий ngrok якщо є
    try:
        subprocess.run(["taskkill", "/F", "/IM", "ngrok.exe"],
                       capture_output=True, timeout=5)
    except Exception:
        pass
    time.sleep(1)

    # Запускаємо ngrok
    try:
        subprocess.Popen(
            ["ngrok", "http", str(HTTP_PORT), "--log=stdout"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        print("❌ ngrok не знайдено! Встанови ngrok з https://ngrok.com/download")
        sys.exit(1)

    # Чекаємо поки ngrok запуститься
    print("⏳ Запуск ngrok...", end="", flush=True)
    for _ in range(20):
        time.sleep(1)
        print(".", end="", flush=True)
        try:
            r = requests.get("http://localhost:4040/api/tunnels", timeout=2)
            tunnels = r.json().get("tunnels", [])
            for tunnel in tunnels:
                if tunnel.get("proto") == "https":
                    print()
                    return tunnel["public_url"]
        except Exception:
            continue

    print("\n❌ ngrok не запустився. Перевір чи встановлений і налаштований authtoken.")
    sys.exit(1)






# ─── Головна функція ─────────────────────────────────────────────────────────

def main():
    global g_token, g_chat_id

    token, telegram_id = setup()
    g_token = token
    g_chat_id = int(telegram_id)

    print("=" * 50)
    print("  PC Agent — Telegram PC Control")
    print("=" * 50)

    code = input("\n🔑 Введи код підключення з бота: ").strip().upper()
    if not code:
        print("Код не введено!")
        return

    # Запускаємо HTTP сервер у фоні
    server = HTTPServer(("0.0.0.0", HTTP_PORT), CommandHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"✅ HTTP сервер запущено на порту {HTTP_PORT}")

    # Запускаємо ngrok
    ngrok_url = start_ngrok()
    print(f"🌐 Публічний URL: {ngrok_url}")

    # Реєструємося в боті
    print("📡 Реєстрація в боті...")
    register_with_bot(token, g_chat_id, ngrok_url, code)

    # Чекаємо підтвердження (перевіряємо чи бот відповів)
    print("⏳ Очікую підтвердження від бота...")
    time.sleep(3)

    print(f"\n✅ Підключено!")
    print(f"💻 ПК: {PC_NAME}")
    print(f"🌐 URL: {ngrok_url}")
    print("\n🟢 Агент працює. Не закривай це вікно!")
    print("   Telegram → бот → 🖥 Комп'ютер → керуй ПК")
    print("\nCtrl+C для зупинки\n")

    # Просто тримаємо сервер живим — бот сам пінгує агента через HTTP
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n\n👋 Агент зупинено.")
        server.shutdown()

if __name__ == "__main__":
    main()
