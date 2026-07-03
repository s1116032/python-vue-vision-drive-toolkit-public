import os
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import User, Task, Image
from ..schemas import TaskCreate, TaskResponse
from ..dependencies import get_current_user
from ..config import settings
from .background_jobs import process_training_task

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. 驗證傳入的 image_ids 是否都存在，且都屬於當前使用者 (防呆與資安檢查)
    if not task_data.image_ids:
        raise HTTPException(status_code=400, detail="請至少選擇一張圖片進行訓練")

    result = await db.execute(
        select(Image).where(
            Image.id.in_(task_data.image_ids), Image.user_id == current_user.id
        )
    )
    valid_images = result.scalars().all()

    if len(valid_images) != len(task_data.image_ids):
        raise HTTPException(status_code=400, detail="包含無效或無權限的圖片 ID")

    # 2. 建立任務紀錄
    new_task = Task(
        user_id=current_user.id,
        status="processing",  # 一進入背景任務就標記為處理中
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    # 3. 將耗時任務丟入背景執行 (不阻塞當前 API 回傳)
    background_tasks.add_task(process_training_task, new_task.id)

    return new_task


@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    # 取得該使用者的所有任務，最新的排最前面
    result = await db.execute(
        select(Task)
        .where(Task.user_id == current_user.id)
        .order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()
    return tasks


@router.get("/{task_id}/download")
async def download_model(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. 檢查任務是否存在且屬於該使用者
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalars().first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 2. 檢查任務是否已完成
    if task.status != "completed" or not task.model_path:
        raise HTTPException(
            status_code=400, detail="Model is not ready yet or training failed."
        )

    # 3. 準備檔案路徑
    file_path = os.path.join(settings.MODELS_DIR, task.model_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Model file not found on server")

    # 4. 回傳檔案 (瀏覽器會自動觸發下載)
    return FileResponse(
        path=file_path,
        filename="self_driving_model.txt",
        media_type="application/octet-stream",
    )
