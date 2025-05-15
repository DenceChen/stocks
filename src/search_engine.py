"""
搜索引擎模块 - 用于从Google和百度获取相关信息的URL
"""
import logging
import time
from typing import List, Dict
from googlesearch import search as google_search
from baidusearch.baidusearch import search as baidu_search

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self, max_results: int = 10, sleep_interval: float = 2.0):
        """
        初始化搜索引擎
        
        Args:
            max_results: 每次搜索返回的最大结果数
            sleep_interval: 连续搜索间的睡眠时间(秒)，避免被搜索引擎限制
        """
        self.max_results = max_results
        self.sleep_interval = sleep_interval
        
    def google_search(self, query: str) -> List[str]:
        """
        使用Google搜索获取URL
        
        Args:
            query: 搜索关键词
            
        Returns:
            URL列表
        """
        logger.info(f"Google搜索: {query}")
        try:
            results = list(google_search(query, num_results=self.max_results))
            logger.info(f"Google搜索成功: 获取了 {len(results)} 个结果")
            return results
        except Exception as e:
            logger.error(f"Google搜索出错: {str(e)}")
            return []
            
    def baidu_search(self, query: str) -> List[Dict]:
        """
        使用百度搜索获取URL和摘要
        
        Args:
            query: 搜索关键词
            
        Returns:
            包含title, abstract, url的字典列表
        """
        logger.info(f"百度搜索: {query}")
        try:
            results = baidu_search(query)
            logger.info(f"百度搜索成功: 获取了 {len(results)} 个结果")
            return results
        except Exception as e:
            logger.error(f"百度搜索出错: {str(e)}")
            return []
            
    def get_urls_with_google(self, queries: List[str]) -> List[str]:
        """
        批量使用Google搜索获取URL
        
        Args:
            queries: 搜索关键词列表
            
        Returns:
            URL列表
        """
        all_urls = []
        for query in queries:
            urls = self.google_search(query)
            all_urls.extend(urls)
            time.sleep(self.sleep_interval)  # 避免过快搜索被限制
        return list(set(all_urls))  # 去重
        
    def get_urls_with_baidu(self, queries: List[str]) -> List[str]:
        """
        批量使用百度搜索获取URL
        
        Args:
            queries: 搜索关键词列表
            
        Returns:
            URL列表
        """
        all_urls = []
        for query in queries:
            results = self.baidu_search(query)
            urls = [result['url'] for result in results]
            all_urls.extend(urls)
            time.sleep(self.sleep_interval)  # 避免过快搜索被限制
        return list(set(all_urls))  # 去重

if __name__ == "__main__":
    # 测试代码
    engine = SearchEngine(max_results=5)
    
    # 测试Google搜索
    print("测试Google搜索:")
    results = engine.google_search("最近央行政策新闻")
    for url in results:
        print(url)
        
    # 测试百度搜索
    print("\n测试百度搜索:")
    results = engine.baidu_search("近期上涨股票")
    for result in results:
        print(f"标题: {result['title']}")
        print(f"摘要: {result['abstract']}")
        print(f"链接: {result['url']}")
        print("-" * 40) 