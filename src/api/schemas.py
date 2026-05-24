"""
Pydantic 模型定义 - API 请求和响应数据结构
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


# ============ 响应格式 ============

class ApiResponse(BaseModel):
    """统一 API 响应格式"""
    success: bool = True
    data: Optional[Any] = None
    error: Optional[Dict[str, str]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ============ 行情数据 ============

class StockQuoteResponse(BaseModel):
    """股票行情响应"""
    stock_code: str
    stock_name: str
    current_price: float
    change_percent: float
    volume: int
    timestamp: str


class FinancialDataResponse(BaseModel):
    """财务数据响应"""
    stock_code: str
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    debt_ratio: Optional[float] = None
    revenue_growth: Optional[float] = None
    profit_growth: Optional[float] = None


class KlineDataResponse(BaseModel):
    """K线数据响应"""
    stock_code: str
    dates: List[str]
    prices: List[float]
    volumes: List[int]


class BatchQuotesResponse(BaseModel):
    """批量行情响应"""
    quotes: Dict[str, StockQuoteResponse]


# ============ 分析请求 ============

class StockAnalysisRequest(BaseModel):
    """单股分析请求"""
    stock_code: str = Field(..., min_length=6, max_length=6, description="股票代码")
    stock_name: Optional[str] = Field(None, description="股票名称")
    risk_preference: str = Field("low", pattern="^(low|medium|high)$", description="风险偏好")
    max_urls: int = Field(15, ge=5, le=50, description="最大处理URL数量")


class MarketAnalysisRequest(BaseModel):
    """市场分析请求"""
    search_queries: Optional[List[str]] = Field(None, description="自定义搜索关键词")
    risk_preference: str = Field("low", pattern="^(low|medium|high)$", description="风险偏好")
    max_urls: int = Field(20, ge=5, le=50, description="最大处理URL数量")


class BatchAnalysisRequest(BaseModel):
    """批量分析请求"""
    stocks: List[Dict[str, str]] = Field(..., min_items=1, max_items=50, description="股票列表")
    risk_preference: str = Field("low", pattern="^(low|medium|high)$", description="风险偏好")
    max_urls_per_stock: int = Field(10, ge=5, le=30, description="每只股票最大URL数量")


# ============ 分析响应 ============

class StockAnalysisResponse(BaseModel):
    """单股分析响应"""
    stock_code: str
    stock_name: Optional[str] = None
    recommendation: str
    quote: Optional[StockQuoteResponse] = None
    financials: Optional[FinancialDataResponse] = None
    processing_time: float
    sources: List[str]
    risk_preference: str
    timestamp: str


class MarketAnalysisResponse(BaseModel):
    """市场分析响应"""
    recommendation: str
    sources: List[str]
    timestamp: str
    output_file: Optional[str] = None


class BatchAnalysisResult(BaseModel):
    """批量分析单项结果"""
    stock_code: str
    stock_name: Optional[str] = None
    recommendation: Optional[str] = None
    error: Optional[str] = None
    status: str  # "success" or "error"


class BatchAnalysisResponse(BaseModel):
    """批量分析响应"""
    task_id: str
    status: str  # "pending" or "processing" or "completed" or "error"
    results: Optional[List[BatchAnalysisResult]] = None
    total_count: int
    success_count: int = 0
    error_count: int = 0


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    status: str
    progress: Optional[float] = None
    results: Optional[List[BatchAnalysisResult]] = None
    error: Optional[str] = None


# ============ 健康检查 ============

class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str = "ok"
    version: str = "1.0.0"
    timestamp: str
