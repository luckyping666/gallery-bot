from fastapi import APIRouter, UploadFile, Form, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.deps import get_db
from services.gallery_service import GalleryService
from repositories.gallery_repository import GalleryRepository

import os

# /app/project/api → /app/project
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# /app/project/templates
TEMPLATES_DIR = os.path.join(PROJECT_DIR, "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

print("PROJECT ROOT:", PROJECT_DIR)
print("TEMPLATES_DIR:", TEMPLATES_DIR)
print("TEMPLATES EXISTS:", os.path.exists(TEMPLATES_DIR))

print("ROOT CONTENT:", os.listdir(PROJECT_DIR))
print("API CONTENT:", os.listdir(os.path.join(PROJECT_DIR, "api")))
print("TEMPLATES CONTENT:", os.listdir(TEMPLATES_DIR))



templates = Jinja2Templates(directory=TEMPLATES_DIR)
router = APIRouter(prefix="/gallery", tags=["Gallery"])

print("TEMPLATES_DIR:", TEMPLATES_DIR)
print("FILES:", os.listdir(TEMPLATES_DIR))


@router.post("/upload")
async def upload_gallery(
    chat_id: int = Form(...),
    files: list[UploadFile] = None,
    session: AsyncSession = Depends(get_db)
):
    if not files:
        return {"error": "No files provided"}

    file_bytes = [await f.read() for f in files]
    filenames = [f.filename for f in files]

    service = GalleryService(GalleryRepository())

    hash_id = await service.create_gallery(
        session=session,
        chat_id=chat_id,
        files=file_bytes,
        filenames=filenames
    )

    # Абсолютная ссылка
    return {
        "url": f"{settings.BASE_URL.rstrip('/')}/gallery/view/{hash_id}"
    }



@router.get("/view/{hash_id}", response_class=HTMLResponse)
async def view_gallery(request: Request, hash_id: str):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_DIR = os.path.join(os.path.dirname(BASE_DIR), "static")
    folder = os.path.join(STATIC_DIR, "images", hash_id)

    if not os.path.exists(folder):
        return HTMLResponse("Gallery not found", status_code=404)

    images = [
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
    ]

    return templates.TemplateResponse(
        "gallery.html",
        {
            "request": request,
            "images": images,
            "hash_id": hash_id
        }
    )
