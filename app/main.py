import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import gallery_router
from app.bot.bot import bot, dp
from app.bot.handlers import router as bot_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Современный способ запуска фоновых задач (вместо on_event).
    Здесь мы запускаем Telegram-бота в режиме polling.
    """
    dp.include_router(bot_router)

    # Запускаем polling в фоне
    polling_task = asyncio.create_task(dp.start_polling(bot))

    yield  # приложение работает

    # Корректно завершаем polling при остановке FastAPI
    polling_task.cancel()
    await bot.session.close()


app = FastAPI(lifespan=lifespan)

# Подключаем статику
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключаем API
app.include_router(gallery_router)
