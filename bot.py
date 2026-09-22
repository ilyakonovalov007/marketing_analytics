import asyncio
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(token=TOKEN)
dp = Dispatcher()


# Состояния заявки
class LeadForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_contact = State()

# Подключаем базу

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Таблица пользователей

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER,
    username TEXT,
    source TEXT,
    date TEXT
)
""")

# Таблица событий

cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event TEXT,
    source TEXT,
    date TEXT
)
""")
# Таблица лидов

cursor.execute("""
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    contact TEXT,
    source TEXT,
    date TEXT
)
""")

#Таблица рекламных размещений
cursor.execute("""
CREATE TABLE IF NOT EXISTS placements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placement_id TEXT UNIQUE,
    platform TEXT,
    post_name TEXT,
    cost REAL,
    date TEXT
)
""")

#Таблица покупок

cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    placement_id TEXT,
    amount REAL,
    course TEXT,
    date TEXT
)
""")

conn.commit()


# Кнопка

menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Оставить заявку",
                callback_data="request"
            )
        ]
    ]
)
# /start

@dp.message(CommandStart())
async def start_handler(message: Message):

    # Получаем параметр tracking-ссылки
    # Например:
    # /start instagram_post_1

    args = message.text.split()

    if len(args) > 1:
        source = args[1]
    else:
        source = "unknown"

    print("SOURCE:", source)

    # Сохраняем пользователя

    cursor.execute("""
    INSERT INTO users (user_id, username, source, date)
    VALUES (?, ?, ?, ?)
    """,
    (
        message.from_user.id,
        message.from_user.username,
        source,
        str(datetime.now())
    ))

    conn.commit()

    # Сохраняем событие start

    cursor.execute("""
    INSERT INTO events (user_id, event, source, date)
    VALUES (?, ?, ?, ?)
    """,
    (
        message.from_user.id,
        "start",
        source,
        str(datetime.now())
    ))

    conn.commit()

    # Показываем меню

    await message.answer(
        f"Привет! 🚀\n\n"
        f"Ты пришёл из источника: {source}\n\n"
        f"Что хочешь сделать?",
        reply_markup=menu
    )

# Нажатие кнопки

@dp.callback_query()
async def button_click(callback: CallbackQuery, state: FSMContext):

    user_id = callback.from_user.id

    # Находим источник пользователя

    cursor.execute("""
    SELECT source
    FROM users
    WHERE user_id = ?
    ORDER BY date DESC
    LIMIT 1
    """,
    (user_id,))
    result = cursor.fetchone()


    if result:
        source = result[0]
    else:
        source = "unknown"

    print("USER:", user_id)
    print("SOURCE:", source)
    print("BUTTON:", callback.data)

    # Определяем событие

    if callback.data == "request":
        event = "click_request"
        text = "Хорошо! 📩\n\nКак вас зовут?"
        await callback.answer()
        await callback.message.answer(text)
        await state.set_state(LeadForm.waiting_for_name)

        return

    else:
        event = "unknown"
        text = "Неизвестное действие."

    # Записываем событие

    cursor.execute("""
    INSERT INTO events (user_id, event, source, date)
    VALUES (?, ?, ?, ?)
    """,
    (
        user_id,
        event,
        source,
        str(datetime.now())
    ))

    conn.commit()
    # Убираем "часики" с кнопки
    await callback.answer()
    # Отправляем соответствующий текст
    await callback.message.answer(text)

# Получаем имя

@dp.message(LeadForm.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    name = message.text
    # Сохраняем имя во временное состояние FSM
    await state.update_data(name=name)
    await state.set_state(LeadForm.waiting_for_contact)
    await message.answer(
        f"Приятно познакомиться, {name}! 👋\n\n"
        "Теперь напишите ваш контакт."
    )

@dp.message(LeadForm.waiting_for_contact)
async def get_contact(message: Message, state: FSMContext):

    contact = message.text

    # Забираем имя, которое сохранили раньше
    data = await state.get_data()
    name = data["name"]

    # Получаем источник пользователя
    cursor.execute("""
    SELECT source
    FROM users
    WHERE user_id = ?
    ORDER BY date DESC
    LIMIT 1
    """,
    (message.from_user.id,))

    result = cursor.fetchone()

    if result:
        source = result[0]
    else:
        source = "unknown"

    # Сохраняем лида в базу
    cursor.execute("""
    INSERT INTO leads (user_id, name, contact, source, date)
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        message.from_user.id,
        name,
        contact,
        source,
        str(datetime.now())
    ))

    conn.commit()

    await message.answer(
        "Готово! ✅\n\n"
        "Ваша заявка сохранена."
    )
    # Завершаем состояние
    await state.clear()

# Запуск
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())