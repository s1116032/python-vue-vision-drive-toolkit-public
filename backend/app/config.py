import os

# 取得 backend 資料夾的絕對路徑
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings:
    PROJECT_NAME: str = "Vision Drive Toolkit"
    # 使用非同步 SQLite
    DATABASE_URL: str = f"sqlite+aiosqlite:///{os.path.join(BASE_DIR, 'app.db')}"
    
    # JWT 設定
    SECRET_KEY: str = "super-secret-key-for-jwt-day1-mvp"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 小時
    
    # 檔案儲存路徑
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    IMAGES_DIR: str = os.path.join(UPLOAD_DIR, "images")
    MODELS_DIR: str = os.path.join(UPLOAD_DIR, "models")

settings = Settings()

# 確保上傳目錄存在
os.makedirs(settings.IMAGES_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)