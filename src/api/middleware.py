"""
中间件 - CORS、请求日志、错误处理
"""
import time
import logging
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from src.logging_config import get_api_logger

logger = get_api_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # 记录请求
        logger.info(f"→ {request.method} {request.url.path}")

        try:
            response = await call_next(request)

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
