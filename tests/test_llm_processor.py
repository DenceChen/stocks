"""
LLMProcessor单元测试
"""
import pytest
import json
from unittest.mock import patch, MagicMock

# Set environment before imports
import os
os.environ['LLM_API_KEY'] = 'test-key'

from src.llm_processor import LLMProcessor


class TestLLMProcessorStructuredOutput:
    """测试LLMProcessor结构化输出"""

    @pytest.fixture
    def processor(self):
        return LLMProcessor(api_key="test-key")

    def test_build_summary_text(self, processor):
        """测试_build_summary_text方法"""
        docs = [
            {"title": "Test Doc", "url": "http://example.com", "extracted_info": "Test info"}
        ]
        result = processor._build_summary_text(docs)
        assert "Test Doc" in result
        assert "http://example.com" in result

    def test_build_summary_text_truncation(self, processor):
        """测试_build_summary_text截断功能"""
        docs = [
            {"title": f"Doc {i}", "url": f"http://example.com/{i}",
             "extracted_info": "x" * 1000}
            for i in range(20)
        ]
        result = processor._build_summary_text(docs)
        assert len(result) <= 14500  # 14000 + buffer

    def test_generate_investment_advice_structured_with_mock(self, processor, mocker):
        """测试结构化输出方法"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(
                content=json.dumps({
                    "summary": "Test summary",
                    "risk_assessment": {"level": "medium", "factors": ["factor1"]},
                    "recommendations": [{"action": "买入", "target_price": "100"}],
                    "indicators": {"pe_ratio": 20.5},
                    "sources": ["http://example.com"]
                })
            ))
        ]
        mocker.patch.object(processor.client.chat.completions, 'create', return_value=mock_response)

        result = processor.generate_investment_advice_structured(
            extracted_docs=[{"title": "Test", "url": "http://example.com", "extracted_info": "test info"}],
            risk_preference="medium"
        )

        assert isinstance(result, dict)
        assert "summary" in result
        assert result["summary"] == "Test summary"

    def test_generate_investment_advice_structured_empty_docs(self, processor):
        """测试空文档列表"""
        result = processor.generate_investment_advice_structured([], risk_preference="low")
        assert "error" in result

    def test_generate_investment_advice_structured_json_parse_error(self, processor, mocker):
        """测试JSON解析失败时的降级处理"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="not valid json"))
        ]
        mocker.patch.object(processor.client, 'chat', return_value=mock_response)

        result = processor.generate_investment_advice_structured(
            extracted_docs=[{"title": "Test", "url": "http://example.com", "extracted_info": "test"}],
            risk_preference="low"
        )

        assert "error" in result or "raw_content" in result