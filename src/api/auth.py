"""
认证 API - 用户注册、登录、JWT 认证
"""
import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional

from src.api.middleware import get_current_user
from src.db.database import get_db, init_db
from src.logging_config import get_api_logger

logger = get_api_logger()

# JWT 配置
JWT_SECRET = os.getenv("JWT_SECRET", "stocks-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 30

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


# ============ 数据模型 ============

class UserRegister(BaseModel):
    """用户注册请求"""
    username: str
    password: str


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    created_at: str


# ============ 辅助函数 ============

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')


def create_access_token(user_id: int, username: str) -> str:
    """生成 JWT access token"""
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """解码 JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 已过期"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Token"
        )


# ============ 路由 ============

@router.post("/register", response_model=TokenResponse)
async def register(user: UserRegister):
    """用户注册"""
    async with get_db() as db:
        # 检查用户名是否已存在
        cursor = await db.execute(
            "SELECT id FROM users WHERE username = ?",
            (user.username,)
        )
        existing_user = await cursor.fetchone()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被注册"
            )

        # 创建新用户
        password_hash = get_password_hash(user.password)
        cursor = await db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (user.username, password_hash)
        )
        await db.commit()
        user_id = cursor.lastrowid

        logger.info(f"新用户注册成功: {user.username} (ID: {user_id})")

        # 生成 token
        access_token = create_access_token(user_id, user.username)
        return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    """用户登录"""
    async with get_db() as db:
        # 查找用户
        cursor = await db.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (user.username,)
        )
        user_row = await cursor.fetchone()

        if not user_row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )

        user_id, username, password_hash = user_row

        # 验证密码
        if not verify_password(user.password, password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )

        logger.info(f"用户登录成功: {username} (ID: {user_id})")

        # 生成 token
        access_token = create_access_token(user_id, username)
        return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user_id: int = Depends(get_current_user)):
    """获取当前用户信息"""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, username, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        user_row = await cursor.fetchone()

        if not user_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        return UserResponse(
            id=user_row[0],
            username=user_row[1],
            created_at=user_row[2]
        )
