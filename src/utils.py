"""
工具模块 - 包含日志配置和其他通用工具函数
"""
import os
import sys
import time
import logging
import platform
from typing import Dict, Any, Optional
from datetime import datetime

# 颜色代码常量
class Colors:
    """终端颜色代码"""
    # 前景色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # 背景色
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # 样式
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ITALIC = '\033[3m'
    
    # 重置
    RESET = '\033[0m'

    # 禁用颜色输出的标志
    DISABLED = False
    
    @classmethod
    def disable_colors(cls):
        """禁用颜色输出"""
        cls.DISABLED = True
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """对文本应用颜色"""
        if cls.DISABLED or 'win' in platform.system().lower():
            return text
        return f"{color}{text}{cls.RESET}"

# 定制的日志格式化器
class ColoredFormatter(logging.Formatter):
    """为不同级别的日志添加颜色的格式化器"""
    
    COLORS = {
        'DEBUG': Colors.BRIGHT_BLUE,
        'INFO': Colors.BRIGHT_GREEN,
        'WARNING': Colors.BRIGHT_YELLOW,
        'ERROR': Colors.BRIGHT_RED,
        'CRITICAL': Colors.BG_RED + Colors.WHITE,
    }
    
    MODULE_COLOR = Colors.BRIGHT_CYAN
    TIME_COLOR = Colors.BRIGHT_BLACK
    MESSAGE_COLOR = Colors.RESET
    
    def __init__(self, fmt=None, datefmt=None, style='%', validate=True):
        super().__init__(fmt, datefmt, style, validate)
        
        # Windows终端通常不支持ANSI颜色代码
        if 'win' in platform.system().lower():
            Colors.disable_colors()
    
    def format(self, record):
        levelname = record.levelname
        module = record.name
        message = record.getMessage()
        
        # 格式化时间
        asctime = self.formatTime(record, self.datefmt)
        
        # 应用颜色
        if not Colors.DISABLED:
            levelname = Colors.colorize(f"[{levelname:^8}]", self.COLORS.get(levelname, Colors.RESET))
            module = Colors.colorize(f"{module}", self.MODULE_COLOR)
            asctime = Colors.colorize(f"{asctime}", self.TIME_COLOR)
            message = Colors.colorize(f"{message}", self.MESSAGE_COLOR)
        else:
            levelname = f"[{levelname:^8}]"
        
        # 将格式化的各部分组合起来
        log_message = f"{asctime} {levelname} {module}: {message}"
        
        # 如果有异常信息，添加到日志中
        if record.exc_info:
            log_message += self.formatException(record.exc_info)
            
        return log_message

# 添加Logger类以兼容导入
class Logger:
    """
    日志管理类，提供对日志功能的统一访问
    """
    
    @classmethod
    def setup_logging(cls, log_file: Optional[str] = None, log_level: int = logging.INFO, console_level: int = logging.INFO) -> logging.Logger:
        """
        设置全局日志配置
        
        Args:
            log_file: 日志文件路径，如果为None则不记录到文件
            log_level: 文件日志级别
            console_level: 控制台日志级别
            
        Returns:
            根日志记录器
        """
        # 获取根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # 设置为最低级别，让处理器决定是否记录
        
        # 清除现有的处理器
        root_logger.handlers = []
        
        # 创建彩色控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_formatter = ColoredFormatter(
            fmt='%(asctime)s %(levelname)s %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # 如果提供了日志文件路径，创建文件处理器
        if log_file:
            # 确保日志目录存在
            os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
            
            # 创建文件处理器
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                fmt='%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
        
        return root_logger
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        获取指定名称的日志记录器
        
        Args:
            name: 日志记录器名称，通常为模块名
            
        Returns:
            日志记录器
        """
        return logging.getLogger(name)

# 保留原有的函数接口以保持兼容性
def setup_logging(log_file: Optional[str] = None, log_level: int = logging.INFO, console_level: int = logging.INFO) -> logging.Logger:
    """设置日志的函数版本，调用Logger类的方法"""
    return Logger.setup_logging(log_file, log_level, console_level)

def get_logger(name: str) -> logging.Logger:
    """获取日志记录器的函数版本，调用Logger类的方法"""
    return Logger.get_logger(name)

def timer(func):
    """
    装饰器：计算并记录函数执行时间
    
    Args:
        func: 要装饰的函数
        
    Returns:
        装饰后的函数
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        logger.debug(f"开始执行 {func.__name__}")
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"执行完成 {func.__name__}, 耗时: {execution_time:.4f}秒")
        return result
    return wrapper

def async_timer(func):
    """
    装饰器：计算并记录异步函数执行时间
    
    Args:
        func: 要装饰的异步函数
        
    Returns:
        装饰后的异步函数
    """
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        logger.debug(f"开始执行 {func.__name__}")
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"执行完成 {func.__name__}, 耗时: {execution_time:.4f}秒")
        return result
    return wrapper

def save_data(data: Any, filename: str, data_dir: str = "../data") -> str:
    """
    保存数据到文件
    
    Args:
        data: 要保存的数据
        filename: 文件名，无需包含时间戳和目录
        data_dir: 数据目录
        
    Returns:
        完整的文件路径
    """
    import json
    
    # 确保数据目录存在
    os.makedirs(data_dir, exist_ok=True)
    
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = os.path.join(data_dir, f"{filename}_{timestamp}.json")
    
    # 保存数据
    try:
        with open(full_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return full_filename
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"保存数据出错: {str(e)}")
        return ""

def print_colored_title(title: str, color: str = Colors.BRIGHT_CYAN, width: int = 50, char: str = "=") -> None:
    """
    打印彩色标题
    
    Args:
        title: 标题文本
        color: 颜色代码
        width: 总宽度
        char: 填充字符
    """
    border = char * width
    centered_title = f"{title}".center(width)
    
    print("\n" + Colors.colorize(border, color))
    print(Colors.colorize(centered_title, color))
    print(Colors.colorize(border, color) + "\n")

if __name__ == "__main__":
    # 测试日志配置
    logger = setup_logging()
    logger.debug("这是一个调试日志")
    logger.info("这是一个信息日志")
    logger.warning("这是一个警告日志")
    logger.error("这是一个错误日志")
    logger.critical("这是一个严重错误日志")
    
    # 测试彩色标题
    print_colored_title("测试标题", Colors.BRIGHT_GREEN)
    print_colored_title("警告信息", Colors.BRIGHT_YELLOW)
    print_colored_title("错误信息", Colors.BRIGHT_RED) 