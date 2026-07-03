from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, Token, UserResponse
from .utils import get_password_hash, verify_password, create_access_token, decode_token
from ..config import settings

router = APIRouter()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # 檢查 Email 是否已存在
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 建立新使用者
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password),
        is_verified=False,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # 生成驗證 Token (有效期 1 小時)
    verify_token = create_access_token(
        data={"sub": user_data.email},
        expires_delta=timedelta(hours=1),
        token_type="verify",
    )

    # 模擬發送 Email：直接在 Console 印出驗證連結
    verify_url = f"http://localhost:8000/api/verify?token={verify_token}"
    print(f"\n--- [模擬 Email 發送] ---")
    print(f"請點擊以下連結驗證 Email:\n{verify_url}")
    print(f"--------------------------\n")

    return new_user


@router.get("/verify", response_class=HTMLResponse)
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    payload = decode_token(token)
    if not payload or payload.get("type") != "verify":
        return HTMLResponse("<h1>Invalid or expired verification link.</h1>")

    email = payload.get("sub")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        return HTMLResponse("<h1>User not found.</h1>")

    if user.is_verified:
        # 已驗證過，直接導向登入頁
        return RedirectResponse(url="http://localhost:5173/login")

    # 標記為已驗證
    user.is_verified = True
    await db.commit()

    # 驗證成功，導向前端登入頁
    return RedirectResponse(url="http://localhost:5173/login?verified=true")


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    # 查詢使用者
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()

    # 驗證密碼與帳號狀態
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="Email not verified. Please check your console for the verification link.",
        )

    # 生成 Access Token
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}
