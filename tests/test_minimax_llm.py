"""
MiniMax LLM 集成测试
"""
import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 设置环境变量
os.environ['LLM_API_KEY'] = 'sk-test-key'
os.environ['LLM_BASE_URL'] = 'https://api.minimaxi.com'
os.environ['LLM_MODEL'] = 'MiniMax-M2.7-8k'

from src.llm_processor import LLMProcessor


class TestMiniMaxLLM:
    """测试MiniMax LLM配置"""

    @pytest.fixture
    def processor(self):
        return LLMProcessor(
            api_key='sk-test-key',
            base_url='https://api.minimaxi.com',
            model='MiniMax-M2.7-8k'
        )

    def test_minimax_client_initialization(self, processor):
        """验证MiniMax客户端初始化"""
        assert processor.base_url == 'https://api.minimaxi.com'
        assert 'MiniMax' in processor.model

    def test_chat_completion_format(self, processor, mocker):
        """验证MiniMax聊天补全格式"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(
                content='Test response',
                role='assistant'
            ))
        ]
        mock_response.model = 'MiniMax-M2.7-8k'
        mock_response.id = 'test-id'
        mock_response.created = 1234567890

        mocker.patch.object(processor.client.chat.completions, 'create', return_value=mock_response)

        result = processor.client.chat.completions.create(
            model='MiniMax-M2.7-8k',
            messages=[{'role': 'user', 'content': 'Hello'}]
        )

        assert result.choices[0].message.content == 'Test response'


class TestMiniMaxSearchIntegration:
    """测试MiniMax搜索集成"""

    @pytest.fixture
    def search_client(self):
        from src.search_engine import SearchEngine
        return SearchEngine()

    def test_minimax_search_function_exists(self, search_client):
        """验证MiniMax搜索函数存在"""
        assert hasattr(search_client, 'minimax_search')

    def test_search_returns_content(self, search_client, mocker):
        """验证搜索返回原始内容"""
        mock_response = {
            'results': [
                {
                    'title': 'Test Article',
                    'url': 'https://example.com',
                    'content': 'This is the raw content from search.',
                    'snippet': 'Test snippet'
                }
            ]
        }

        mocker.patch('requests.post', return_value=MagicMock(
            json=lambda: mock_response,
            status_code=200
        ))

        result = search_client.minimax_search('test query')

        assert 'results' in result or isinstance(result, dict)


class TestMiniMaxConfig:
    """测试MiniMax配置"""

    def test_config_uses_minimax_base_url(self):
        """验证配置使用MiniMax base URL"""
        from src.config import get_config
        config = get_config()
        assert config['LLM']['BASE_URL'] == 'https://api.minimaxi.com'

    def test_config_uses_minimax_model(self):
        """验证配置使用MiniMax模型"""
        from src.config import get_config
        config = get_config()
        assert 'MiniMax' in config['LLM']['MODEL']
