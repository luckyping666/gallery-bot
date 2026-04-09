import hashlib
import os
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.gallery_repository import GalleryRepository
from app.core.config import settings


class GalleryService:
    """
    Сервис для работы с галереями.

    Содержит бизнес-логику:
    - генерация уникального hash
    - сохранение изображений
    - создание галереи через репозиторий
    """

    def __init__(self, repository: GalleryRepository):
        self.repository = repository

    @staticmethod
    def generate_hash(chat_id: int, counter: int) -> str:
        """
        Генерирует уникальный хэш галереи на основе chat_id и порядкового номера.
        """
        raw = f"{chat_id}:{counter}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    async def save_images(self, hash_id: str, files: List[bytes], filenames: List[str]) -> None:
        """
        Сохраняет изображения в файловую систему.

        Args:
            hash_id (str): Уникальный идентификатор галереи.
            files (List[bytes]): Список бинарных данных изображений.
            filenames (List[str]): Имена файлов.
        """
        folder = f"app/static/images/{hash_id}"
        os.makedirs(folder, exist_ok=True)

        for file_bytes, filename in zip(files, filenames):
            path = f"{folder}/{filename}"
            with open(path, "wb") as f:
                f.write(file_bytes)

    async def create_gallery(
        self,
        session: AsyncSession,
        chat_id: int,
        files: List[bytes],
        filenames: List[str]
    ) -> str:
        """
        Создаёт галерею:
        - считает порядковый номер
        - генерирует hash
        - сохраняет изображения
        - создаёт запись в БД

        Returns:
            str: hash галереи
        """
        # 1. Считаем номер галереи
        counter = await self.repository.count_by_chat(session, chat_id) + 1

        # 2. Генерируем уникальный hash
        hash_id = self.generate_hash(chat_id, counter)

        # 3. Сохраняем изображения
        await self.save_images(hash_id, files, filenames)

        # 4. Создаём запись в БД
        await self.repository.create(
            session=session,
            chat_id=chat_id,
            counter=counter,
            hash_id=hash_id
        )

        return hash_id
