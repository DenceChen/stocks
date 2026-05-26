"""
配置文件 - 存储API密钥和其他配置信息
"""
import os
import logging
from typing import Dict, Any

# 尝试加载.env文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("警告: python-dotenv 未安装，将使用默认设置。如需使用环境变量，请安装 python-dotenv")

# 基本配置
BASE_CONFIG = {
    # 数据目录
    "DATA_DIR": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data")),
    
    # 搜索引擎配置
    "SEARCH_ENGINE": {
        "DEFAULT_METHOD": "minimax",  # 'google', 'baidu' 或 'minimax'
        "MAX_RESULTS": 15,  # 增加默认结果数量
        "SLEEP_INTERVAL": 2.0,  # 搜索请求间隔时间(秒)
    },
    
    # 爬虫配置
    "CRAWLER": {
        "MAX_CONCURRENCY": 5,
        "TIMEOUT": 30,  # 请求超时时间(秒)
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "RETRY_COUNT": 3,  # 重试次数
        "RETRY_DELAY": 5,  # 重试延迟(秒)
    },
    
    # LLM配置 - MiniMax
    "LLM": {
        "API_KEY": os.getenv("LLM_API_KEY"),
        "BASE_URL": os.getenv("LLM_BASE_URL", "https://api.minimaxi.com/v1"),
        "MODEL": os.getenv("LLM_MODEL", "MiniMax-M2.7-highspeed"),
        "MAX_TOKENS": 8192,
        "TEMPERATURE": 0.7,
        "TOP_P": 0.95,
    },

    # MiniMax搜索配置
    "MINIMAX_SEARCH": {
        "BASE_URL": "https://api.minimaxi.com",
        "API_KEY": os.getenv("LLM_API_KEY"),
        "ENDPOINT": "/v1/coding_plan/search",
    },
    
    # 日志配置
    "LOGGING": {
        "LEVEL": logging.INFO,
        "FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "LOG_FILE": os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data")), "stock_agent.log"),
        "CONSOLE_LEVEL": logging.INFO,  # 控制台日志级别
    },
    
    # 投资策略配置
    "INVESTMENT": {
        "FOCUS_INDUSTRIES": ["新能源", "半导体", "人工智能", "生物医药", "消费电子", "金融科技", "大数据", "云计算"],
        "RISK_TOLERANCE": "中等",  # 风险偏好: 低/中等/高
        "INVESTMENT_HORIZON": "中长期",  # 投资周期: 短期/中长期/长期
    },
    
    # Agent配置
    "AGENT_CONFIG": {
        "OUTPUT_DIR": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results")),
        "CACHE_ENABLED": True,
        "CACHE_DIR": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cache")),
        "MAX_RETRY_ATTEMPTS": 3,
        "SAVE_INTERMEDIATE_RESULTS": True,
        "VERBOSE_OUTPUT": False,
    },
}

# 预定义的搜索关键词 - 精简为核心查询，避免超时
DEFAULT_SEARCH_QUERIES = [
    # 宏观与政策
    "A股市场最新行情分析",
    "央行最新货币政策动向",
    "证监会最新监管政策",

    # 热门板块
    "半导体和AI板块最新动态",
    "新能源行业投资机会",

    # 资金与情绪
    "北向资金最新动向",
    "券商最新策略报告观点",

    # 个股筛选
    "低估值高成长股分析",
    "高股息率价值股筛选",

    # 风险
    "股市最新风险提示",
]

# 获取配置函数
def get_config() -> Dict[str, Any]:
    """
    获取配置信息

    Returns:
        包含配置信息的字典
    """
    if not os.getenv("LLM_API_KEY"):
        raise ValueError("LLM_API_KEY environment variable is required")

    config = BASE_CONFIG.copy()
    
    # 确保数据目录存在
    os.makedirs(config["DATA_DIR"], exist_ok=True)
    
    return config

# 初始化日志配置
def init_logging():
    """
    初始化日志配置
    """
    config = get_config()
    log_config = config["LOGGING"]
    
    # 确保日志目录存在
    os.makedirs(os.path.dirname(log_config["LOG_FILE"]), exist_ok=True)
    
    logging.basicConfig(
        level=log_config["LEVEL"],
        format=log_config["FORMAT"],
        handlers=[
            logging.FileHandler(log_config["LOG_FILE"]),
            logging.StreamHandler()
        ]
    )
    
if __name__ == "__main__":
    # 测试配置
    config = get_config()
    print("配置信息:")
    for key, value in config.items():
        print(f"{key}: {value}") 