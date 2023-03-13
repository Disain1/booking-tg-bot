import os

import utils.keyboard as keyboard
import utils.database as database
import utils.functions as functions
import utils.strings as strings
import utils.states as states
import utils.status as status
import utils.ticket as ticket
import excel.excel as excel

from re import compile
from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN, DATABASE_PATH, ADMIN_IDS


bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
database = database.Database(DATABASE_PATH)


@dp.message_handler(commands='start')
async def sendWelcome(message: types.Message):
    user_id = message.from_user.id

    result = database.getOne("SELECT user_id FROM states WHERE user_id = ?", [user_id])

    if result is None:
        await message.answer(strings.START_MESSAGE, reply_markup=keyboard.bookButtonKeyboard())
        database.commit("INSERT INTO states VALUES(?, ?)", [user_id, states.START])
        database.commit("INSERT INTO users (user_id) VALUES(?)", [user_id])
        return
    

@dp.message_handler(commands='admin')
async def admin(message: types.Message):
    user_id = message.from_user.id

    if user_id not in ADMIN_IDS:
        return
    
    functions.setUserState(database, user_id, states.ADMIN_MENU)
    await message.answer("Меню администраторов", reply_markup=keyboard.adminKeyboard(database))


@dp.message_handler(lambda message: functions.getUserState(database, message.from_user.id) is states.ADMIN_MENU)
async def adminMenu(message: types.Message):
    user_id = message.from_user.id

    if message.text == "📑 Excel файл мест":
        file = excel.getPlacesFile(database)
        await message.answer_document(file)
    elif message.text == "📑 Excel файл пользователей":
        file = excel.getUsersFile(database)
        await message.answer_document(file)
    elif message.text == "🚫 Убрать бронь":
        await message.answer("Введите через пробел ряд и место, которое нужно убрать: ")
    elif message.text == "🚪 Выйти":
        await message.answer("Выход... 🚪", reply_markup=types.ReplyKeyboardRemove())
        functions.setUserState(database, user_id, states.SELECT_ROW)
    
        await message.answer_photo(
            open("images/rows.png", "rb"),
            caption=strings.SELECT_ROW,
            reply_markup=keyboard.rowsKeyboard(database)
        )
    else:
        try:
            row, place = message.text.split()
            functions.removeBooking(database, int(row), int(place))
            await message.answer("Бронь убрана ✅")
        except Exception:
            pass


@dp.callback_query_handler(lambda query: (query.data == "book_place"))
async def bookPlace(query: types.CallbackQuery):
    user_id = query.from_user.id

    await query.message.delete()
    await query.message.answer(strings.SEND_NAME)
    functions.setUserState(database, user_id, states.SEND_NAME)


@dp.callback_query_handler(lambda query: query.data.startswith("unbook_place"))
async def bookPlace(query: types.CallbackQuery):
    user_id = query.from_user.id
    row, place = query.data.split("_")[2:4]

    await query.message.unpin()
    
    functions.removeBooking(database, row, place)
    functions.setUserState(database, user_id, states.SELECT_ROW)

    await query.message.edit_media(types.InputMediaPhoto(open("images/rows.png", "rb")))
    await query.message.edit_caption(caption=strings.SELECT_ROW, reply_markup=keyboard.rowsKeyboard(database))


@dp.message_handler(lambda message: functions.getUserState(database, message.from_user.id) is states.SEND_NAME)
async def sendName(message: types.Message):
    user_id = message.from_user.id

    pattern = compile("^[А-Яа-яЁё]+\s+[А-Яа-яЁё]+$")
    if not pattern.match(message.text):
        await message.answer(strings.NAME_ERROR)
    else:
        name = " ".join([x.capitalize() for x in message.text.split()])
        database.commit("UPDATE users SET name = ? WHERE user_id = ?", [name, user_id])
        await message.answer(strings.FROM_PETRSU, reply_markup=keyboard.fromPetrsuKeyboard())
        functions.setUserState(database, user_id, states.FROM_PERTSU)


@dp.callback_query_handler(lambda query: functions.getUserState(database, query.from_user.id) is states.FROM_PERTSU)
async def fromPetrsu(query: types.CallbackQuery):
    user_id = query.from_user.id

    if query.data == "yes":
        database.commit("UPDATE users SET from_petrsu = ? WHERE user_id = ?", [True, user_id])
    else:
        database.commit("UPDATE users SET from_petrsu = ? WHERE user_id = ?", [False, user_id])

    await query.message.delete()
    functions.setUserState(database, user_id, states.SEND_VK_ID)
    await query.message.answer(strings.SEND_VK_ID)


@dp.message_handler(lambda message: functions.getUserState(database, message.from_user.id) is states.SEND_VK_ID)
async def sendVkId(message: types.Message):
    user_id = message.from_user.id
    
    database.commit("UPDATE users SET vk_id = ? WHERE user_id = ?", [message.text, user_id])
    functions.setUserState(database, user_id, states.SELECT_ROW)
    
    await message.answer_photo(
        open("images/rows.png", "rb"),
        caption=strings.REGISTRATION_SUCCSESS,
        reply_markup=keyboard.rowsKeyboard(database)
        )
    

@dp.callback_query_handler(lambda query: query.data == "back")
async def back(query: types.CallbackQuery):
    user_id = query.from_user.id
    
    functions.setUserState(database, user_id, states.SELECT_ROW)
    await query.message.edit_media(types.InputMediaPhoto(open("images/rows.png", "rb")))
    await query.message.edit_caption(caption=strings.SELECT_ROW, reply_markup=keyboard.rowsKeyboard(database))


@dp.callback_query_handler(lambda query: functions.getUserState(database, query.from_user.id) is states.SELECT_ROW)
async def selectRow(query: types.CallbackQuery):
    user_id = query.from_user.id

    if not query.data.isnumeric(): return
    row = query.data

    functions.setUserState(database, user_id, states.SELECT_PLACE)
    await query.message.edit_media(types.InputMediaPhoto(open(f"images/row{row}.png", "rb")))
    await query.message.edit_caption(strings.SELECT_PLACE.format(row), reply_markup=keyboard.placesKeyboard(database, row))


@dp.callback_query_handler(lambda query: functions.getUserState(database, query.from_user.id) is states.SELECT_PLACE)
async def place(query: types.CallbackQuery):
    user_id = query.from_user.id
    row, place = query.data.split("_")

    result = database.getOne("SELECT status FROM places WHERE row = ? AND place = ?", [row, place])

    if result is None: return
    
    if result[0] != 0:
        await query.answer("Это место уже успели забронировать, попробуй выбрать другое!", show_alert=True)
        return
    
    result = database.getOne("SELECT user_id FROM places WHERE user_id = ?", [user_id])

    if result != None:
        await query.answer("Ты уже забронировал место, если хочешь выбрать другое - отмени старую бронь", show_alert=True)
        return

    functions.addBooking(database, user_id, row, place, status.BOOKED)
    functions.setUserState(database, user_id, states.TICKET)

    file = ticket.getTicketImage(row, place)
    
    await query.message.delete()

    message = await query.message.answer_photo(
        file,
        f"<b>Место: {place}\nРяд: {row}</b>\n\nВот твой билет, не потеряй 🤭",
        reply_markup=keyboard.unbookButtonKeyboard(row, place)
        )
    
    await message.pin()
    
    os.remove(file.name)


if __name__ == '__main__':
    functions.initDatabase(database)
    executor.start_polling(dp, skip_updates=True)