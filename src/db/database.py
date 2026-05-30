"""
数据库操作 - 使用 aiosqlite 异步操作 SQLite
"""
import aiosqlite
import os
from contextlib import asynccontextmanager

from src.logging_config import get_api_logger

logger = get_api_logger()

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "stocks.db")


@asynccontextmanager
async def get_db():
    """获取数据库连接的异步上下文管理器"""
    db = await aiosqlite.connect(DB_PATH)
    try:
        await db.execute("PRAGMA foreign_keys = ON")
        yield db
    finally:
        await db.close()


async def init_db():
    """初始化数据库表"""
    async with aiosqlite.connect(DB_PATH) as db:
        # 启用外键约束
        await db.execute("PRAGMA foreign_keys = ON")

        # 创建用户表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # 创建分析历史表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('stock', 'market', 'batch')),
                stock_code TEXT NOT NULL DEFAULT '',
                stock_name TEXT NOT NULL DEFAULT '',
                risk_preference TEXT NOT NULL DEFAULT 'medium',
                summary TEXT NOT NULL DEFAULT '',
                full_content TEXT NOT NULL DEFAULT '',
                processing_time REAL,
                sources TEXT NOT NULL DEFAULT '[]',
                starred INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 创建索引以提升查询性能
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_user_id
            ON analysis_history(user_id)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_user_starred
            ON analysis_history(user_id, starred)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_created_at
            ON analysis_history(created_at DESC)
        """)

        await db.commit()
        logger.info(f"数据库初始化完成: {DB_PATH}")


async def save_analysis(
    user_id: int,
    analysis_type: str,
    stock_code: str,
    stock_name: str,
    risk_preference: str,
    summary: str,
    full_content: str,
    processing_time: float = None,
    sources: list = None
) -> int:
    """保存分析记录到数据库，返回记录 ID"""
    import json
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO analysis_history
            (user_id, type, stock_code, stock_name, risk_preference, summary, full_content, processing_time, sources)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            analysis_type,
            stock_code,
            stock_name,
            risk_preference,
            summary,
            full_content,
            processing_time,
            json.dumps(sources or [], ensure_ascii=False)
        ))
        await db.commit()
        return cursor.lastrowid
