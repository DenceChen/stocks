"""
中间件 - CORS、请求日志、错误处理、JWT 认证
"""
import time
import logging
import os
from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Optional

import jwt

from src.logging_config import get_api_logger

logger = get_api_logger()

# JWT 配置
JWT_SECRET = os.getenv("JWT_SECRET", "stocks-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # 记录请求
        logger.info(f"→ {request.method} {request.url.path}")

        try:
            response = await call_next(request)

            # SSE 流式响应：直接返回，不做任何缓冲
            content_type = response.headers.get("content-type", "")
            if "text/event-stream" in content_type:
                logger.info(f"← {request.method} {request.url.path} status={response.status_code} (streaming)")
                return response

            # 计算处理时间
            duration = time.time() - start_time

            # 记录响应
            logger.info(
                f"← {request.method} {request.url.path} "
                f"status={response.status_code} duration={duration:.3f}s"
            )

            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = f"{duration:.3f}"

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"✗ {request.method} {request.url.path} "
                f"error={str(e)} duration={duration:.3f}s"
            )
            raise


def setup_cors(app):
    """配置 CORS"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:5173",
            "*",  # 开发环境允许所有
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


async def get_current_user(request: Request) -> Optional[int]:
    """
    从请求中提取并验证 JWT token，返回 user_id

    对于 SSE stream 端点，token 从 query param 读取（因为 EventSource 不支持自定义 header）
    对于普通 API，token 从 Authorization header 读取

    Returns:
        int: user_id
    Raises:
        HTTPException: 认证失败时抛出 401
    """
    # 先尝试从 query param 获取 token（SSE stream 使用）
    token = request.query_params.get("token")

    # 如果 query param 没有，尝试从 Authorization header 获取
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证 token"
        )

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 中缺少 user_id"
            )
        return user_id
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


def decode_access_token(token: str) -> dict:
    """解码 JWT token（供其他模块使用）"""
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


__all__ = ["setup_cors", "RequestLoggingMiddleware", "get_current_user", "decode_access_token", "JWT_SECRET", "JWT_ALGORITHM"]
