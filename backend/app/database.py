from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from .config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


# 依賴注入：取得 DB Session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


SYNC_DATABASE_URL = settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 必須加上這個參數
)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
