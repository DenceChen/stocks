"""
搜索引擎模块 - 用于从Google和百度获取相关信息的URL
"""
import logging
import time
import requests
from typing import List, Dict, Any
from googlesearch import search as google_search
from baidusearch.baidusearch import search as baidu_search
from bs4 import BeautifulSoup

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
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
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
    
    def google_search_with_metadata(self, query: str) -> List[Dict[str, str]]:
        """
        使用Google搜索获取URL、标题和摘要
        
        Args:
            query: 搜索关键词
            
        Returns:
            包含url、title、abstract的字典列表
        """
        logger.info(f"Google搜索(含元数据): {query}")
        try:
            urls = self.google_search(query)
            results = []
            
            for url in urls:
                # 获取标题和摘要
                try:
                    title, abstract = self._fetch_title_and_description(url)
                    results.append({
                        'url': url,
                        'title': title,
                        'abstract': abstract
                    })
                except Exception as e:
                    logger.warning(f"获取网页元数据失败: {url}, 错误: {str(e)}")
                    # 如果获取失败，也添加到结果中，但摘要设为空
                    results.append({
                        'url': url,
                        'title': url,  # 使用URL作为标题
                        'abstract': ""
                    })
                    
                # 避免过快请求
                time.sleep(0.5)
                
            logger.info(f"Google搜索(含元数据)成功: 获取了 {len(results)} 个结果")
            return results
        except Exception as e:
            logger.error(f"Google搜索(含元数据)出错: {str(e)}")
            return []
    
    def _fetch_title_and_description(self, url: str) -> tuple:
        """
        获取网页的标题和描述
        
        Args:
            url: 网页URL
            
        Returns:
            (标题, 描述)元组
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取标题
            title = soup.title.text.strip() if soup.title else url
            
            # 获取描述
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            og_desc = soup.find('meta', attrs={'property': 'og:description'})
            description = ""
            
            if meta_desc and meta_desc.get('content'):
                description = meta_desc['content']
            elif og_desc and og_desc.get('content'):
                description = og_desc['content']
            else:
                # 如果没有描述标签，获取页面前200个字符作为摘要
                text = soup.get_text()
                description = ' '.join(text.split())[:200] + "..."
                
            return title, description
            
        except Exception as e:
            logger.error(f"获取网页元数据失败: {url}, 错误: {str(e)}")
            return url, ""  # 返回URL作为标题，描述为空
            
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
    
    def get_search_results_with_metadata(self, queries: List[str], method: str = "google") -> List[Dict[str, str]]:
        """
        批量搜索并获取包含元数据的结果
        
        Args:
            queries: 搜索关键词列表
            method: 搜索方法，'google'或'baidu'
            
        Returns:
            包含url、title、abstract的字典列表
        """
        all_results = []
        for query in queries:
            if method.lower() == "google":
                results = self.google_search_with_metadata(query)
            else:
                results = self.baidu_search(query)
                
            all_results.extend(results)
            time.sleep(self.sleep_interval)  # 避免过快搜索被限制
            
        # 去重 (基于URL)
        unique_results = []
        seen_urls = set()
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
                
        return unique_results
            
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
    
    # 测试Google搜索(含元数据)
    print("\n测试Google搜索(含元数据):")
    results = engine.google_search_with_metadata("大A股市场最新行情")
    for result in results:
        print(f"标题: {result['title']}")
        print(f"摘要: {result['abstract']}")
        print(f"链接: {result['url']}")
        print("-" * 40)
        
    # 测试百度搜索
    print("\n测试百度搜索:")
    results = engine.baidu_search("近期上涨股票")
    for result in results:
        print(f"标题: {result['title']}")
        print(f"摘要: {result['abstract']}")
        print(f"链接: {result['url']}")
        print("-" * 40) 