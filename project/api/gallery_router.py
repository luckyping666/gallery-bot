from fastapi import APIRouter, UploadFile, Form, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.deps import get_db
from services.gallery_service import GalleryService
from repositories.gallery_repository import GalleryRepository

import os

router = APIRouter(prefix="/gallery", tags=["Gallery"])


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

    return {
        "url": f"{settings.BASE_URL.rstrip('/')}/gallery/view/{hash_id}"
    }


from fastapi import APIRouter, UploadFile, Form, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.deps import get_db
from services.gallery_service import GalleryService
from repositories.gallery_repository import GalleryRepository

import os

router = APIRouter(prefix="/gallery", tags=["Gallery"])


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

    return {
        "url": f"{settings.BASE_URL.rstrip('/')}/gallery/view/{hash_id}"
    }


@router.get("/view/{hash_id}", response_class=HTMLResponse)
async def view_gallery(hash_id: str):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_DIR = os.path.join(os.path.dirname(BASE_DIR), "static")
    folder = os.path.join(STATIC_DIR, "images", hash_id)

    if not os.path.exists(folder):
        return HTMLResponse("Gallery not found", status_code=404)

    # Берём только файлы, исключаем папки
    images = [
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
    ]

    # Генерируем HTML для картинок
    images_html = "\n".join(
        f'<img src="/static/images/{hash_id}/{img}" alt="image" onclick="openLightbox(this.src)">'
        for img in images
    )

    # Полная HTML‑страница
    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Галерея</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>
            body {{
                margin: 0;
                padding: 0;
                background: #111;
                color: #fff;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}

            header {{
                padding: 20px;
                text-align: center;
                font-size: 24px;
                font-weight: 600;
                background: #000;
                border-bottom: 1px solid #222;
            }}

            .gallery {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
                gap: 12px;
                padding: 20px;
            }}

            .gallery img {{
                width: 100%;
                height: auto;
                border-radius: 10px;
                object-fit: cover;
                transition: transform .2s ease, box-shadow .2s ease;
                cursor: pointer;
            }}

            .gallery img:hover {{
                transform: scale(1.03);
                box-shadow: 0 0 15px rgba(255,255,255,0.2);
            }}

            .lightbox {{
                display: none;
                position: fixed;
                inset: 0;
                background: rgba(0,0,0,0.9);
                justify-content: center;
                align-items: center;
                z-index: 9999;
            }}

            .lightbox img {{
                max-width: 90%;
                max-height: 90%;
                border-radius: 10px;
            }}

            .lightbox.active {{
                display: flex;
            }}
        </style>
    </head>

    <body>

    <header>
        Галерея
    </header>

    <div class="gallery">
        {images_html}
    </div>

    <div class="lightbox" id="lightbox" onclick="closeLightbox()">
        <img id="lightbox-img" src="">
    </div>

    <script>
        function openLightbox(src) {{
            const lb = document.getElementById("lightbox");
            const img = document.getElementById("lightbox-img");
            img.src = src;
            lb.classList.add("active");
        }}

        function closeLightbox() {{
            document.getElementById("lightbox").classList.remove("active");
        }}
    </script>

    </body>
    </html>
    """

    return HTMLResponse(content=html)
