
import os
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
from handlers import register_all_handlers

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

register_all_handlers(dp, bot)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
