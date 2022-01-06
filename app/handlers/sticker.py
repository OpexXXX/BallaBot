from aiogram import Dispatcher, types
import random
import string

from shutil import copy2


from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.ballistic.shoot import main as make_sticker
from aiogram.types import InputFile, sticker

from app.dbprovider import SQLiteProvider
class MakeSticker(StatesGroup):
    waiting_for_height =  State()
    waiting_for_len = State()
    waiting_for_click_on_turn = State()
    waiting_for_file = State()
    
    make_file = State()



async def sticker_start(message: types.Message, state: FSMContext):
    
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username

    if not SQLiteProvider.exists_user(user_id):
        SQLiteProvider.add_to_db(user_id, first_name, last_name, username)
        await message.answer("https://youtu.be/r2YRaNnoxaA")
        await message.answer("opex618@gmail.com")
        print("New user")
    else:
        turr_data = SQLiteProvider.get_user_turrets(user_id) 
        for row in turr_data:
            if row==None:
                await message.answer("Введите высоту барабана, мм:")
                await MakeSticker.waiting_for_height.set()
                return
        await state.update_data(turret_height=turr_data[0])
        await state.update_data(turret_len=turr_data[1])
        await state.update_data(click_on_turn=turr_data[2])

        await message.answer(f'Сохраненные настройки: \nвысота барабана {turr_data[0]}мм,\nдлинна наклейки {turr_data[1]}мм, \n{turr_data[2]} щелчков на 1 оборот барабана.')
        await message.answer("Поделитесь таблицей поправок из приложения 'Стрелок'")
        await MakeSticker.waiting_for_file.set()
        return

    await message.answer("Введите высоту барабана, мм:")
    await MakeSticker.waiting_for_height.set()


async def wait_click_on_turn(message: types.Message, state: FSMContext):
    num = 0
    flag = False
    try:
        num=int(message.text)
        flag =  True
    except ValueError:
        flag = False

    if flag==False:
        await message.answer("Введите количество щелчков на один оборот:")
        return
    if flag and num>200:
        await message.answer("Многовато.")
        await message.answer("Введите количество щелчков на один оборот:")
        return
    if flag and num<10:
        await message.answer("Маловато.")
        await message.answer("Введите количество щелчков на один оборот:")
        return

    await state.update_data(click_on_turn=num)

    user_data = await state.get_data()
    user_id = message.from_user.id
    turret_height =user_data['turret_height']
    turret_len=user_data['turret_len'] 
    click_on_turn=user_data['click_on_turn']
    SQLiteProvider.update_db_turr(user_id,turret_height,turret_len,click_on_turn)

    await message.answer("Поделитесь таблицей поправок из приложения 'Стрелок'")
    await MakeSticker.waiting_for_file.set()

async def wait_turret_height(message: types.Message, state: FSMContext):
    num = 0.0
    flag = False
    try:
        num=float(message.text.replace(',','.'))
        flag =  True
    except ValueError:
        flag = False

    if flag==False:
        await message.answer("Введите высоту барабана, мм:")
        return
    if flag and num>30.0:
        await message.answer("Слишком высоко.")
        await message.answer("Введите высоту барабана, мм:")
        return
    if flag and num<3.0:
        await message.answer("Слишком низко.")
        await message.answer("Введите высоту барабана, мм:")
        return
    await state.update_data(turret_height=num)
    await message.answer("Введите длинну окружности барабана или длинну наклейки, мм:")
    await MakeSticker.waiting_for_len.set()

async def wait_turret_len(message: types.Message,  state: FSMContext):
    num = 0.0
    flag = False
    try:
        num=float(message.text.replace(',','.'))
        flag =  True
    except ValueError:
        flag = False

    if flag==False:
        await message.answer("Введите длинну окружности барабана или длинну наклейки, мм:")
        return
    if flag and num>200.0:
        await message.answer("Длинновато.")
        await message.answer("Введите длинну окружности барабана или длинну наклейки, мм:")
        return
    if flag and num<20.0:
        await message.answer("Коротковато.")
        await message.answer("Введите длинну окружности барабана или длинну наклейки, мм:")
        return
    await state.update_data(turret_len=num)
    await message.answer("Введите количество щелчков на один оборот:")
  
    await MakeSticker.waiting_for_click_on_turn.set()


async def recive_file(message: types.Message, state: FSMContext):
    file_name = message.document.file_name 
    
    if file_name != "table.csv" and file_name != "table.htm":
        await message.answer("Пожалуйста, отправте фаилы table.csv table.htm.")
        img = InputFile("img/3.jpg")
        await message.answer_photo(img)
        return
    if file_name == "table.csv":
        file_path = await message.document.download()
        await state.update_data(csv_file=file_path.name)
        await state.update_data(csv_file_resive=True)
    if file_name == "table.htm":
        file_path = await message.document.download()
        await state.update_data(htm_file=file_path.name)
        await state.update_data(htm_file_resive=True)
    user_data = await state.get_data()

    if ('csv_file_resive'in user_data and user_data['csv_file_resive']  )and ('htm_file_resive'in user_data and user_data['htm_file_resive']):
        #await message.answer("Файлы получены")
        SQLiteProvider.increment_generate(message.from_user.id)
        randName = ''.join([random.choice(string.ascii_lowercase) for i in range(16)])
        pdf_file = 'tmp/'+str(message.from_user.id)+randName+".pdf"

        copy2(user_data['csv_file'],'tmp/'+ str(message.from_user.id)+randName+'.csv')
        copy2(user_data['htm_file'],'tmp/'+ str(message.from_user.id)+randName+'.htm')
        try:
            warning_list,cartrige_name = make_sticker(user_data['csv_file'],user_data['htm_file'],pdf_file,sticker_len_mm=user_data['turret_len'],stickerHeight_mm=user_data['turret_height'],click_on_turn=user_data['click_on_turn'])
            doc = InputFile(pdf_file,cartrige_name+".pdf")
            for row in warning_list:
                await message.answer(row)
            await message.answer_document(doc)
        except Exception as e:
           await message.answer(f"Что то пошло не так.\n{e}")

        await state.update_data(csv_file_resive=False)
        await state.update_data(htm_file_resive=False)
        
        
        #await message.answer("Жду table.csv table.htm")
        #await MakeSticker.waiting_for_file.set()
        

async def cmd_set(message: types.Message, state: FSMContext):
    await message.answer("Введите высоту барабана, мм:")
    await MakeSticker.waiting_for_height.set()

async def cmd_help(message: types.Message, state: FSMContext):
    await message.answer("https://youtu.be/r2YRaNnoxaA")
    await message.answer("opex618@gmail.com")

def register_handlers_sticker(dp: Dispatcher):
    dp.register_message_handler(sticker_start, commands="start", state="*")
    dp.register_message_handler(cmd_set, commands="set", state="*")
    dp.register_message_handler(cmd_help, commands="help", state="*")
    dp.register_message_handler(wait_turret_len, state=MakeSticker.waiting_for_len)
    dp.register_message_handler(wait_turret_height, state=MakeSticker.waiting_for_height)
    dp.register_message_handler(wait_click_on_turn, state=MakeSticker.waiting_for_click_on_turn)
    dp.register_message_handler(recive_file,content_types=[types.ContentType.DOCUMENT], state=MakeSticker.waiting_for_file)
   
