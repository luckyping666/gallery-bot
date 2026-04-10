from core.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
