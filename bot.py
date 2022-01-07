#!venv/bin/python
import asyncio
import logging
from dotenv import dotenv_values

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.handlers.sticker import register_handlers_sticker
from app.handlers.common import register_handlers_common
from app.dbprovider import SQLiteProvider

config = dotenv_values(".env")
logger = logging.getLogger(__name__)
iobot = Bot(token=config["BOT_TOKEN"])

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Старт"),
        BotCommand(command="/help", description="Помощь"),
        BotCommand(command="/set", description="Сброс значений"),
        BotCommand(command="/cancel", description="Отменa")
    ]
    await bot.set_my_commands(commands)


async def main():
    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    # Парсинг файла конфигурации
    

    # Объявление и инициализация объектов бота и диспетчера
   
    dp = Dispatcher(iobot, storage=MemoryStorage())

    SQLiteProvider.connect("db.sqlite")


    # Регистрация хэндлеров
    register_handlers_common(dp, config["ADMIN_ID"])
    register_handlers_sticker(dp)

    # Установка команд бота
    await set_commands(iobot)

    # Запуск поллинга
    # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
