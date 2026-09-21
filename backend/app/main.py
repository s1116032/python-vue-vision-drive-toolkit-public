from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .config import settings
from .auth.routes import router as auth_router
from .images.routes import router as images_router
from .tasks.routes import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup (啟動前執行) ---
    # 自動建立所有資料表 (在生產環境通常會改用 Alembic 遷移，但 MVP 階段這樣寫最簡潔)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # 這裡是應用程式運行的階段

    # --- Shutdown (關閉時執行) ---
    # 可以在這裡加入關閉資料庫連線池、清理快取等邏輯


# 初始化 FastAPI 應用，並注入 lifespan
app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# ==========================================
# 中介軟體設定 (Middleware)
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 路由掛載 (Routers)
# ==========================================
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(images_router, prefix="/api/images", tags=["Images"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["Tasks"])


# ==========================================
# 根路徑健康檢查 (Health Check)
# ==========================================
@app.get("/")
async def root():
    return {"message": "Welcome to Vision Drive Toolkit API", "status": "running"}
