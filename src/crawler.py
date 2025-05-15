"""
网页爬虫模块 - 负责爬取指定URL的内容
"""
import asyncio
import logging
from typing import List, Dict, Optional
import os
import json
from datetime import datetime
from crawl4ai import AsyncWebCrawler

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebCrawler:
    def __init__(self, data_dir: str = "../data"):
        """
        初始化网页爬虫
        
        Args:
            data_dir: 数据保存目录
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
    async def crawl_url(self, url: str) -> Optional[Dict]:
        """
        爬取单个URL的内容
        
        Args:
            url: 待爬取的URL
            
        Returns:
            包含爬取内容的字典，失败返回None
        """
        logger.info(f"开始爬取: {url}")
        try:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url)
                
                if not result or not result.markdown:
                    logger.warning(f"URL爬取失败或内容为空: {url}")
                    return None
                    
                content = {
                    "url": url,
                    "title": result.title if hasattr(result, "title") else "未知标题",
                    "content": result.markdown,
                    "crawl_time": datetime.now().isoformat()
                }
                
                logger.info(f"URL爬取成功: {url}")
                return content
                
        except Exception as e:
            logger.error(f"爬取URL出错: {url}, 错误: {str(e)}")
            return None
            
    async def crawl_urls(self, urls: List[str], max_concurrency: int = 5) -> List[Dict]:
        """
        批量爬取多个URL
        
        Args:
            urls: URL列表
            max_concurrency: 最大并发数
            
        Returns:
            成功爬取的内容列表
        """
        logger.info(f"开始爬取 {len(urls)} 个URL，最大并发数: {max_concurrency}")
        
        # 创建任务列队，但限制并发数
        results = []
        for i in range(0, len(urls), max_concurrency):
            batch = urls[i:i+max_concurrency]
            tasks = [self.crawl_url(url) for url in batch]
            batch_results = await asyncio.gather(*tasks)
            
            # 过滤掉None结果
            valid_results = [r for r in batch_results if r]
            results.extend(valid_results)
            
            logger.info(f"完成批次爬取: {i+1} 至 {min(i+max_concurrency, len(urls))}/{len(urls)}")
            
        # 保存爬取结果
        self._save_results(results)
        
        return results
        
    def _save_results(self, results: List[Dict]):
        """
        保存爬取结果到文件
        
        Args:
            results: 爬取结果列表
        """
        if not results:
            logger.warning("没有结果需要保存")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.data_dir, f"crawl_results_{timestamp}.json")
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"爬取结果已保存至: {filename}")
        except Exception as e:
            logger.error(f"保存爬取结果出错: {str(e)}")
            
if __name__ == "__main__":
    # 测试代码
    async def test():
        crawler = WebCrawler()
        test_urls = [
            "https://www.pbc.gov.cn/",  # 中国人民银行
            "http://www.csrc.gov.cn/",  # 中国证监会
            "https://finance.sina.com.cn/stock/"  # 新浪财经
        ]
        results = await crawler.crawl_urls(test_urls, max_concurrency=2)
        print(f"成功爬取了 {len(results)} 个网页")
        
    asyncio.run(test()) 