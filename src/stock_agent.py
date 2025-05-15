"""
股票投资Agent - 协调整个工作流程，从搜索、爬取到分析生成建议
"""
import logging
import asyncio
import os
from typing import List, Dict, Optional, Any, Union
from datetime import datetime

# 使用直接导入而非相对导入
from src.config import get_config
from src.search_engine import SearchEngine
from src.crawler import WebCrawler
from src.llm_processor import LLMProcessor

# 获取配置
config = get_config()

# 设置日志
logging.basicConfig(
    level=config["LOGGING"]["LEVEL"], 
    format=config["LOGGING"]["FORMAT"],
    handlers=[
        logging.FileHandler(config["LOGGING"]["LOG_FILE"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StockAgent:
    def __init__(self, data_dir: str = None, config: Dict[str, Any] = None):
        """
        初始化股票投资Agent
        
        Args:
            data_dir: 数据保存目录
            config: 配置字典，如果提供则使用该配置
        """
        # 使用提供的配置或获取默认配置
        self.config = config or get_config()
        
        # 使用提供的数据目录或配置中的数据目录
        self.data_dir = data_dir or self.config["DATA_DIR"]
        
        # 设置输出目录
        self.output_dir = self.config["AGENT_CONFIG"]["OUTPUT_DIR"] if "AGENT_CONFIG" in self.config else os.path.join(self.data_dir, "results")
        
        # 确保目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化搜索引擎
        self.search_engine = SearchEngine(
            max_results=self.config["SEARCH_ENGINE"]["MAX_RESULTS"],
            sleep_interval=self.config["SEARCH_ENGINE"]["SLEEP_INTERVAL"]
        )
        
        # 初始化爬虫
        self.crawler = WebCrawler(data_dir=self.data_dir)
        
        # 初始化LLM处理器
        self.llm_processor = LLMProcessor(
            api_key=self.config["LLM"]["API_KEY"],
            base_url=self.config["LLM"]["BASE_URL"],
            model=self.config["LLM"]["MODEL"]
        )
        
        logger.info("股票投资Agent初始化完成")
        
    async def analyze_market(self, search_queries: List[str], search_method: str = None, max_urls: int = None, max_concurrency: int = None) -> Union[Dict[str, Any], str]:
        """
        分析市场整体情况，生成投资建议
        
        Args:
            search_queries: 搜索关键词列表
            search_method: 搜索方法 ('google' 或 'baidu')
            max_urls: 最多处理的URL数量
            max_concurrency: 爬虫最大并发数
            
        Returns:
            包含分析结果的字典或投资建议字符串
        """
        # 使用提供的参数或配置中的参数
        search_method = search_method or self.config["SEARCH_ENGINE"]["DEFAULT_METHOD"]
        max_urls = max_urls or 20
        max_concurrency = max_concurrency or self.config["CRAWLER"]["MAX_CONCURRENCY"]
        
        logger.info(f"开始市场分析，搜索方法: {search_method}，搜索关键词: {search_queries}")
        
        try:
            # 步骤1: 搜索获取URL
            urls = self._search(search_queries, search_method, max_urls)
            if not urls:
                logger.error("没有找到任何URL，无法继续")
                return {"error": "无法获取相关信息，请检查搜索关键词或网络连接。"}
                
            # 步骤2: 爬取网页内容
            documents = await self.crawler.crawl_urls(urls, max_concurrency=max_concurrency)
            if not documents:
                logger.error("爬取失败，没有获取到任何内容")
                return {"error": "爬取网页内容失败，请检查网络连接或URL有效性。"}
                
            logger.info(f"成功爬取了 {len(documents)} 个网页")
            
            # 步骤3: 提取每个文档的关键信息
            extracted_docs = []
            for doc in documents:
                extracted_info = self.llm_processor.extract_info_from_document(doc)
                extracted_docs.append(extracted_info)
                
            logger.info(f"完成了 {len(extracted_docs)} 个文档的信息提取")
            
            # 步骤4: 生成市场分析和投资建议
            market_analysis = self.llm_processor.generate_market_analysis(extracted_docs)
            
            # 步骤5: 保存分析结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"market_analysis_{timestamp}.txt"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(market_analysis)
            
            logger.info(f"市场分析已保存至: {filepath}")
            
            # 返回分析结果
            return {
                "recommendation": market_analysis,
                "sources": [doc.get("url", "") for doc in documents],
                "timestamp": timestamp,
                "output_file": filepath
            }
            
        except Exception as e:
            logger.error(f"市场分析过程中发生错误: {str(e)}")
            return f"市场分析过程中发生错误: {str(e)}"
        
    async def run(self, search_queries: List[str], search_method: str = None, max_urls: int = None, max_concurrency: int = None) -> str:
        """
        运行完整的工作流程
        
        Args:
            search_queries: 搜索关键词列表
            search_method: 搜索方法 ('google' 或 'baidu')
            max_urls: 最多处理的URL数量
            max_concurrency: 爬虫最大并发数
            
        Returns:
            生成的投资建议
        """
        # 使用提供的参数或配置中的参数
        search_method = search_method or self.config["SEARCH_ENGINE"]["DEFAULT_METHOD"]
        max_urls = max_urls or 20
        max_concurrency = max_concurrency or self.config["CRAWLER"]["MAX_CONCURRENCY"]
        
        logger.info(f"开始运行股票投资Agent，搜索方法: {search_method}，搜索关键词: {search_queries}")
        
        # 步骤1: 搜索获取URL
        urls = self._search(search_queries, search_method, max_urls)
        if not urls:
            logger.error("没有找到任何URL，无法继续")
            return "无法获取相关信息，请检查搜索关键词或网络连接。"
            
        # 步骤2: 爬取网页内容
        documents = await self.crawler.crawl_urls(urls, max_concurrency=max_concurrency)
        if not documents:
            logger.error("爬取失败，没有获取到任何内容")
            return "爬取网页内容失败，请检查网络连接或URL有效性。"
            
        logger.info(f"成功爬取了 {len(documents)} 个网页")
        
        # 步骤3: 提取每个文档的关键信息
        extracted_docs = []
        for doc in documents:
            extracted_info = self.llm_processor.extract_info_from_document(doc)
            extracted_docs.append(extracted_info)
            
        logger.info(f"完成了 {len(extracted_docs)} 个文档的信息提取")
        
        # 步骤4: 生成投资建议
        investment_advice = self.llm_processor.generate_investment_advice(extracted_docs)
        
        # 步骤5: 保存投资建议
        filename = self.llm_processor.save_advice_to_file(investment_advice, data_dir=self.output_dir)
        logger.info(f"投资建议已保存至: {filename}")
        
        logger.info("完成全部流程，已生成投资建议")
        return investment_advice
        
    def _search(self, queries: List[str], method: str = "google", max_urls: int = 20) -> List[str]:
        """
        搜索获取URL
        
        Args:
            queries: 搜索关键词列表
            method: 搜索方法 ('google' 或 'baidu')
            max_urls: 最多返回的URL数量
            
        Returns:
            URL列表
        """
        logger.info(f"使用{method}搜索: {queries}")
        
        urls = []
        if method.lower() == "google":
            urls = self.search_engine.get_urls_with_google(queries)
        elif method.lower() == "baidu":
            urls = self.search_engine.get_urls_with_baidu(queries)
        else:
            logger.error(f"不支持的搜索方法: {method}")
            return []
            
        # 限制URL数量
        if len(urls) > max_urls:
            logger.info(f"限制URL数量 {len(urls)} -> {max_urls}")
            urls = urls[:max_urls]
            
        return urls

async def main():
    """
    主函数，演示Agent的使用
    """
    # 创建Agent
    agent = StockAgent()
    
    # 定义搜索关键词
    search_queries = [
        "最近央行政策新闻",
        "证监会最新政策公告",
        "近期股市行情分析",
        "热门行业板块分析",
        "近期上涨最快的股票",
        "金融科技股票分析",
        "新能源行业投资机会",
        "消费行业股票分析",
        "医药行业投资机会"
    ]
    
    # 运行Agent，获取投资建议
    advice = await agent.run(
        search_queries=search_queries,
        search_method="google",  # 也可以是"baidu"
        max_urls=15,
        max_concurrency=3
    )
    
    # 打印投资建议
    print("\n" + "="*50)
    print("【股票投资建议】")
    print("="*50)
    print(advice)
    print("="*50)
    
if __name__ == "__main__":
    asyncio.run(main()) 