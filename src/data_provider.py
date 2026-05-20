"""
数据提供模块 - 通过AKShare获取股票行情和财务数据
"""
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

try:
    import akshare as ak
    import pandas as pd
except ImportError:
    ak = None
    pd = None

logger = logging.getLogger(__name__)

@dataclass
class StockQuote:
    """股票行情数据"""
    stock_code: str
    stock_name: str
    current_price: float
    change_percent: float
    volume: int
    timestamp: str

@dataclass
class FinancialData:
    """财务数据"""
    stock_code: str
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    roe: Optional[float]
    debt_ratio: Optional[float]
    revenue_growth: Optional[float]
    profit_growth: Optional[float]

class DataProvider:
    """AKShare数据源封装"""

    def __init__(self):
        if ak is None:
            raise ImportError("akshare is required. Install with: pip install akshare")
        if pd is None:
            raise ImportError("pandas is required. Install with: pip install pandas")
        self._session_cache: Dict[str, Any] = {}

    async def get_quote(self, stock_code: str) -> Optional[StockQuote]:
        """获取实时行情"""
        try:
            df = ak.stock_zh_a_spot_em()
            row = df[df['代码'] == stock_code]

            if row.empty:
                logger.warning(f"Stock {stock_code} not found")
                return None

            row = row.iloc[0]
            return StockQuote(
                stock_code=stock_code,
                stock_name=str(row.get('名称', '')),
                current_price=float(row.get('最新价', 0)),
                change_percent=float(row.get('涨跌幅', 0)),
                volume=int(row.get('成交量', 0)),
                timestamp=pd.Timestamp.now().isoformat() if pd else ''
            )
        except Exception as e:
            logger.error(f"Failed to get quote for {stock_code}: {e}")
            return None

    async def get_kline(self, stock_code: str, period: str = "daily",
                        adjust: str = "qfq") -> Optional[Any]:
        """获取K线数据"""
        cache_key = f"{stock_code}_{period}_{adjust}"
        if cache_key in self._session_cache:
            return self._session_cache[cache_key]

        try:
            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period=period,
                adjust=adjust
            )
            self._session_cache[cache_key] = df
            return df
        except Exception as e:
            logger.error(f"Failed to get kline for {stock_code}: {e}")
            return None

    async def get_financials(self, stock_code: str) -> Optional[FinancialData]:
        """获取财务数据"""
        try:
            df = ak.stock_financial_analysis_indicator(symbol=stock_code)
            if df is None or df.empty:
                return None

            latest = df.iloc[0]
            return FinancialData(
                stock_code=stock_code,
                pe_ratio=float(latest.get('市盈率', 0)) if pd.notna(latest.get('市盈率', 0)) else None,
                pb_ratio=float(latest.get('市净率', 0)) if pd.notna(latest.get('市净率', 0)) else None,
                roe=float(latest.get('净资产收益率', 0)) if pd.notna(latest.get('净资产收益率', 0)) else None,
                debt_ratio=float(latest.get('资产负债率', 0)) if pd.notna(latest.get('资产负债率', 0)) else None,
                revenue_growth=float(latest.get('营收增长率', 0)) if pd.notna(latest.get('营收增长率', 0)) else None,
                profit_growth=float(latest.get('利润增长率', 0)) if pd.notna(latest.get('利润增长率', 0)) else None,
            )
        except Exception as e:
            logger.error(f"Failed to get financials for {stock_code}: {e}")
            return None

    async def get_realtime_quotes(self, stock_codes: List[str]) -> Dict[str, StockQuote]:
        """批量获取实时行情"""
        quotes = {}
        for code in stock_codes:
            quote = await self.get_quote(code)
            if quote:
                quotes[code] = quote
        return quotes
