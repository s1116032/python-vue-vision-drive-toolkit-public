import os
import zipfile
import shutil
import time
from sqlalchemy.orm import Session
from ..database import SyncSessionLocal
from ..models import Task, Image
from ..config import settings


def convert_to_yolo_bbox(ann):
    """將 annotation 轉換為 YOLO BBox 格式"""
    class_id = ann.get("category_id", 0)

    if ann["type"] == "bbox":
        x, y, w, h = ann["x"], ann["y"], ann["w"], ann["h"]
        return f"{class_id} {x + w / 2:.6f} {y + h / 2:.6f} {w:.6f} {h:.6f}"

    elif ann["type"] == "polygon":
        points = ann["points"]
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        w, h = max_x - min_x, max_y - min_y
        return f"{class_id} {min_x + w / 2:.6f} {min_y + h / 2:.6f} {w:.6f} {h:.6f}"

    return None


def process_training_task(task_id: int, image_ids: list[int]):
    # 模擬訓練耗時 (使用同步的 time.sleep)
    time.sleep(3)

    # 使用同步 Session
    db: Session = SyncSessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return

        # 準備暫存目錄
        task_dir = os.path.join(settings.MODELS_DIR, f"task_{task_id}")
        os.makedirs(task_dir, exist_ok=True)

        # 取得圖片與標記資料 (同步查詢)
        images = db.query(Image).filter(Image.id.in_(image_ids)).all()

        # 複製圖片並產生 YOLO txt 標籤檔
        for img in images:
            src_path = os.path.join(settings.IMAGES_DIR, img.filepath)
            base_name = os.path.splitext(img.filepath)[0]

            # 使用 shutil.copy 效能更好且程式碼更乾淨
            if os.path.exists(src_path):
                shutil.copy(src_path, os.path.join(task_dir, img.filepath))

            if (
                img.annotations
                and isinstance(img.annotations, list)
                and len(img.annotations) > 0
            ):
                txt_path = os.path.join(task_dir, f"{base_name}.txt")
                with open(txt_path, "w", encoding="utf-8", newline="\n") as f:
                    for ann in img.annotations:
                        line = convert_to_yolo_bbox(ann)
                        if line:
                            f.write(line + "\n")

        # 4. 打包成 ZIP
        zip_filename = f"dataset_task_{task_id}.zip"
        zip_path = os.path.join(settings.MODELS_DIR, zip_filename)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(task_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, task_dir)
                    zipf.write(file_path, arcname)

        # 清理暫存目錄
        shutil.rmtree(task_dir)

        # 更新資料庫狀態
        task.status = "completed"
        task.model_path = zip_filename
        db.commit()

    except Exception as e:
        print(f"Task {task_id} failed: {e}")
        # 確保 task 變數存在再更新失敗狀態
        if "task" in locals() and task:
            task.status = "failed"
            db.commit()
    finally:
        # 關閉同步 Session
        db.close()
