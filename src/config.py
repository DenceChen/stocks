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
        "DEFAULT_METHOD": "google",  # 'google' 或 'baidu'
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
    
    # LLM配置
    "LLM": {
        "API_KEY": os.getenv("LLM_API_KEY", "sk-1c5050f8829e45d18b1b8d0f124c2219"),
        "BASE_URL": os.getenv("LLM_BASE_URL", "https://api.deepseek.com"),
        "MODEL": os.getenv("LLM_MODEL", "deepseek-chat"),
        "MAX_TOKENS": 4096,
        "TEMPERATURE": 0.7,  # 添加温度参数，控制生成文本的随机性
        "TOP_P": 0.95,  # 添加top_p参数，控制采样范围
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

# 预定义的搜索关键词 - 大幅扩充和细化
DEFAULT_SEARCH_QUERIES = [
    # 宏观经济与政策
    "中国最新GDP增长预期",
    "央行最新货币政策动向",
    "证监会最新监管政策",
    "国家发改委产业政策最新动态",
    "财政部最新财政政策",
    "中国经济转型最新进展",
    "最新减税降费政策",
    
    # 市场趋势与行情
    "最近A股市场行情分析",
    "今日股市涨跌板块分析",
    "近期市场资金流向趋势",
    "外资流入流出最新数据",
    "北向资金动向分析",
    "融资融券余额变化趋势",
    "市场情绪指标分析",
    
    # 热门行业板块
    "半导体行业最新发展趋势",
    "新能源行业投资机会分析",
    "人工智能概念股最新动态",
    "生物医药行业投资分析",
    "消费电子产业链分析",
    "金融科技行业发展前景",
    "数字经济相关板块分析",
    
    # 个股动态
    "近期业绩大幅增长的股票",
    "连续上涨的强势股分析",
    "高股息率价值股筛选",
    "低估值绩优股分析",
    "主力资金重点关注的股票",
    "机构一致推荐的股票",
    "创新高股票分析",
    
    # 特定指标分析
    "高ROE股票筛选与分析",
    "高毛利率公司分析",
    "高研发投入企业分析",
    "高现金流企业分析",
    "低市盈率高成长股分析",
    
    # 研报与分析师观点
    "券商最新策略报告观点",
    "知名分析师最新股市预测",
    "机构最新重仓股变化",
    "私募基金最新持仓动向",
    "公募基金重点布局方向",
    
    # 风险事件监控
    "股市最新风险提示",
    "近期监管处罚信息",
    "企业财务造假风险预警",
    "上市公司债务风险分析",
    "股票质押风险监控",
    
    # 国际市场影响
    "美联储最新货币政策对A股影响",
    "国际地缘政治风险对股市影响",
    "全球资本市场联动性分析",
    "外围市场波动对A股影响",
]

# 获取配置函数
def get_config() -> Dict[str, Any]:
    """
    获取配置信息
    
    Returns:
        包含配置信息的字典
    """
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