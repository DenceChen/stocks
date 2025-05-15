#!/usr/bin/env python3
"""
简单的导入测试文件，用于验证安装是否正确
"""
import os
import sys
import unittest

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

class TestImports(unittest.TestCase):
    """测试所有关键模块能否正常导入"""
    
    def test_import_config(self):
        """测试配置模块导入"""
        from src.config import get_config
        config = get_config()
        self.assertIsNotNone(config)
        self.assertIn("DATA_DIR", config)
        self.assertIn("AGENT_CONFIG", config)
    
    def test_import_stock_agent(self):
        """测试StockAgent模块导入"""
        from src.stock_agent import StockAgent
        self.assertTrue(callable(StockAgent))
    
    def test_import_utils(self):
        """测试工具函数导入"""
        from src.utils import Logger, print_colored_title, Colors
        self.assertIsNotNone(Logger)
        self.assertTrue(callable(print_colored_title))
        self.assertIsNotNone(Colors)
        
    def test_import_prompts(self):
        """测试提示词模板导入"""
        from src.prompts import (
            INFO_EXTRACTION_SYSTEM_PROMPT,
            INVESTMENT_ADVICE_SYSTEM_PROMPT
        )
        self.assertIsInstance(INFO_EXTRACTION_SYSTEM_PROMPT, str)
        self.assertIsInstance(INVESTMENT_ADVICE_SYSTEM_PROMPT, str)

if __name__ == "__main__":
    unittest.main() 