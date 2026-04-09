from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from app.core.database import Base

class Gallery(Base):
    __tablename__ = "galleries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    counter: Mapped[int] = mapped_column(Integer, nullable=False)
    hash_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
