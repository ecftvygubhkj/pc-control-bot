## 💻 Як підключити свій ПК до бота

1. Напиши боту `/start`
2. Натисни **🖥 Комп'ютер** → **🔌 Підключити ПК**
3. Отримай унікальний код підключення
4. Завантаж `pc_agent.py` на свій ПК
5. Встанови бібліотеки:
```bash
pip install aiogram psutil pycaw comtypes Pillow pyautogui
```
6. Відкрий `pc_agent.py` і встав токен бота
7. Запусти:
```bash
python pc_agent.py
```
8. Введи свій код — ПК з'явиться онлайн! ✅

> ⚠️ `pc_agent.py` має бути запущений на ПК поки ти хочеш ним керувати.

---

## 📁 Структура проєкту

```
pc-control-bot/
├── main.py           # Бот (деплоїться на Railway)
├── pc_agent.py       # Агент (запускається на ПК користувача)
├── requirements.txt  # Залежності
├── .env              # Токен (НЕ завантажувати на GitHub!)
├── .gitignore        # Ігнор файли
└── README.md         # Ця документація
```

---

## 🔒 Безпека

- Кожен користувач отримує **унікальний одноразовий код** підключення
- Код дійсний **24 години**
- Кожен бачить **тільки свій ПК**
- Токен бота зберігається в `.env` і **не потрапляє на GitHub**

---

## 🛠 Технології

- [aiogram 3](https://docs.aiogram.dev/) — Telegram Bot API
- [psutil](https://psutil.readthedocs.io/) — системна статистика
- [pycaw](https://github.com/AndreMiras/pycaw) — керування звуком Windows
- [Pillow](https://pillow.readthedocs.io/) — скріншоти
- [Railway](https://railway.app) — хостинг бота

---

## 📄 Ліцензія

MIT — використовуй як хочеш 🙂
