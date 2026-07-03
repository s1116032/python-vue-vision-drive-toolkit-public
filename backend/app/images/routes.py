import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import filetype

from ..database import get_db
from ..models import User, Image
from ..schemas import ImageResponse
from ..dependencies import get_current_user
from ..auth.utils import decode_token
from ..config import settings

router = APIRouter()


@router.post("/", response_model=list[ImageResponse])
async def upload_files(
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    saved_images = []

    for file in files:
        # ==========================================
        # 1. 安全驗證：讀取檔案開頭檢查 Magic Numbers
        # ==========================================
        # 讀取前 2048 bytes 足以判斷絕大多數的圖片與影片格式
        header = await file.read(2048)
        kind = filetype.guess(header)

        # 驗證完畢後，務必將檔案指標歸零，否則後續寫入會從 2KB 處開始，導致檔案損壞！
        await file.seek(0)

        if kind is None:
            raise HTTPException(
                status_code=400, detail=f"無法辨識檔案格式，拒絕上傳: {file.filename}"
            )

        real_mime_type = kind.mime
        # ==========================================
        # 2. 根據「真實的 MIME Type」決定處理邏輯
        if real_mime_type.startswith("image/"):
            file_ext = os.path.splitext(file.filename)[1] or f".{kind.extension}"
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(settings.IMAGES_DIR, unique_filename)

            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            db_image = Image(
                user_id=current_user.id,
                filename=file.filename,
                filepath=unique_filename,
            )
            db.add(db_image)
            saved_images.append(db_image)

        elif real_mime_type.startswith("video/"):
            # 影片抽幀邏輯 (每 3 秒抽一張)
            try:
                import cv2
            except ImportError:
                raise HTTPException(
                    status_code=500, detail="opencv-python not installed."
                )

            file_ext = os.path.splitext(file.filename)[1] or f".{kind.extension}"
            unique_video_name = f"{uuid.uuid4()}{file_ext}"
            video_path = os.path.join(settings.IMAGES_DIR, unique_video_name)

            # 先將影片暫存到本地
            with open(video_path, "wb") as f:
                content = await file.read()
                f.write(content)

            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0:
                fps = 30  # 預設 30 fps
            frame_interval = int(fps * 3)  # 每 3 秒的幀數

            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_count % frame_interval == 0:
                    img_name = f"{uuid.uuid4()}_frame{frame_count}.jpg"
                    img_path = os.path.join(settings.IMAGES_DIR, img_name)
                    cv2.imwrite(img_path, frame)

                    db_image = Image(
                        user_id=current_user.id,
                        filename=f"{file.filename}_frame{frame_count}.jpg",
                        filepath=img_name,
                    )
                    db.add(db_image)
                    saved_images.append(db_image)
                frame_count += 1

            cap.release()
            # MVP 階段不保留影片原件，只保留抽幀圖片以節省空間
            os.remove(video_path)
        else:
            raise HTTPException(
                status_code=400, detail="Only image and video files are supported."
            )

    await db.commit()
    for img in saved_images:
        await db.refresh(img)

    return saved_images


@router.get("/", response_model=list[ImageResponse])
async def get_images(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Image)
        .where(Image.user_id == current_user.id)
        .order_by(Image.created_at.desc())
    )
    images = result.scalars().all()
    return images


@router.get("/{id}/file")
async def get_image_file(
    id: int,
    token: str = Query(..., description="JWT Token for authentication"),
    db: AsyncSession = Depends(get_db),
):
    # 解析 Query String 中的 Token
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")

    email = payload.get("sub")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # 驗證圖片是否屬於該使用者
    result = await db.execute(select(Image).where(Image.id == id))
    image = result.scalars().first()
    if not image or image.user_id != user.id:
        raise HTTPException(status_code=404, detail="Image not found")

    file_path = os.path.join(settings.IMAGES_DIR, image.filepath)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    # 加入 Cache-Control 標頭，強制瀏覽器不要快取
    return FileResponse(
        file_path,
        headers={"Cache-Control": "no-cache, no-store, must-revalidate, max-age=0"},
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Image).where(Image.id == id, Image.user_id == current_user.id)
    )
    image = result.scalars().first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    file_path = os.path.join(settings.IMAGES_DIR, image.filepath)
    if os.path.exists(file_path):
        os.remove(file_path)

    await db.delete(image)
    await db.commit()
    return None
