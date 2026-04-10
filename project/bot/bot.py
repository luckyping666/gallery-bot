from aiogram import Bot, Dispatcher
from core.config import settings

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
