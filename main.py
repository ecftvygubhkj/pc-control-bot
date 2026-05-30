import asyncio
import os
import json
import secrets
import time
import aiohttp
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_ТУТ")

# ── Переклади ──────────────────────────────────────────────────────────────────
TEXTS = {
    "uk": {
        "welcome": (
            "👋 Привіт, <b>{name}</b>!\n\n"
            "Я бот для керування твоїм ПК прямо з Telegram.\n"
            "Вибери розділ нижче 👇"
        ),
        "btn_pc": "🖥 Комп'ютер",
        "btn_settings": "⚙️ Налаштування",
        "pc_offline": "🔴 <b>ПК не підключений</b>\n\nНатисни кнопку нижче щоб підключити свій комп'ютер.",
        "connect_btn": "🔌 Підключити ПК",
        "your_code": (
            "🔑 <b>Твій код підключення:</b>\n\n"
            "<code>{code}</code>\n\n"
            "📋 <b>Інструкція:</b>\n\n"
            "1. Встанови <a href='https://python.org/downloads'>Python</a> якщо ще не встановлено\n\n"
            "2. Встанови бібліотеки:\n"
            "<code>pip install psutil pycaw comtypes Pillow pyautogui requests</code>\n\n"
            "3. Встанови <a href='https://ngrok.com/download'>ngrok</a> і налаштуй authtoken\n\n"
            "4. <a href='https://raw.githubusercontent.com/ecftvygubhkj/pc-control-bot/main/pc_agent.py'>⬇️ Завантаж pc_agent.py</a>\n\n"
            "5. Запусти:\n"
            "<code>python pc_agent.py</code>\n\n"
            "6. Введи токен бота, свій Telegram ID, потім код <code>{code}</code>\n\n"
            "✅ ПК з'явиться онлайн автоматично!\n\n"
            "⏳ Код дійсний 24 години."
        ),
        "pc_online": "🟢 <b>ПК онлайн</b>\n\n💻 {name}\nОстанній сигнал: {time}",
        "pc_menu": "Вибери дію:",
        "btn_stats": "📊 Статистика",
        "btn_volume": "🔊 Гучність",
        "btn_music": "🎵 Музика",
        "btn_mic": "🎤 Мікрофон",
        "btn_screenshot": "📸 Скріншот",
        "btn_shutdown": "🔴 Вимкнути ПК",
        "btn_reboot": "🔄 Перезавантажити",
        "btn_sleep": "💤 Сон",
        "btn_lock": "🔒 Заблокувати",
        "btn_back": "◀️ Назад",
        "settings_title": "⚙️ <b>Налаштування</b>",
        "lang_btn": "🌐 Мова: Українська",
        "about_btn": "ℹ️ Про бота",
        "about_text": (
            "🤖 <b>PC Control Bot</b>\n\n"
            "Версія: 3.0\n"
            "Керуй своїм ПК прямо з Telegram!\n\n"
            "<b>Функції:</b>\n"
            "• 📊 Статистика (CPU, RAM, диск, мережа)\n"
            "• 🔊 Керування гучністю\n"
            "• 🎵 Музика (play/pause/next/prev)\n"
            "• 🎤 Вмикати/вимикати мікрофон\n"
            "• 📸 Скріншот екрану\n"
            "• 🔴 Вимкнення / перезавантаження\n"
            "• 💤 Режим сну\n"
            "• 🔒 Блокування екрану\n\n"
            "Кожен користувач підключає свій ПК окремо!\n"
            "Ніхто не має доступу до чужого комп'ютера."
        ),
        "lang_changed": "✅ Мову змінено на Українську",
        "choose_lang": "🌐 Вибери мову / Choose language:",
        "cmd_sent": "✅ Команду надіслано",
        "waiting_response": "⏳ Очікую відповідь від ПК...",
        "pc_disconnected": "❌ ПК не відповідає. Переконайся що pc_agent.py запущений.",
        "vol_current": "🔊 Поточна гучність: <b>{vol}%</b>",
        "vol_keyboard": "Вибери дію з гучністю:",
        "music_keyboard": "Вибери дію:",
        "btn_vol_up": "🔊 +10%",
        "btn_vol_down": "🔉 -10%",
        "btn_vol_mute": "🔇 Mute",
        "btn_play_pause": "⏯ Play/Pause",
        "btn_next": "⏭ Наступний",
        "btn_prev": "⏮ Попередній",
        "btn_mic_toggle": "🎤 Вкл/Викл мікрофон",
        "shutdown_confirm": "⚠️ <b>Ти впевнений?</b>\nПК буде вимкнено!",
        "btn_yes": "✅ Так, вимкнути",
        "btn_cancel": "❌ Скасувати",
        "reboot_confirm": "⚠️ <b>Ти впевнений?</b>\nПК буде перезавантажено!",
        "btn_yes_reboot": "✅ Так, перезавантажити",
        "disconnected_pc": "🔴 ПК відключився",
        "new_code": "🔄 Новий код",
        "pc_connected_notify": "🟢 <b>ПК підключено!</b>\n💻 {name}",
    },
    "en": {
        "welcome": (
            "👋 Hello, <b>{name}</b>!\n\n"
            "I'm a bot to control your PC directly from Telegram.\n"
            "Choose a section below 👇"
        ),
        "btn_pc": "🖥 Computer",
        "btn_settings": "⚙️ Settings",
        "pc_offline": "🔴 <b>PC is not connected</b>\n\nPress the button below to connect your computer.",
        "connect_btn": "🔌 Connect PC",
        "your_code": (
            "🔑 <b>Your connection code:</b>\n\n"
            "<code>{code}</code>\n\n"
            "📋 <b>Instructions:</b>\n\n"
            "1. Install <a href='https://python.org/downloads'>Python</a> if not installed\n\n"
            "2. Install libraries:\n"
            "<code>pip install psutil pycaw comtypes Pillow pyautogui requests</code>\n\n"
            "3. Install <a href='https://ngrok.com/download'>ngrok</a> and set up authtoken\n\n"
            "4. <a href='https://raw.githubusercontent.com/ecftvygubhkj/pc-control-bot/main/pc_agent.py'>⬇️ Download pc_agent.py</a>\n\n"
            "5. Run:\n"
            "<code>python pc_agent.py</code>\n\n"
            "6. Enter bot token, your Telegram ID, then code <code>{code}</code>\n\n"
            "✅ PC will appear online automatically!\n\n"
            "⏳ Code is valid for 24 hours."
        ),
        "pc_online": "🟢 <b>PC Online</b>\n\n💻 {name}\nLast seen: {time}",
        "pc_menu": "Choose action:",
        "btn_stats": "📊 Statistics",
        "btn_volume": "🔊 Volume",
        "btn_music": "🎵 Music",
        "btn_mic": "🎤 Microphone",
        "btn_screenshot": "📸 Screenshot",
        "btn_shutdown": "🔴 Shutdown PC",
        "btn_reboot": "🔄 Reboot",
        "btn_sleep": "💤 Sleep",
        "btn_lock": "🔒 Lock",
        "btn_back": "◀️ Back",
        "settings_title": "⚙️ <b>Settings</b>",
        "lang_btn": "🌐 Language: English",
        "about_btn": "ℹ️ About bot",
        "about_text": (
            "🤖 <b>PC Control Bot</b>\n\n"
            "Version: 3.0\n"
            "Control your PC directly from Telegram!\n\n"
            "<b>Features:</b>\n"
            "• 📊 Statistics (CPU, RAM, disk, network)\n"
            "• 🔊 Volume control\n"
            "• 🎵 Music (play/pause/next/prev)\n"
            "• 🎤 Microphone on/off\n"
            "• 📸 Screenshot\n"
            "• 🔴 Shutdown / reboot\n"
            "• 💤 Sleep mode\n"
            "• 🔒 Lock screen\n\n"
            "Each user connects their own PC separately!\n"
            "Nobody can access someone else's computer."
        ),
        "lang_changed": "✅ Language changed to English",
        "choose_lang": "🌐 Вибери мову / Choose language:",
        "cmd_sent": "✅ Command sent",
        "waiting_response": "⏳ Waiting for PC response...",
        "pc_disconnected": "❌ PC is not responding. Make sure pc_agent.py is running.",
        "vol_current": "🔊 Current volume: <b>{vol}%</b>",
        "vol_keyboard": "Choose volume action:",
        "music_keyboard": "Choose action:",
        "btn_vol_up": "🔊 +10%",
        "btn_vol_down": "🔉 -10%",
        "btn_vol_mute": "🔇 Mute",
        "btn_play_pause": "⏯ Play/Pause",
        "btn_next": "⏭ Next",
        "btn_prev": "⏮ Previous",
        "btn_mic_toggle": "🎤 Toggle Microphone",
        "shutdown_confirm": "⚠️ <b>Are you sure?</b>\nPC will be shut down!",
        "btn_yes": "✅ Yes, shutdown",
        "btn_cancel": "❌ Cancel",
        "reboot_confirm": "⚠️ <b>Are you sure?</b>\nPC will be rebooted!",
        "btn_yes_reboot": "✅ Yes, reboot",
        "disconnected_pc": "🔴 PC disconnected",
        "new_code": "🔄 New code",
        "pc_connected_notify": "🟢 <b>PC connected!</b>\n💻 {name}",
    }
}

# ── Стан ──────────────────────────────────────────────────────────────────────
user_lang = {}      # user_id -> "uk" / "en"
user_codes = {}     # code -> {"user_id": int, "expires": float}
connected_pcs = {}  # user_id -> {"name": str, "last_seen": float, "url": str}

def t(user_id, key, **kwargs):
    lang = user_lang.get(user_id, "uk")
    text = TEXTS[lang][key]
    if kwargs:
        text = text.format(**kwargs)
    return text

def is_pc_online(user_id):
    if user_id not in connected_pcs:
        return False
    last = connected_pcs[user_id]["last_seen"]
    return (time.time() - last) < 45  # 45 секунд таймаут

def format_time(ts):
    import datetime
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime("%H:%M:%S")

# ── Генерація коду ────────────────────────────────────────────────────────────
def generate_code(user_id):
    # Повернути існуючий діючий код
    for c, v in list(user_codes.items()):
        if v["user_id"] == user_id and time.time() < v["expires"]:
            return c

    # Видалити прострочений
    to_delete = [c for c, v in user_codes.items() if v["user_id"] == user_id]
    for c in to_delete:
        del user_codes[c]

    # Генеруємо новий
    code = secrets.token_hex(3).upper()
    user_codes[code] = {
        "user_id": user_id,
        "expires": time.time() + 86400
    }
    return code

def get_user_by_code(code):
    data = user_codes.get(code)
    if not data:
        return None
    if time.time() > data["expires"]:
        del user_codes[code]
        return None
    return data["user_id"]

# ── HTTP запит до агента ──────────────────────────────────────────────────────
async def send_to_agent(user_id: int, action: str) -> str | None:
    """Надсилає HTTP POST до агента і повертає результат"""
    if not is_pc_online(user_id):
        return None

    url = connected_pcs[user_id]["url"]

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{url}/cmd",
                json={"action": action},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("result", "ok")
                return None
    except Exception as e:
        print(f"[send_to_agent] Помилка: {e}")
        # Якщо не відповів — помічаємо як офлайн
        if user_id in connected_pcs:
            connected_pcs[user_id]["last_seen"] = 0
        return None

# ── Клавіатури ────────────────────────────────────────────────────────────────
def main_keyboard(user_id):
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text=t(user_id, "btn_pc")),
            KeyboardButton(text=t(user_id, "btn_settings")),
        ]],
        resize_keyboard=True,
        is_persistent=True
    )

def pc_offline_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(user_id, "connect_btn"), callback_data="show_code")
    ]])

def pc_online_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(user_id, "btn_stats"), callback_data="pc_stats"),
            InlineKeyboardButton(text=t(user_id, "btn_screenshot"), callback_data="pc_screenshot"),
        ],
        [
            InlineKeyboardButton(text=t(user_id, "btn_volume"), callback_data="pc_volume"),
            InlineKeyboardButton(text=t(user_id, "btn_music"), callback_data="pc_music"),
        ],
        [
            InlineKeyboardButton(text=t(user_id, "btn_mic"), callback_data="pc_mic"),
            InlineKeyboardButton(text=t(user_id, "btn_lock"), callback_data="pc_lock"),
        ],
        [
            InlineKeyboardButton(text=t(user_id, "btn_sleep"), callback_data="pc_sleep"),
        ],
        [
            InlineKeyboardButton(text=t(user_id, "btn_reboot"), callback_data="pc_reboot"),
            InlineKeyboardButton(text=t(user_id, "btn_shutdown"), callback_data="pc_shutdown"),
        ],
    ])

def volume_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(user_id, "btn_vol_down"), callback_data="vol_down"),
            InlineKeyboardButton(text=t(user_id, "btn_vol_up"), callback_data="vol_up"),
        ],
        [InlineKeyboardButton(text=t(user_id, "btn_vol_mute"), callback_data="vol_mute")],
        [InlineKeyboardButton(text=t(user_id, "btn_back"), callback_data="pc_back")],
    ])

def music_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(user_id, "btn_prev"), callback_data="music_prev"),
            InlineKeyboardButton(text=t(user_id, "btn_play_pause"), callback_data="music_playpause"),
            InlineKeyboardButton(text=t(user_id, "btn_next"), callback_data="music_next"),
        ],
        [InlineKeyboardButton(text=t(user_id, "btn_back"), callback_data="pc_back")],
    ])

def shutdown_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(user_id, "btn_yes"), callback_data="shutdown_yes"),
        InlineKeyboardButton(text=t(user_id, "btn_cancel"), callback_data="pc_back"),
    ]])

def reboot_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(user_id, "btn_yes_reboot"), callback_data="reboot_yes"),
        InlineKeyboardButton(text=t(user_id, "btn_cancel"), callback_data="pc_back"),
    ]])

def settings_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(user_id, "lang_btn"), callback_data="change_lang")],
        [InlineKeyboardButton(text=t(user_id, "about_btn"), callback_data="about")],
    ])

def lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="set_lang_uk")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en")],
    ])

# ── Бот і диспетчер ───────────────────────────────────────────────────────────
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ── Хендлери ──────────────────────────────────────────────────────────────────
@dp.message(Command("start"))
async def cmd_start(message: Message):
    uid = message.from_user.id
    name = message.from_user.first_name or "Друже"
    await message.answer(
        t(uid, "welcome", name=name),
        reply_markup=main_keyboard(uid),
        parse_mode="HTML"
    )

@dp.message(F.text.in_(["🖥 Комп'ютер", "🖥 Computer"]))
async def section_pc(message: Message):
    uid = message.from_user.id
    if is_pc_online(uid):
        pc = connected_pcs[uid]
        await message.answer(
            t(uid, "pc_online", name=pc["name"], time=format_time(pc["last_seen"])) + "\n\n" + t(uid, "pc_menu"),
            reply_markup=pc_online_keyboard(uid),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            t(uid, "pc_offline"),
            reply_markup=pc_offline_keyboard(uid),
            parse_mode="HTML"
        )

@dp.message(F.text.in_(["⚙️ Налаштування", "⚙️ Settings"]))
async def section_settings(message: Message):
    uid = message.from_user.id
    await message.answer(
        t(uid, "settings_title"),
        reply_markup=settings_keyboard(uid),
        parse_mode="HTML"
    )

# ── Показати код підключення ──────────────────────────────────────────────────
@dp.callback_query(F.data == "show_code")
async def show_code(cb: CallbackQuery):
    uid = cb.from_user.id
    code = generate_code(uid)
    await cb.message.answer(
        t(uid, "your_code", code=code),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await cb.answer()

# ── Реєстрація агента: /agent_connect CODE PC_NAME NGROK_URL ─────────────────
@dp.message(Command("agent_connect"))
async def agent_connect(message: Message):
    parts = message.text.split(maxsplit=3)
    # /agent_connect CODE PC_NAME https://xxxx.ngrok.io
    if len(parts) < 4:
        await message.answer("ERROR:invalid_format")
        return

    code = parts[1].upper()
    pc_name = parts[2]
    ngrok_url = parts[3].strip()

    user_id = get_user_by_code(code)
    if not user_id:
        await message.answer("ERROR:invalid_code")
        return

    # Зберігаємо підключення з ngrok URL
    connected_pcs[user_id] = {
        "name": pc_name,
        "last_seen": time.time(),
        "url": ngrok_url,
    }

    # Видаляємо використаний код
    to_del = [c for c, v in user_codes.items() if v["user_id"] == user_id]
    for c in to_del:
        del user_codes[c]

    print(f"✅ ПК підключено: {pc_name} | {ngrok_url} | user_id={user_id}")

    # Повідомляємо користувача
    await bot.send_message(
        user_id,
        t(user_id, "pc_connected_notify", name=pc_name),
        parse_mode="HTML",
        reply_markup=main_keyboard(user_id)
    )

# ── Пінг від агента: /agent_ping NGROK_URL ───────────────────────────────────
@dp.message(Command("agent_ping"))
async def agent_ping(message: Message):
    parts = message.text.split(maxsplit=1)
    user_id = message.from_user.id
    if user_id in connected_pcs:
        connected_pcs[user_id]["last_seen"] = time.time()
        # Оновлюємо URL якщо передано (ngrok URL може змінитись)
        if len(parts) == 2:
            connected_pcs[user_id]["url"] = parts[1].strip()
        print(f"📡 Ping від {connected_pcs[user_id]['name']}")

# ── Назад до меню ПК ─────────────────────────────────────────────────────────
@dp.callback_query(F.data == "pc_back")
async def pc_back(cb: CallbackQuery):
    uid = cb.from_user.id
    if is_pc_online(uid):
        pc = connected_pcs[uid]
        await cb.message.edit_text(
            t(uid, "pc_online", name=pc["name"], time=format_time(pc["last_seen"])) + "\n\n" + t(uid, "pc_menu"),
            reply_markup=pc_online_keyboard(uid),
            parse_mode="HTML"
        )
    else:
        await cb.message.edit_text(
            t(uid, "pc_offline"),
            reply_markup=pc_offline_keyboard(uid),
            parse_mode="HTML"
        )
    await cb.answer()

# ── Статистика ────────────────────────────────────────────────────────────────
@dp.callback_query(F.data == "pc_stats")
async def pc_stats(cb: CallbackQuery):
    uid = cb.from_user.id
    await cb.answer(t(uid, "waiting_response"))
    result = await send_to_agent(uid, "stats")
    if result is None:
        await cb.message.answer(t(uid, "pc_disconnected"))

# ── Скріншот ──────────────────────────────────────────────────────────────────
@dp.callback_query(F.data == "pc_screenshot")
async def pc_screenshot(cb: CallbackQuery):
    uid = cb.from_user.id
    await cb.answer(t(uid, "waiting_response"))
    result = await send_to_agent(uid, "screenshot")
    if result is None:
        await cb.message.answer(t(uid, "pc_disconnected"))

# ── Гучність ──────────────────────────────────────────────────────────────────
@dp.callback_query(F.data == "pc_volume")
async def pc_volume(cb: CallbackQuery):
    uid = cb.from_user.id
    vol = await send_to_agent(uid, "get_volume") or "?"
    await cb.message.edit_text(
        t(uid, "vol_current", vol=vol) + "\n\n" + t(uid, "vol_keyboard"),
        reply_markup=volume_keyboard(uid),
        parse_mode="HTML"
    )
    await cb.answer()

@dp.callback_query(F.data.in_(["vol_up", "vol_down", "vol_mute"]))
async def volume_action(cb: CallbackQuery):
    uid = cb.from_user.id
    vol = await send_to_agent(uid, cb.data) or "?"
    await cb.message.edit_text(
        t(uid, "vol_current", vol=vol) + "\n\n" + t(uid, "vol_keyboard"),
        reply_markup=volume_keyboard(uid),
        parse_mode="HTML"
    )
    await cb.answer(t(uid, "cmd_sent"))

# ── Музика ────────────────────────────────────────────────────────────────────
@dp.callback_query(F.data == "pc_music")
async def pc_music(cb: CallbackQuery):
    uid = cb.from_user.id
    await cb.message.edit_text(t(uid, "music_keyboard"), reply_markup=music_keyboard(uid))
    await cb.answer()

@dp.callback_query(F.data.in_(["music_prev", "music_playpause", "music_next"]))
async def music_action(cb: CallbackQuery):
    uid = cb.from_user.id
    await send_to_agent(uid, cb.data)
    await cb.answer(t(uid, "cmd_sent"))

# ── Мікрофон ─────────────────────────────────────────────────────────────────
@dp.callback_query(F.data == "pc_mic")
async def pc_mic(cb: CallbackQuery):
    uid = cb.from_user.id
    result = await send_to_agent(uid, "mic_toggle") or "?"
    await cb.answer(f"🎤 {result}", show_alert=True)

# ── Заблокувати ───────────────────────────────────────────────────────────────
@dp.callback_query(F.data == "pc_lock")
async def pc_lock(cb: CallbackQuery):
    uid = cb.from_user.id
    await send_to_agent(uid, "lock")
    await cb.answer(t(uid, "cmd_sent"))

# ── Сон ──────────────────────────────────────────────────────────────────────
@dp.callback_query(F.data == "pc_sleep")
async def pc_sleep(cb: CallbackQuery):
    uid = cb.from_user.id
    await send_to_agent(uid, "sleep")
    await cb.answer(t(uid, "cmd_sent"))

# ── Вимкнення ─────────────────────────────────────────────────────────────────
@dp.callback_query(F.data == "pc_shutdown")
async def pc_shutdown_confirm(cb: CallbackQuery):
    uid = cb.from_user.id
    await cb.message.edit_text(
        t(uid, "shutdown_confirm"),
        reply_markup=shutdown_keyboard(uid),
        parse_mode="HTML"
    )
    await cb.answer()

@dp.callback_query(F.data == "shutdown_yes")
async def pc_shutdown_yes(cb: CallbackQuery):
    uid = cb.from_user.id
    await send_to_agent(uid, "shutdown")
    connected_pcs.pop(uid, None)
    await cb.message.edit_text(t(uid, "disconnected_pc"))
    await cb.answer()

# ── Перезавантаження ──────────────────────────────────────────────────────────
@dp.callback_query(F.data == "pc_reboot")
async def pc_reboot_confirm(cb: CallbackQuery):
    uid = cb.from_user.id
    await cb.message.edit_text(
        t(uid, "reboot_confirm"),
        reply_markup=reboot_keyboard(uid),
        parse_mode="HTML"
    )
    await cb.answer()

@dp.callback_query(F.data == "reboot_yes")
async def pc_reboot_yes(cb: CallbackQuery):
    uid = cb.from_user.id
    await send_to_agent(uid, "reboot")
    connected_pcs.pop(uid, None)
    await cb.message.edit_text(t(uid, "disconnected_pc"))
    await cb.answer()

# ── Налаштування ──────────────────────────────────────────────────────────────
@dp.callback_query(F.data == "about")
async def show_about(cb: CallbackQuery):
    uid = cb.from_user.id
    await cb.message.answer(t(uid, "about_text"), parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data == "change_lang")
async def change_lang(cb: CallbackQuery):
    uid = cb.from_user.id
    await cb.message.answer(t(uid, "choose_lang"), reply_markup=lang_keyboard())
    await cb.answer()

@dp.callback_query(F.data.in_(["set_lang_uk", "set_lang_en"]))
async def set_lang(cb: CallbackQuery):
    uid = cb.from_user.id
    lang = "uk" if cb.data == "set_lang_uk" else "en"
    user_lang[uid] = lang
    await cb.message.answer(t(uid, "lang_changed"), reply_markup=main_keyboard(uid))
    await cb.answer()

# ── Запуск ────────────────────────────────────────────────────────────────────
async def main():
    print("✅ Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
