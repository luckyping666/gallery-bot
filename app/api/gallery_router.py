from fastapi import APIRouter, UploadFile, Form, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.services.gallery_service import GalleryService
from app.repositories.gallery_repository import GalleryRepository

import os


router = APIRouter(prefix="/gallery", tags=["Gallery"])
templates = Jinja2Templates(directory="app/templates")


@router.post("/upload")
async def upload_gallery(
    chat_id: int = Form(...),
    files: list[UploadFile] = None,
    session: AsyncSession = Depends(get_db)
):
    """
    Принимает изображения от Telegram-бота, создаёт галерею и возвращает ссылку.
    """
    if not files:
        return {"error": "No files provided"}

    # Читаем файлы в память
    file_bytes = [await f.read() for f in files]
    filenames = [f.filename for f in files]

    # Инициализируем сервис
    service = GalleryService(GalleryRepository())

    # Создаём галерею
    hash_id = await service.create_gallery(
        session=session,
        chat_id=chat_id,
        files=file_bytes,
        filenames=filenames
    )

    return {"url": f"/gallery/view/{hash_id}"}


@router.get("/view/{hash_id}", response_class=HTMLResponse)
async def view_gallery(hash_id: str, request: Request):
    """
    Отображает HTML-галерею по её уникальному hash_id.
    """
    folder = f"app/static/images/{hash_id}"

    if not os.path.exists(folder):
        return HTMLResponse("Gallery not found", status_code=404)

    images = os.listdir(folder)

    return templates.TemplateResponse(
        "gallery.html",
        {
            "request": request,
            "images": images,
            "hash_id": hash_id
        }
    )
