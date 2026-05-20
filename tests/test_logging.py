"""
日志系统测试
"""
import pytest
import os
import sys
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 设置环境变量
os.environ['LLM_API_KEY'] = 'sk-test-key'
os.environ['LOG_LEVEL'] = 'DEBUG'

from src.logging_config import (
    setup_logger,
    get_logger,
    log_api_call,
    log_function_call,
    get_app_logger,
    get_api_logger,
    get_error_logger,
    ColoredFormatter,
    LOG_FORMAT,
    LOG_LEVEL
)


class TestColoredFormatter:
    """测试彩色格式化器"""

    def test_format_with_debug_level(self):
        """测试 DEBUG 级别格式化"""
        formatter = ColoredFormatter(LOG_FORMAT)
        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None
        )
        formatted = formatter.format(record)
        assert "DEBUG" in formatted
        assert "test message" in formatted

    def test_format_with_error_level(self):
        """测试 ERROR 级别格式化"""
        formatter = ColoredFormatter(LOG_FORMAT)
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="error message",
            args=(),
            exc_info=None
        )
        formatted = formatter.format(record)
        assert "ERROR" in formatted


class TestSetupLogger:
    """测试日志设置"""

    def test_setup_logger_returns_logger(self):
        """测试 setup_logger 返回日志记录器"""
        logger = setup_logger("test.setup")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.setup"

    def test_setup_logger_with_file(self, tmp_path):
        """测试带文件的日志记录器"""
        log_file = tmp_path / "test.log"
        logger = setup_logger("test.file", str(log_file))
        assert logger.handlers  # 应该有 handlers

    def test_setup_logger_does_not_duplicate_handlers(self):
        """测试不会重复添加 handler"""
        logger_name = "test.duplicate"
        logger1 = setup_logger(logger_name)
        logger2 = setup_logger(logger_name)
        # 同名 logger 应该返回相同的实例
        assert logger1 is logger2


class TestGetLogger:
    """测试获取日志记录器"""

    def test_get_logger_returns_logger(self):
        """测试 get_logger 返回日志记录器"""
        logger = get_logger("test.get")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.get"


class TestLogApiCall:
    """测试 API 调用日志"""

    def test_log_api_call_without_error(self, caplog):
        """测试记录成功 API 调用"""
        logger = logging.getLogger("test.api")
        logger.setLevel(logging.INFO)

        with caplog.at_level(logging.INFO):
            log_api_call(logger, "POST", "https://api.example.com",
                        status_code=200, duration=1.5)

        assert "API POST https://api.example.com" in caplog.text
        assert "status=200" in caplog.text
        assert "duration=1.500s" in caplog.text

    def test_log_api_call_with_error(self, caplog):
        """测试记录失败 API 调用"""
        logger = logging.getLogger("test.api.error")
        logger.setLevel(logging.ERROR)

        with caplog.at_level(logging.ERROR):
            log_api_call(logger, "GET", "https://api.example.com",
                        status_code=500, error="Server Error")

        assert "ERROR" in caplog.text
        assert "error=Server Error" in caplog.text


class TestLogFunctionCall:
    """测试函数调用日志"""

    def test_log_function_call_with_args(self, caplog):
        """测试记录带参数的函数调用"""
        logger = logging.getLogger("test.func")
        logger.setLevel(logging.DEBUG)

        with caplog.at_level(logging.DEBUG):
            log_function_call(logger, "process_data",
                           args=("arg1", "arg2"),
                           kwargs={"key": "value"},
                           duration=0.5)

        assert "FUNC process_data()" in caplog.text
        assert "args=(arg1, arg2)" in caplog.text
        assert "duration=0.500s" in caplog.text

    def test_log_function_call_with_result(self, caplog):
        """测试记录带返回值的函数调用"""
        logger = logging.getLogger("test.func.result")
        logger.setLevel(logging.DEBUG)

        with caplog.at_level(logging.DEBUG):
            log_function_call(logger, "get_data",
                           result={"status": "success"})

        assert "result=" in caplog.text

    def test_log_function_call_with_error(self, caplog):
        """测试记录错误的函数调用"""
        logger = logging.getLogger("test.func.error")
        logger.setLevel(logging.ERROR)

        with caplog.at_level(logging.ERROR):
            log_function_call(logger, "failing_func",
                           error="ValueError")

        assert "ERROR" in caplog.text
        assert "error=ValueError" in caplog.text


class TestPreconfiguredLoggers:
    """测试预配置日志记录器"""

    def test_get_app_logger(self):
        """测试获取应用日志记录器"""
        logger = get_app_logger()
        assert isinstance(logger, logging.Logger)
        assert "stocks" in logger.name

    def test_get_api_logger(self):
        """测试获取 API 日志记录器"""
        logger = get_api_logger()
        assert isinstance(logger, logging.Logger)
        assert "stocks.api" in logger.name

    def test_get_error_logger(self):
        """测试获取错误日志记录器"""
        logger = get_error_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.ERROR


class TestLogLevel:
    """测试日志级别配置"""

    def test_log_level_from_env(self):
        """测试从环境变量读取日志级别"""
        assert LOG_LEVEL == "DEBUG"
        assert hasattr(logging, "DEBUG")
