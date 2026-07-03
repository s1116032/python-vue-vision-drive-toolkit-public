import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .config import settings
from .auth.routes import router as auth_router
from .images.routes import router as images_router
from .tasks.routes import router as tasks_router

# 產生一個假的 test.txt 模型檔案供後續下載使用
dummy_model_path = f"{settings.MODELS_DIR}/test.txt"
if not os.path.exists(dummy_model_path):
    with open(dummy_model_path, "w") as f:
        f.write("This is a dummy self-driving car vision model.\n")

app = FastAPI(title=settings.PROJECT_NAME)

# CORS 設定 (允許前端 Vite 預設的 Port 5173 存取)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載 Auth 路由，統一加上 /api 前綴
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(images_router, prefix="/api/images", tags=["Images"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["Tasks"])


@app.on_event("startup")
async def startup():
    # 啟動時自動建立所有資料表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {"message": "Welcome to Vision Drive Toolkit API"}
