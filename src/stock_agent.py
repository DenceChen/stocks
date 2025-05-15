"""
股票投资Agent - 协调整个工作流程，从搜索、爬取到分析生成建议
"""
import logging
import asyncio
import os
import time
from typing import List, Dict, Optional, Any, Union, Tuple
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
        
    async def analyze_market(self, search_queries: List[str], search_method: str = None, max_urls: int = None, max_concurrency: int = None, risk_preference: str = "low") -> Union[Dict[str, Any], str]:
        """
        分析市场整体情况，生成投资建议
        
        Args:
            search_queries: 搜索关键词列表
            search_method: 搜索方法 ('google' 或 'baidu')
            max_urls: 最多处理的URL数量
            max_concurrency: 爬虫最大并发数
            risk_preference: 投资风险偏好 ('low', 'medium', 'high')
            
        Returns:
            包含分析结果的字典或投资建议字符串
        """
        # 使用提供的参数或配置中的参数
        search_method = search_method or self.config["SEARCH_ENGINE"]["DEFAULT_METHOD"]
        max_urls = max_urls or 20
        max_concurrency = max_concurrency or self.config["CRAWLER"]["MAX_CONCURRENCY"]
        
        logger.info(f"开始市场分析，搜索方法: {search_method}，搜索关键词: {search_queries}，风险偏好: {risk_preference}")
        
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
            market_analysis = self.llm_processor.generate_market_analysis(extracted_docs, risk_preference=risk_preference)
            
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
        
    async def run(self, search_queries: List[str], search_method: str = None, max_urls: int = None, max_concurrency: int = None, risk_preference: str = "low") -> str:
        """
        运行完整的工作流程
        
        Args:
            search_queries: 搜索关键词列表
            search_method: 搜索方法 ('google' 或 'baidu')
            max_urls: 最多处理的URL数量
            max_concurrency: 爬虫最大并发数
            risk_preference: 投资风险偏好 ('low', 'medium', 'high')
            
        Returns:
            生成的投资建议
        """
        # 使用提供的参数或配置中的参数
        search_method = search_method or self.config["SEARCH_ENGINE"]["DEFAULT_METHOD"]
        max_urls = max_urls or 20
        max_concurrency = max_concurrency or self.config["CRAWLER"]["MAX_CONCURRENCY"]
        
        logger.info(f"开始运行股票投资Agent，搜索方法: {search_method}，搜索关键词: {search_queries}，风险偏好: {risk_preference}")
        
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
        investment_advice = self.llm_processor.generate_investment_advice(extracted_docs, risk_preference=risk_preference)
        
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

    def analyze_stock(self, stock_code: str, stock_name: Optional[str] = None, max_urls: int = 15, save_results: bool = True, risk_preference: str = "low") -> Dict[str, Any]:
        """
        分析单个股票
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            max_urls: 最大处理URL数量
            save_results: 是否保存结果
            risk_preference: 投资风险偏好
            
        Returns:
            包含分析结果的字典
        """
        logger.info(f"开始分析股票: {stock_name or ''}({stock_code}), 风险偏好: {risk_preference}")
        
        start_time = time.time()
        
        try:
            # 构建搜索关键词
            search_queries = []
            
            # 基本信息搜索
            if stock_name:
                search_queries.extend([
                    f"{stock_code} {stock_name} 财务报表",
                    f"{stock_code} {stock_name} 公司公告",
                    f"{stock_code} {stock_name} 行业分析",
                    f"{stock_code} {stock_name} 最新研报"
                ])
            else:
                search_queries.extend([
                    f"{stock_code} 财务报表",
                    f"{stock_code} 公司公告",
                    f"{stock_code} 行业分析",
                    f"{stock_code} 最新研报"
                ])
            
            # 根据风险偏好添加额外的关键词
            if risk_preference == "low":
                search_queries.extend([
                    f"{stock_code} {stock_name or ''} 稳定性分析",
                    f"{stock_code} {stock_name or ''} 分红历史",
                    f"{stock_code} {stock_name or ''} 风险评估"
                ])
            elif risk_preference == "medium":
                search_queries.extend([
                    f"{stock_code} {stock_name or ''} 成长性分析",
                    f"{stock_code} {stock_name or ''} 行业地位",
                    f"{stock_code} {stock_name or ''} 竞争优势"
                ])
            elif risk_preference == "high":
                search_queries.extend([
                    f"{stock_code} {stock_name or ''} 高成长",
                    f"{stock_code} {stock_name or ''} 突破创新",
                    f"{stock_code} {stock_name or ''} 技术革新"
                ])
            
            # 执行搜索
            urls = self._search(search_queries, max_urls=max_urls)
            if not urls:
                logger.error(f"未找到关于股票 {stock_code} 的相关信息")
                return {"error": f"未找到关于股票 {stock_code} 的相关信息"}
            
            # 爬取网页内容
            documents = asyncio.run(self.crawler.crawl_urls(urls))
            if not documents:
                logger.error(f"爬取股票 {stock_code} 相关网页失败")
                return {"error": f"爬取股票 {stock_code} 相关网页失败"}
                
            # 提取信息
            extracted_docs = []
            for doc in documents:
                info = self.llm_processor.extract_info_from_document(doc)
                extracted_docs.append(info)
            
            # 生成投资建议
            recommendation = self.llm_processor.generate_investment_advice(
                extracted_docs, 
                risk_preference=risk_preference
            )
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 保存结果
            results = {
                "stock_code": stock_code,
                "stock_name": stock_name,
                "recommendation": recommendation,
                "processing_time": processing_time,
                "sources": urls,
                "risk_preference": risk_preference,
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
            }
            
            if save_results:
                # 保存结果到文件
                filename = f"stock_analysis_{stock_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                filepath = os.path.join(self.output_dir, filename)
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"股票代码: {stock_code}\n")
                    f.write(f"股票名称: {stock_name or '未知'}\n")
                    f.write(f"风险偏好: {risk_preference}\n")
                    f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("\n" + "="*50 + "\n")
                    f.write(recommendation)
                    f.write("\n" + "="*50 + "\n")
                    f.write(f"信息来源:\n")
                    for i, url in enumerate(urls, 1):
                        f.write(f"{i}. {url}\n")
                
                results["output_file"] = filepath
                logger.info(f"股票 {stock_code} 分析结果已保存至: {filepath}")
            
            return results
            
        except Exception as e:
            logger.error(f"分析股票 {stock_code} 过程中发生错误: {str(e)}")
            return {"error": str(e)}
    
    def batch_analyze(self, stocks: List[Tuple[str, Optional[str]]], max_urls_per_stock: int = 10, risk_preference: str = "low") -> List[Dict[str, Any]]:
        """
        批量分析多只股票
        
        Args:
            stocks: 股票列表，每项为(代码, 名称)元组
            max_urls_per_stock: 每只股票的最大处理URL数量
            risk_preference: 投资风险偏好
            
        Returns:
            包含每只股票分析结果的列表
        """
        logger.info(f"开始批量分析 {len(stocks)} 只股票，风险偏好: {risk_preference}")
        
        results = []
        for i, (code, name) in enumerate(stocks, 1):
            logger.info(f"[{i}/{len(stocks)}] 分析股票: {name or ''}({code})")
            
            # 分析单个股票
            stock_result = self.analyze_stock(
                stock_code=code,
                stock_name=name,
                max_urls=max_urls_per_stock,
                save_results=True,
                risk_preference=risk_preference
            )
            
            results.append(stock_result)
            
            # 避免过快请求
            if i < len(stocks):
                logger.info(f"等待 3 秒后继续下一只股票分析...")
                time.sleep(3)
        
        # 生成汇总报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = f"batch_analysis_summary_{timestamp}.txt"
        summary_path = os.path.join(self.output_dir, summary_file)
        
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(f"批量股票分析汇总报告\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"风险偏好: {risk_preference}\n")
            f.write(f"分析股票数量: {len(stocks)}\n")
            f.write("\n" + "="*50 + "\n\n")
            
            for i, result in enumerate(results, 1):
                code = result.get("stock_code", "未知")
                name = result.get("stock_name", "")
                stock_name = f"{name}({code})" if name else code
                
                f.write(f"{i}. {stock_name}\n")
                if "error" in result:
                    f.write(f"   错误: {result['error']}\n")
                else:
                    recommendation = result.get("recommendation", "")
                    summary = recommendation[:200] + "..." if len(recommendation) > 200 else recommendation
                    f.write(f"   摘要: {summary}\n")
                    f.write(f"   详细文件: {os.path.basename(result.get('output_file', ''))}\n")
                f.write("\n")
        
        logger.info(f"批量分析汇总报告已保存至: {summary_path}")
        return results

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
        max_concurrency=3,
        risk_preference="low"
    )
    
    # 打印投资建议
    print("\n" + "="*50)
    print("【股票投资建议】")
    print("="*50)
    print(advice)
    print("="*50)
    
if __name__ == "__main__":
    asyncio.run(main()) 