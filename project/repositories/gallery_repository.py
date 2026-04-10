from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.gallery import Gallery


class GalleryRepository:
    """
    Репозиторий для работы с моделью Gallery.

    Инкапсулирует всю логику взаимодействия с базой данных
    для сущности Gallery (создание, получение, выборки).
    """

    async def create(
        self,
        session: AsyncSession,
        chat_id: int,
        counter: int,
        hash_id: str
    ) -> Gallery:
        """
        Создаёт новую запись галереи в базе данных.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            chat_id (int): Telegram chat_id пользователя.
            counter (int): Порядковый номер галереи пользователя.
            hash_id (str): Уникальный хэш галереи.

        Returns:
            Gallery: Созданный объект галереи.
        """
        gallery = Gallery(
            chat_id=chat_id,
            counter=counter,
            hash_id=hash_id
        )

        session.add(gallery)
        await session.commit()
        await session.refresh(gallery)

        return gallery

    async def get_by_hash(
        self,
        session: AsyncSession,
        hash_id: str
    ) -> Optional[Gallery]:
        """
        Получает галерею по её уникальному хэшу.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            hash_id (str): Уникальный идентификатор галереи.

        Returns:
            Gallery | None: Найденная галерея или None.
        """
        stmt = select(Gallery).where(Gallery.hash_id == hash_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_chat(
        self,
        session: AsyncSession,
        chat_id: int
    ) -> int:
        """
        Возвращает количество галерей, созданных пользователем.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            chat_id (int): Telegram chat_id пользователя.

        Returns:
            int: Количество галерей.
        """
        stmt = select(Gallery).where(Gallery.chat_id == chat_id)
        result = await session.execute(stmt)
        return len(result.scalars().all())

    async def list_by_chat(
        self,
        session: AsyncSession,
        chat_id: int
    ) -> list[Gallery]:
        """
        Возвращает список всех галерей пользователя.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            chat_id (int): Telegram chat_id пользователя.

        Returns:
            list[Gallery]: Список галерей.
        """
        stmt = (
            select(Gallery)
            .where(Gallery.chat_id == chat_id)
            .order_by(Gallery.counter.asc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
