from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter
from app.dbprovider import SQLiteProvider 

async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())

  

# Просто функция, которая доступна только администратору,
# чей ID указан в файле конфигурации.
async def secret_command(message: types.Message):
    count_user = SQLiteProvider.number_of_users()
    await message.answer("Пользователей в базе: "+str(count_user)+".")



def register_handlers_common(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
    dp.register_message_handler(secret_command, IDFilter(user_id=admin_id), commands="members", state="*")
