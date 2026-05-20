"""
日志配置模块 - 统一管理项目日志系统

日志级别:
- DEBUG: 详细调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误

日志格式:
- 时间 | 级别 | 模块 | 消息

日志文件:
- logs/app.log: 应用日志
- logs/error.log: 错误日志（仅 ERROR 及以上）
- logs/api.log: API 调用日志
"""
import os
import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from pathlib import Path

# 日志目录
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志文件路径
APP_LOG = LOG_DIR / "app.log"
ERROR_LOG = LOG_DIR / "error.log"
API_LOG = LOG_DIR / "api.log"

# 日志格式
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志级别环境变量
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


class ColoredFormatter(logging.Formatter):
    """彩色日志格式器"""
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 绿色
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[35m',  # 紫色
        'RESET': '\033[0m',
    }

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(name: str, log_file: str = None, level: str = None) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        log_file: 日志文件路径（可选）
        level: 日志级别（可选，默认从环境变量读取）

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level or LOG_LEVEL))
    logger.propagate = False

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = ColoredFormatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件 handler
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称（通常使用 __name__）

    Returns:
        日志记录器
    """
    return logging.getLogger(name)


def log_api_call(logger: logging.Logger, method: str, url: str,
                 status_code: int = None, duration: float = None,
                 error: str = None):
    """
    记录 API 调用日志

    Args:
        logger: 日志记录器
        method: HTTP 方法
        url: 请求 URL
        status_code: 响应状态码
        duration: 请求耗时（秒）
        error: 错误信息
    """
    parts = [f"API {method} {url}"]

    if status_code:
        parts.append(f"status={status_code}")

    if duration:
        parts.append(f"duration={duration:.3f}s")

    if error:
        parts.append(f"error={error}")
        logger.error(" | ".join(parts))
    else:
        logger.info(" | ".join(parts))


def log_function_call(logger: logging.Logger, func_name: str,
                      args: tuple = None, kwargs: dict = None,
                      result: any = None, error: str = None,
                      duration: float = None):
    """
    记录函数调用日志

    Args:
        logger: 日志记录器
        func_name: 函数名称
        args: 位置参数
        kwargs: 关键字参数
        result: 返回值
        error: 错误信息
        duration: 执行耗时
    """
    parts = [f"FUNC {func_name}()"]

    if args:
        args_str = ", ".join(str(a)[:50] for a in args[:3])
        if len(args) > 3:
            args_str += "..."
        parts.append(f"args=({args_str})")

    if kwargs:
        kwargs_str = ", ".join(f"{k}={v}"[:30] for k, v in list(kwargs.items())[:3])
        if len(kwargs) > 3:
            kwargs_str += "..."
        parts.append(f"kwargs={{{kwargs_str}}}")

    if duration:
        parts.append(f"duration={duration:.3f}s")

    if error:
        parts.append(f"error={error}")
        logger.error(" | ".join(parts))
    elif result is not None:
        result_str = str(result)[:100]
        if len(str(result)) > 100:
            result_str += "..."
        parts.append(f"result={result_str}")
        logger.debug(" | ".join(parts))
    else:
        logger.debug(" | ".join(parts))


# 预配置的日志记录器
def get_app_logger() -> logging.Logger:
    """获取应用日志记录器"""
    return setup_logger("stocks", str(APP_LOG))


def get_api_logger() -> logging.Logger:
    """获取 API 日志记录器"""
    return setup_logger("stocks.api", str(API_LOG))


def get_error_logger() -> logging.Logger:
    """获取错误日志记录器（仅记录 ERROR 及以上）"""
    logger = setup_logger("stocks.error", str(ERROR_LOG))
    logger.setLevel(logging.ERROR)
    return logger


# 便捷函数
def debug(message: str, *args, **kwargs):
    """记录 DEBUG 级别日志"""
    get_app_logger().debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs):
    """记录 INFO 级别日志"""
    get_app_logger().info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs):
    """记录 WARNING 级别日志"""
    get_app_logger().warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs):
    """记录 ERROR 级别日志"""
    get_app_logger().error(message, *args, **kwargs)


def critical(message: str, *args, **kwargs):
    """记录 CRITICAL 级别日志"""
    get_app_logger().critical(message, *args, **kwargs)


if __name__ == "__main__":
    # 测试日志系统
    app_logger = get_app_logger()
    api_logger = get_api_logger()
    error_logger = get_error_logger()

    app_logger.debug("This is a debug message")
    app_logger.info("This is an info message")
    app_logger.warning("This is a warning message")
    app_logger.error("This is an error message")

    log_api_call(api_logger, "POST", "https://api.example.com/chat",
                 status_code=200, duration=1.234)

    log_function_call(app_logger, "process_data",
                     args=("arg1", "arg2"),
                     kwargs={"key": "value"},
                     result={"status": "success"},
                     duration=0.5)

    print(f"\n日志文件已创建:")
    print(f"  - {APP_LOG}")
    print(f"  - {ERROR_LOG}")
    print(f"  - {API_LOG}")
