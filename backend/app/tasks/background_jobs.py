import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import AsyncSessionLocal
from ..models import Task


async def process_training_task(task_id: int):
    """
    背景任務：模擬自駕車模型訓練
    注意：這裡必須使用 AsyncSessionLocal 建立獨立的 DB 連線
    """
    # 模擬訓練耗時 30 秒
    await asyncio.sleep(30)

    # 訓練完成，更新資料庫狀態
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalars().first()

        if task:
            task.status = "completed"
            task.model_path = "test.txt"  # 指向 main.py 中建立的假模型
            await db.commit()
