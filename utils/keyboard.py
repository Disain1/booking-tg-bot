import utils.status as status

from aiogram import types
from utils.database import Database
from utils.functions import getFreePlaceNumbers


def bookButtonKeyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Забронировать место", callback_data="book_place"))

    return keyboard


def unbookButtonKeyboard(row: int, place: int):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Отменить бронь 🚫", callback_data=f"unbook_place_{row}_{place}"))

    return keyboard

def fromPetrsuKeyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text="Да", callback_data="yes"),
        types.InlineKeyboardButton(text="Нет", callback_data="no"),
    )

    return keyboard


def placesKeyboard(database: Database, row: int):
    keyboard = types.InlineKeyboardMarkup()

    result = database.getAll("SELECT place, status FROM places WHERE row = ?", [row])
    for place, s in result:
        s = str(s).replace(f"{status.FREE}", "🟢").replace(f"{status.BOOKED}", "🟡").replace(f"{status.OCCUPIED}", "🔴")
        keyboard.insert(types.InlineKeyboardButton(text=f"Место {place} {s}", callback_data=f"{row}_{place}"))

    keyboard.row(types.InlineKeyboardButton(text="◀️ К выбору ряда", callback_data="back"))

    return keyboard


def rowsKeyboard(database: Database):
    keyboard = types.InlineKeyboardMarkup()

    for row, fp in getFreePlaceNumbers(database):
        keyboard.insert(types.InlineKeyboardButton(text=f"Ряд {row} ({fp})", callback_data=f"{row}"))
    
    return keyboard


def adminKeyboard(database: Database):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.row("🚫 Убрать бронь")
    keyboard.row("🎟 Повторно отправить билет")
    keyboard.row("📑 Excel файл мест")
    keyboard.row("📑 Excel файл пользователей")
    keyboard.row("🚪 Выйти")
    
    return keyboard