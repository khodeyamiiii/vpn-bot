
import os
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
from handlers import register_all_handlers

load_dotenv()
BOT_TOKEN = "7991421382:AAHcUrn-fEHuuHJABCn5gmdYQF4npijJJ6U"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

register_all_handlers(dp, bot)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
