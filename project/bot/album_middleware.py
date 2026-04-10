import asyncio
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Dict, List, Any


class AlbumMiddleware(BaseMiddleware):
    def __init__(self, delay: float = 0.3):
        super().__init__()
        self.delay = delay
        self.albums: Dict[str, List[Message]] = {}

    async def __call__(self, handler, event: Message, data: Dict[str, Any]):
        # Если это не альбом — просто передаём дальше
        if not event.media_group_id:
            return await handler(event, data)

        group_id = event.media_group_id

        # Первая часть альбома
        if group_id not in self.albums:
            self.albums[group_id] = [event]

            # Ждём, пока Telegram пришлёт остальные части
            await asyncio.sleep(self.delay)

            messages = self.albums.pop(group_id)
            data["album"] = messages
            return await handler(messages[-1], data)

        # Остальные части альбома
        self.albums[group_id].append(event)
