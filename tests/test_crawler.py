"""
爬虫模块测试用例
"""
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.crawler import Crawler

class TestCrawler(unittest.TestCase):
    """测试Crawler类"""
    
    def setUp(self):
        """每个测试方法运行前执行"""
        self.crawler = Crawler()
    
    @patch('src.crawler.trafilatura.fetch_url')
    @patch('src.crawler.trafilatura.extract')
    def test_extract_content(self, mock_extract, mock_fetch_url):
        """测试使用trafilatura提取内容"""
        # 设置mock返回值
        mock_fetch_url.return_value = "<html><body>Test content</body></html>"
        
        # 模拟trafilatura提取的JSON结果
        mock_extract.return_value = json.dumps({
            'title': 'Test Title',
            'author': 'Test Author',
            'date': '2023-11-01',
            'text': 'This is a test article content.',
            'raw_html': '<html><body>Test content</body></html>'
        })
        
        # 执行方法
        result = self.crawler.extract_content("https://example.com")
        
        # 检查结果
        self.assertIsNotNone(result)
        self.assertEqual(result['url'], "https://example.com")
        self.assertEqual(result['title'], "Test Title")
        self.assertEqual(result['author'], "Test Author")
        self.assertEqual(result['date'], "2023-11-01")
        self.assertEqual(result['text'], "This is a test article content.")
        
        # 验证mock被正确调用
        mock_fetch_url.assert_called_once_with("https://example.com")
        mock_extract.assert_called_once()
    
    @patch('src.crawler.trafilatura.fetch_url')
    def test_extract_content_download_failure(self, mock_fetch_url):
        """测试下载失败的情况"""
        # 模拟下载失败
        mock_fetch_url.return_value = None
        
        # 执行方法
        result = self.crawler.extract_content("https://example.com")
        
        # 检查结果
        self.assertIsNone(result)
        
        # 验证mock被正确调用
        mock_fetch_url.assert_called_once_with("https://example.com")
    
    @patch('src.crawler.requests.get')
    def test_extract_basic_content(self, mock_get):
        """测试使用BeautifulSoup提取基本内容"""
        # 设置mock返回值
        mock_response = MagicMock()
        mock_response.text = '''
        <html>
            <head>
                <title>Test Page</title>
            </head>
            <body>
                <script>var x = 1;</script>
                <div>Test content</div>
                <style>.test{color:red;}</style>
            </body>
        </html>
        '''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 执行方法
        result = self.crawler.extract_basic_content("https://example.com")
        
        # 检查结果
        self.assertIsNotNone(result)
        self.assertEqual(result['url'], "https://example.com")
        self.assertEqual(result['title'], "Test Page")
        self.assertIn("Test content", result['text'])
        self.assertNotIn("var x = 1", result['text'])
        
        # 验证mock被正确调用
        mock_get.assert_called_once()
    
    @patch('src.crawler.Crawler.extract_content')
    @patch('src.crawler.Crawler.extract_basic_content')
    def test_crawl_urls(self, mock_extract_basic, mock_extract):
        """测试爬取多个URL"""
        # 设置mock返回值
        mock_extract.side_effect = [
            {
                'url': 'https://example1.com',
                'title': 'Example 1',
                'text': 'Content 1'
            },
            None,  # 第二个URL提取失败
            {
                'url': 'https://example3.com',
                'title': 'Example 3',
                'text': 'Content 3'
            }
        ]
        
        mock_extract_basic.side_effect = [
            {
                'url': 'https://example2.com',
                'title': 'Example 2',
                'text': 'Content 2'
            }
        ]
        
        # 执行方法
        urls = ['https://example1.com', 'https://example2.com', 'https://example3.com']
        results = self.crawler.crawl_urls(urls)
        
        # 检查结果
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], 'Example 1')
        self.assertEqual(results[1]['title'], 'Example 2')
        self.assertEqual(results[2]['title'], 'Example 3')
        
        # 验证mock被正确调用
        self.assertEqual(mock_extract.call_count, 3)
        self.assertEqual(mock_extract_basic.call_count, 1)
        mock_extract_basic.assert_called_once_with('https://example2.com')
    
    def test_extract_relevant_sections(self):
        """测试提取相关内容段落"""
        # 准备测试数据
        content = {
            'url': 'https://example.com',
            'title': 'Test Article',
            'text': '''
            第一段落，不包含关键词。
            
            第二段落，包含股票和投资关键词。
            
            第三段落，只包含投资关键词。
            
            第四段落，包含股票关键词。
            
            第五段落，没有关键词。
            '''
        }
        
        keywords = ['股票', '投资']
        
        # 执行方法
        result = self.crawler.extract_relevant_sections(content, keywords)
        
        # 检查结果
        self.assertIn('第二段落', result['text'])
        self.assertIn('第三段落', result['text'])
        self.assertIn('第四段落', result['text'])
        self.assertNotIn('第一段落', result['text'])
        self.assertNotIn('第五段落', result['text'])
        
        # 验证原始对象未被修改
        self.assertNotEqual(content['text'], result['text'])

if __name__ == '__main__':
    unittest.main() 