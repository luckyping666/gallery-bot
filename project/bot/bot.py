from aiogram import Bot, Dispatcher
from core.config import settings
from bot.album_middleware import AlbumMiddleware

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
dp.message.middleware(AlbumMiddleware())
