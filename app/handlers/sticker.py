from aiogram import Dispatcher, types
import random
import string
from datetime import datetime
from shutil import copy2


from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.ballistic.shoot import main as make_sticker
from aiogram.types import InputFile, sticker
from app.dbprovider import SQLiteProvider
#from bot import iobot
#from bot import config
class MakeSticker(StatesGroup):
    waiting_for_height =  State()
    waiting_for_len = State()
    waiting_for_len_of_step = State()
    waiting_for_click_on_turn = State()
    waiting_for_file = State()
    waiting_for_turret_step = State()
    make_file = State()

    
async def make_pdf(user_data,message):
    
    randName = ''.join([random.choice(string.ascii_lowercase) for i in range(16)])
    pdf_file = 'tmp/'+str(message.from_user.id)+randName+".pdf"
    copy2(user_data['csv_file'],'tmp/'+ str(message.from_user.id)+randName+'.csv')
    copy2(user_data['htm_file'],'tmp/'+ str(message.from_user.id)+randName+'.htm')
    current_datetime = datetime.now()
    try:
        warning_list,cartrige_name = make_sticker(user_data['csv_file'],user_data['htm_file'],pdf_file,sticker_len_mm=user_data['turret_len'],stickerHeight_mm=user_data['turret_height'],click_on_turn=user_data['click_on_turn'], turrets_step=user_data['turrets_step'])
        doc = InputFile(pdf_file,"Шаг "+str(round(user_data['turrets_step'],2)).format("{1:3.1f}")+"м "+cartrige_name+ ".pdf")
        for row in warning_list:
            await message.answer(row)
        await message.answer_document(doc)
        SQLiteProvider.increment_generate(message.from_user.id)
        SQLiteProvider.add_generate_message(message.from_user.id, str(current_datetime) + ": Шаг "+str(round(user_data['turrets_step'],2)).format("{1:3.1f}")+"м "+cartrige_name+ " " +  pdf_file)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["100", "50", "25", "12.5","10","5",("Изменить длинну " + str(user_data['turret_len']).format("{1:5.1f}")+"мм")]
        keyboard.add(*buttons)
        await message.answer("Введите шаг или скинте новые файлы.", reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Что то пошло не так.\n{e}",reply_markup=types.ReplyKeyboardRemove())
        SQLiteProvider.add_generate_message(message.from_user.id,str(current_datetime) + ": Шаг "+str(round(user_data['turrets_step'],2)).format("{1:3.1f}")+"м "+ f"{e}" +  pdf_file,succes=False)
        
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
                await message.answer("Введите высоту барабана, мм:",reply_markup=types.ReplyKeyboardRemove())
                await MakeSticker.waiting_for_height.set()
                return
        await state.update_data(turret_height=turr_data[0])
        await state.update_data(turret_len=turr_data[1])
        await state.update_data(click_on_turn=turr_data[2])

        await message.answer(f'Сохраненные настройки: \nвысота барабана {turr_data[0]}мм,\nдлинна наклейки {turr_data[1]}мм, \n{turr_data[2]} щелчков на 1 оборот барабана.',reply_markup=types.ReplyKeyboardRemove())
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
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["100", "50", "25", "12.5","10","5",("Изменить длинну " + str(user_data['turret_len']).format("{1:5.1f}")+"мм")]
        keyboard.add(*buttons)
        await message.answer("Введите шаг градуировки барабана:", reply_markup=keyboard)
        await MakeSticker.waiting_for_turret_step.set()

        await state.update_data(csv_file_resive=False)
        await state.update_data(htm_file_resive=False)
        
        #await message.answer("Жду table.csv table.htm")
        #await MakeSticker.waiting_for_file.set()

async def wait_turret_len_of_step(message: types.Message,  state: FSMContext):
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
    user_data = await state.get_data()
    user_id = message.from_user.id
    turret_height =user_data['turret_height']
    turret_len=user_data['turret_len'] 
    click_on_turn=user_data['click_on_turn']
    SQLiteProvider.update_db_turr(user_id,turret_height,turret_len,click_on_turn)

    if "turrets_step" in user_data.keys():
        await make_pdf(user_data,message)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["100", "50", "25", "12.5","10","5",("Изменить длинну " + str(user_data['turret_len']).format("{1:5.1f}")+"мм")]
        keyboard.add(*buttons)
        await message.answer("Введите шаг градуировки барабана:", reply_markup=keyboard)
    await MakeSticker.waiting_for_turret_step.set()

async def wait_turret_step(message: types.Message,  state: FSMContext):
    num = 0.0
    flag = False
    if "Изменить длинну" in message.text:
        await message.answer("Введите длинну окружности барабана или длинну наклейки, мм:",reply_markup=types.ReplyKeyboardRemove())
        await MakeSticker.waiting_for_len_of_step.set()
        return
    try:
        num=float(message.text.replace(',','.'))
        flag =  True
    except ValueError:
        flag = False

    if flag==False:
        
        return

    if  flag == False or num not in [100.0 , 50.0, 25.0, 12.5, 10.0, 5.0]:
        await message.answer("Выберите из списка")
        return
    await state.update_data(turrets_step=num)
    user_data = await state.get_data()
    await make_pdf(user_data,message)
        #await message.answer("Файлы получены")
    

    
    #await MakeSticker.waiting_for_file.set()
        

async def cmd_set(message: types.Message, state: FSMContext):
    await message.answer("Введите высоту барабана, мм:",reply_markup=types.ReplyKeyboardRemove())
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
    dp.register_message_handler(wait_turret_step, state=MakeSticker.waiting_for_turret_step)
    dp.register_message_handler(wait_turret_len_of_step, state=MakeSticker.waiting_for_len_of_step)
    dp.register_message_handler(recive_file,content_types=[types.ContentType.DOCUMENT], state=MakeSticker.waiting_for_file)
    dp.register_message_handler(recive_file,content_types=[types.ContentType.DOCUMENT], state=MakeSticker.waiting_for_turret_step)
   
