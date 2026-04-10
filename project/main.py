import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.gallery_router import router as gallery_router
from bot.bot import bot, dp
from bot.handlers import router as bot_router

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
STATIC_DIR = os.path.join(BASE_DIR, "static")

sys.path.insert(0, BASE_DIR)
sys.path.insert(0, PARENT_DIR)

# async SQLAlchemy
from core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Создаём таблицы async‑способом
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Подключаем роутеры бота
    dp.include_router(bot_router)

    # 3. Запускаем polling
    polling_task = asyncio.create_task(dp.start_polling(bot))

    yield

    # 4. Останавливаем polling
    polling_task.cancel()
    await bot.session.close()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(gallery_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=80)
