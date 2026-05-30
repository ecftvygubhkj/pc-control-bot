import asyncio
import os
import json
import secrets
import time
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

BOT_TOKEN = "8850935816:AAFGqfuMG7WEWVyFqFwI5Sw-lVMwC_GGSfI"

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
            "1. Встанови Python якщо ще не встановлено\n"
            "2. Встанови бібліотеки в терміналі:\n"
            "<code>pip install aiogram psutil pycaw comtypes Pillow</code>\n\n"
            "3. Завантаж файл <b>pc_agent.py</b>\n\n"
            "4. Запусти:\n"
            "<code>python pc_agent.py</code>\n\n"
            "5. Введи код <code>{code}</code> коли запитає\n\n"
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
            "Версія: 2.0\n"
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
            "1. Install Python if not already installed\n"
            "2. Install libraries in terminal:\n"
            "<code>pip install aiogram psutil pycaw comtypes Pillow</code>\n\n"
            "3. Download <b>pc_agent.py</b>\n\n"
            "4. Run:\n"
            "<code>python pc_agent.py</code>\n\n"
            "5. Enter code <code>{code}</code> when asked\n\n"
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
            "Version: 2.0\n"
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
    }
}

# ── Стан ──────────────────────────────────────────────────────────────────────
user_lang = {}          # user_id -> "uk" / "en"
user_codes = {}         # code -> {"user_id": int, "expires": float}
connected_pcs = {}      # user_id -> {"name": str, "last_seen": float, "chat_id": int}
pending_commands = {}   # user_id -> {"action": str, "data": any}
pending_responses = {}  # user_id -> asyncio.Queue

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
    return (time.time() - last) < 30  # 30 секунд таймаут

def format_time(ts):
    import datetime
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime("%H:%M:%S")

# ── Генерація коду ────────────────────────────────────────────────────────────
def generate_code(user_id):
    # Видалити старий код якщо є
    to_delete = [c for c, v in user_codes.items() if v["user_id"] == user_id]
    for c in to_delete:
        del user_codes[c]
    
    code = secrets.token_hex(3).upper()  # Наприклад: A3F2B1
    user_codes[code] = {
        "user_id": user_id,
        "expires": time.time() + 86400  # 24 години
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
    lang = user_lang.get(user_id, "uk")
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
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(user_id, "btn_yes"), callback_data="shutdown_yes"),
            InlineKeyboardButton(text=t(user_id, "btn_cancel"), callback_data="pc_back"),
        ]
    ])

def reboot_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(user_id, "btn_yes_reboot"), callback_data="reboot_yes"),
            InlineKeyboardButton(text=t(user_id, "btn_cancel"), callback_data="pc_back"),
        ]
    ])

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
        parse_mode="HTML"
    )
    await cb.answer()

# ── API для агента: реєстрація ПК ─────────────────────────────────────────────
@dp.message(Command("agent_connect"))
async def agent_connect(message: Message):
    """Команда від pc_agent.py для реєстрації"""
    parts = message.text.split(maxsplit=2)
    # /agent_connect CODE PC_NAME
    if len(parts) < 3:
        await message.answer("ERROR:invalid_format")
        return
    
    code = parts[1].upper()
    pc_name = parts[2]
    
    user_id = get_user_by_code(code)
    if not user_id:
        await message.answer("ERROR:invalid_code")
        return
    
    # Зберігаємо підключення
    connected_pcs[user_id] = {
        "name": pc_name,
        "last_seen": time.time(),
        "agent_chat_id": message.chat.id,
        "agent_user_id": message.from_user.id,
    }
    
    # Видаляємо код після використання
    to_del = [c for c, v in user_codes.items() if v["user_id"] == user_id]
    for c in to_del:
        del user_codes[c]
    
    await message.answer(f"OK:connected:{user_id}")
    
    # Сповіщаємо користувача
    try:
        await bot.send_message(
            user_id,
            f"🟢 <b>ПК підключено!</b>\n💻 {pc_name}",
            parse_mode="HTML",
            reply_markup=main_keyboard(user_id)
        )
    except Exception:
        pass

# ── API для агента: пінг (heartbeat) ─────────────────────────────────────────
@dp.message(Command("agent_ping"))
async def agent_ping(message: Message):
    """Пінг від агента щоб показати що ПК онлайн"""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return
    try:
        user_id = int(parts[1])
        if user_id in connected_pcs:
            connected_pcs[user_id]["last_seen"] = time.time()
            await message.answer("OK:pong")
    except Exception:
        pass

# ── API для агента: відповідь на команду ─────────────────────────────────────
@dp.message(Command("agent_response"))
async def agent_response(message: Message):
    """Відповідь від агента на команду"""
    # Формат: /agent_response USER_ID TYPE DATA
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        return
    try:
        user_id = int(parts[1])
        resp_type = parts[2]
        data = parts[3]
        
        if user_id in pending_responses:
            await pending_responses[user_id].put({"type": resp_type, "data": data})
    except Exception:
        pass

# ── Відправити команду до агента ─────────────────────────────────────────────
async def send_command_to_pc(user_id, action, data=""):
    if not is_pc_online(user_id):
        return None
    
    agent_chat_id = connected_pcs[user_id]["agent_chat_id"]
    pending_responses[user_id] = asyncio.Queue()
    
    try:
        await bot.send_message(agent_chat_id, f"/cmd {user_id} {action} {data}".strip())
        response = await asyncio.wait_for(pending_responses[user_id].get(), timeout=10)
        return response
    except asyncio.TimeoutError:
        return None
    finally:
        pending_responses.pop(user_id, None)

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
    
    response = await send_command_to_pc(uid, "stats")
    if not response:
        await cb.message.answer(t(uid, "pc_disconnected"))
        return
    
    await cb.message.answer(response["data"], parse_mode="HTML")

# ── Скріншот ──────────────────────────────────────────────────────────────────
@dp.callback_query(F.data == "pc_screenshot")
async def pc_screenshot(cb: CallbackQuery):
    uid = cb.from_user.id
    await cb.answer(t(uid, "waiting_response"))
    
    response = await send_command_to_pc(uid, "screenshot")
    if not response:
        await cb.message.answer(t(uid, "pc_disconnected"))
        return
    # Агент надішле фото напряму

# ── Гучність ──────────────────────────────────────────────────────────────────
@dp.callback_query(F.data == "pc_volume")
async def pc_volume(cb: CallbackQuery):
    uid = cb.from_user.id
    response = await send_command_to_pc(uid, "get_volume")
    vol = response["data"] if response else "?"
    await cb.message.edit_text(
        t(uid, "vol_current", vol=vol) + "\n\n" + t(uid, "vol_keyboard"),
        reply_markup=volume_keyboard(uid),
        parse_mode="HTML"
    )
    await cb.answer()

@dp.callback_query(F.data.in_(["vol_up", "vol_down", "vol_mute"]))
async def volume_action(cb: CallbackQuery):
    uid = cb.from_user.id
    action_map = {"vol_up": "vol_up", "vol_down": "vol_down", "vol_mute": "vol_mute"}
    action = action_map[cb.data]
    response = await send_command_to_pc(uid, action)
    vol = response["data"] if response else "?"
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
    await cb.message.edit_text(
        t(uid, "music_keyboard"),
        reply_markup=music_keyboard(uid)
    )
    await cb.answer()

@dp.callback_query(F.data.in_(["music_prev", "music_playpause", "music_next"]))
async def music_action(cb: CallbackQuery):
    uid = cb.from_user.id
    await send_command_to_pc(uid, cb.data)
    await cb.answer(t(uid, "cmd_sent"))

# ── Мікрофон ─────────────────────────────────────────────────────────────────
@dp.callback_query(F.data == "pc_mic")
async def pc_mic(cb: CallbackQuery):
    uid = cb.from_user.id
    response = await send_command_to_pc(uid, "mic_toggle")
    status = response["data"] if response else "?"
    await cb.answer(f"🎤 {status}", show_alert=True)

# ── Заблокувати ───────────────────────────────────────────────────────────────
@dp.callback_query(F.data == "pc_lock")
async def pc_lock(cb: CallbackQuery):
    uid = cb.from_user.id
    await send_command_to_pc(uid, "lock")
    await cb.answer(t(uid, "cmd_sent"))

# ── Сон ──────────────────────────────────────────────────────────────────────
@dp.callback_query(F.data == "pc_sleep")
async def pc_sleep(cb: CallbackQuery):
    uid = cb.from_user.id
    await send_command_to_pc(uid, "sleep")
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
    await send_command_to_pc(uid, "shutdown")
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
    await send_command_to_pc(uid, "reboot")
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
    await cb.message.answer(
        t(uid, "lang_changed"),
        reply_markup=main_keyboard(uid)
    )
    await cb.answer()

# ── Запуск ────────────────────────────────────────────────────────────────────
async def main():
    print("✅ Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())