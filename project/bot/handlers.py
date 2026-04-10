import aiohttp
from aiogram import Router, types
from aiogram.types import Message

from core.config import settings

router = Router()


@router.message(lambda msg: msg.photo)
async def handle_photos(message: Message, album: list[Message] | None = None):
    """
    Обрабатывает одиночные фото и альбомы.
    Отправляет их в FastAPI для создания галереи.
    """

    chat_id = message.chat.id

    # Если это альбом — используем все фото из альбома
    if album:
        photos = []
        for msg in album:
            photos.extend(msg.photo)
    else:
        photos = message.photo

    # Получаем ссылки на файлы Telegram
    file_urls = []
    for p in photos:
        file = await message.bot.get_file(p.file_id)
        file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"
        file_urls.append((file_url, file.file_path.split("/")[-1]))

    # Формируем multipart form-data
    form = aiohttp.FormData()
    form.add_field("chat_id", str(chat_id))

    async with aiohttp.ClientSession() as session:
        # Скачиваем фото и добавляем в форму
        for url, filename in file_urls:
            async with session.get(url) as resp:
                content = await resp.read()

                form.add_field(
                    "files",
                    content,
                    filename=filename,
                    content_type="image/jpeg"
                )

        # Убираем лишний слэш в BASE_URL
        base = settings.BASE_URL.rstrip("/")
        upload_url = f"{base}/gallery/upload"

        # Отправляем в FastAPI
        async with session.post(upload_url, data=form) as resp:
            if resp.status != 200:
                text = await resp.text()
                await message.answer(f"Ошибка сервера ({resp.status}):\n{text}")
                return

            try:
                data = await resp.json()
            except Exception:
                text = await resp.text()
                await message.answer(f"Ошибка: сервер вернул не JSON:\n{text}")
                return

    # Проверяем, что сервер вернул ссылку
    if "url" not in data:
        await message.answer(f"Ошибка: сервер не вернул ссылку.\nОтвет: {data}")
        return

    # Всё успешно
    await message.answer(f"Ваша галерея готова:\n{data['url']}")
