import aiohttp
from aiogram import Router, types
from aiogram.types import Message

from app.core.config import settings

router = Router()


@router.message(lambda msg: msg.photo)
async def handle_photos(message: Message):
    """
    Обрабатывает входящие фотографии от пользователя.
    Отправляет их в FastAPI для создания галереи.
    """
    chat_id = message.chat.id
    photos = message.photo

    # Получаем ссылки на файлы Telegram
    file_urls = []
    for p in photos:
        file = await message.bot.get_file(p.file_id)
        file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"
        file_urls.append(file_url)

    # Формируем multipart form-data
    form = aiohttp.FormData()
    form.add_field("chat_id", str(chat_id))

    async with aiohttp.ClientSession() as session:
        for url in file_urls:
            async with session.get(url) as resp:
                content = await resp.read()
                filename = url.split("/")[-1]

                form.add_field(
                    "files",
                    content,
                    filename=filename,
                    content_type="image/jpeg"
                )

        # Отправляем в FastAPI
        async with session.post(f"{settings.BASE_URL}/gallery/upload", data=form) as resp:
            data = await resp.json()

    await message.answer(f"Ваша галерея готова:\n{data['url']}")
