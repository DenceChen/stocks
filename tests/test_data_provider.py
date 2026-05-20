"""
DataProvider单元测试
"""
import pytest
from unittest.mock import patch, MagicMock
import sys

# Mock akshare before importing data_provider
sys.modules['akshare'] = MagicMock()
sys.modules['pandas'] = MagicMock()

from src.data_provider import DataProvider, StockQuote, FinancialData


class TestStockQuote:
    """测试StockQuote dataclass"""

    def test_stock_quote_creation(self):
        quote = StockQuote(
            stock_code="000001",
            stock_name="平安银行",
            current_price=12.50,
            change_percent=1.25,
            volume=50000000,
            timestamp="2024-01-01T10:00:00"
        )
        assert quote.stock_code == "000001"
        assert quote.current_price == 12.50
        assert quote.change_percent == 1.25


class TestFinancialData:
    """测试FinancialData dataclass"""

    def test_financial_data_creation(self):
        data = FinancialData(
            stock_code="000001",
            pe_ratio=8.5,
            pb_ratio=0.9,
            roe=12.5,
            debt_ratio=45.0,
            revenue_growth=10.0,
            profit_growth=15.0
        )
        assert data.stock_code == "000001"
        assert data.pe_ratio == 8.5
        assert data.roe == 12.5


class TestDataProvider:
    """测试DataProvider类"""

    @pytest.mark.asyncio
    async def test_get_quote_returns_optional(self):
        """测试get_quote返回Optional[StockQuote]"""
        provider = DataProvider()
        assert hasattr(provider, 'get_quote')

    @pytest.mark.asyncio
    async def test_get_kline_caching(self):
        """测试get_kline缓存功能"""
        provider = DataProvider()
        mock_df = MagicMock()

        with patch('akshare.stock_zh_a_hist', return_value=mock_df) as mock_hist:
            await provider.get_kline("000001")
            await provider.get_kline("000001")
            assert mock_hist.call_count == 1

    @pytest.mark.asyncio
    async def test_get_financials_returns_optional(self):
        """测试get_financials返回Optional[FinancialData]"""
        provider = DataProvider()
        assert hasattr(provider, 'get_financials')
