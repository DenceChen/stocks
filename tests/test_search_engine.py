"""
搜索引擎模块测试用例
"""
import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.search_engine import SearchEngine

class TestSearchEngine(unittest.TestCase):
    """测试SearchEngine类"""
    
    def setUp(self):
        """每个测试方法运行前执行"""
        self.search_engine = SearchEngine()
    
    @patch('src.search_engine.requests.get')
    def test_search_google(self, mock_get):
        """测试Google搜索方法"""
        # 设置mock返回值
        mock_response = MagicMock()
        mock_response.text = '''
        <html>
            <body>
                <div class="g">
                    <a href="https://example.com">Example</a>
                </div>
                <div class="g">
                    <a href="https://test.com">Test</a>
                </div>
            </body>
        </html>
        '''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 执行搜索
        results = self.search_engine.search_google("test query")
        
        # 检查结果
        self.assertEqual(len(results), 2)
        self.assertIn("https://example.com", results)
        self.assertIn("https://test.com", results)
        
        # 验证mock被正确调用
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertIn("test+query", kwargs.get('url', args[0]))
    
    @patch('src.search_engine.requests.get')
    def test_search_baidu(self, mock_get):
        """测试百度搜索方法"""
        # 设置mock返回值
        mock_response = MagicMock()
        mock_response.text = '''
        <html>
            <body>
                <div class="result">
                    <a href="https://example.cn">Example</a>
                </div>
                <div class="result">
                    <a href="https://test.cn">Test</a>
                </div>
            </body>
        </html>
        '''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 执行搜索
        results = self.search_engine.search_baidu("测试查询")
        
        # 检查结果
        self.assertEqual(len(results), 2)
        self.assertIn("https://example.cn", results)
        self.assertIn("https://test.cn", results)
    
    @patch('src.search_engine.SearchEngine.search_google')
    @patch('src.search_engine.SearchEngine.search_baidu')
    def test_search_combined(self, mock_baidu, mock_google):
        """测试组合搜索方法"""
        # 设置mock返回值
        mock_google.return_value = ["https://example.com", "https://test.com"]
        mock_baidu.return_value = ["https://example.cn", "https://test.com"]  # 注意此处有重复URL
        
        # 执行搜索
        results = self.search_engine.search("查询词", engines=["google", "baidu"])
        
        # 检查结果
        self.assertEqual(len(results), 3)  # 应该去重
        self.assertIn("https://example.com", results)
        self.assertIn("https://test.com", results)
        self.assertIn("https://example.cn", results)
        
        # 验证两个搜索方法都被调用
        mock_google.assert_called_once_with("查询词", 10)
        mock_baidu.assert_called_once_with("查询词", 10)
    
    @patch('src.search_engine.SearchEngine.search')
    def test_search_stock_info(self, mock_search):
        """测试股票信息搜索方法"""
        # 设置mock返回值
        mock_search.return_value = ["https://finance-example.com"]
        
        # 模拟配置
        self.search_engine.config = {
            'DEFAULT_SEARCH_CATEGORIES': [
                {
                    'name': 'Test Category',
                    'templates': [
                        '{stock_code} financial',
                        '{stock_name} news'
                    ]
                }
            ]
        }
        
        # 执行搜索
        results = self.search_engine.search_stock_info("AAPL", "Apple")
        
        # 验证search方法被调用了正确的次数和参数
        self.assertEqual(mock_search.call_count, 2)
        
        # 获取所有调用参数
        calls = mock_search.call_args_list
        queries = [call[0][0] for call in calls]
        
        # 验证查询参数
        self.assertIn("AAPL financial", queries)
        self.assertIn("Apple news", queries)

if __name__ == '__main__':
    unittest.main() 