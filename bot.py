import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import API_TOKEN
from authors import register_authors_handlers, send_team_menu
from feedback import register_feedback_handlers
from premium import register_premium_handlers

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

register_authors_handlers(dp, bot)
register_feedback_handlers(dp, bot)
register_premium_handlers(dp, bot)

async def main():
    # запуск меню "Команда и Партнёры"
    await send_team_menu()
    # запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
