import aiohttp
from aiogram import Router, types
from aiogram.types import Message

from core.config import settings

router = Router()


@router.message(lambda msg: msg.photo)
async def handle_photos(message: Message, album: list[Message] | None = None):
    chat_id = message.chat.id

    # Берём только ОДНО фото из каждого сообщения — самое большое
    if album:
        photos = [msg.photo[-1] for msg in album]
    else:
        photos = [message.photo[-1]]

    file_urls = []
    for p in photos:
        file = await message.bot.get_file(p.file_id)
        file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"
        file_urls.append((file_url, file.file_path.split("/")[-1]))

    form = aiohttp.FormData()
    form.add_field("chat_id", str(chat_id))

    async with aiohttp.ClientSession() as session:
        for url, filename in file_urls:
            async with session.get(url) as resp:
                content = await resp.read()
                form.add_field(
                    "files",
                    content,
                    filename=filename,
                    content_type="image/jpeg"
                )

        upload_url = f"{settings.BASE_URL.rstrip('/')}/gallery/upload"

        async with session.post(upload_url, data=form) as resp:
            data = await resp.json()

    await message.answer(f"Ваша галерея готова:\n{data['url']}")
