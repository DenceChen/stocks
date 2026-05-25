# 股票投资分析 Web 系统架构设计

## 1. 系统概述

本系统为股票投资分析 Web 应用，提供市场分析、个股分析、批量分析、实时行情等功能。

**技术栈**:
- 后端: Python + FastAPI/Flask
- 前端: React + TypeScript (推荐) 或纯 HTML/JS/CSS (轻量)
- 数据源: AKShare (行情/财务) + MiniMax API (搜索/LLM)

---

## 2. 页面布局与组件结构

### 2.1 页面结构

```
┌─────────────────────────────────────────────────────────┐
│ Header: Logo + 导航栏 + 用户信息                          │
├───────────┬─────────────────────────────────────────────┤
│           │                                             │
│  Sidebar  │              Main Content                   │
│  (侧边栏)  │              (主内容区)                     │
│           │                                             │
│  - 首页    │   ┌─────────────────────────────────────┐   │
│  - 个股分析 │   │ 分析卡片 (K线图/财务数据/投资建议)      │   │
│  - 市场分析 │   └─────────────────────────────────────┘   │
│  - 批量分析 │                                             │
│  - 实时行情 │   ┌─────────────────────────────────────┐   │
│  - 我的收藏 │   │ 数据表格 (股票列表/历史记录)            │   │
│           │   └─────────────────────────────────────┘   │
│           │                                             │
└───────────┴─────────────────────────────────────────────┘
```

### 2.2 核心页面

| 页面 | 功能 | 主要组件 |
|------|------|----------|
| 首页/仪表盘 | 市场概览、我的持仓、快速分析入口 | MarketOverview, QuickActions, RecentAnalysis |
| 个股分析 | 输入股票代码、查看分析结果 | StockSearch, StockChart, FinancialTable, RecommendationCard |
| 市场分析 | 行业板块分析、资金流向、热点追踪 | SectorHeatmap, FundFlow, HotStocks |
| 批量分析 | 批量输入股票、多任务并行分析 | BatchStockInput, ProgressBar, BatchResultTable |
| 实时行情 | A股实时行情、涨跌幅榜、条件筛选 | RealtimeQuoteTable, FilterPanel, SortableHeader |
| 分析历史 | 历史分析记录、收藏的投资建议 | HistoryList, FavoritePanel |

### 2.3 组件层级

```
App
├── Header
│   ├── Logo
│   ├── Navigation (NavLink)
│   └── UserMenu
├── Sidebar
│   ├── NavMenu
│   └── QuickStats
└── MainContent
    ├── DashboardPage
    │   ├── MarketOverviewCard
    │   ├── QuickActionGrid
    │   └── RecentAnalysisList
    ├── StockAnalysisPage
    │   ├── StockSearchBar
    │   ├── StockInfoCard
    │   │   ├── StockChart (K线)
    │   │   └── KeyMetrics
    │   ├── FinancialTable
    │   └── RecommendationCard
    ├── MarketAnalysisPage
    │   ├── SectorHeatmap
    │   ├── FundFlowChart
    │   └── HotStocksTable
    ├── BatchAnalysisPage
    │   ├── StockInputArea
    │   ├── AnalysisProgress
    │   └── BatchResultTable
    ├── RealtimeQuotePage
    │   ├── FilterBar
    │   └── QuoteTable
    └── HistoryPage
        ├── FilterBar
        └── HistoryList
```

---

## 3. 前端技术选择

### 3.1 推荐方案: React + TypeScript

**优势**:
- 组件化架构，代码复用性高
- TypeScript 类型安全，适合复杂数据流
- 生态丰富 (图表库、UI 组件库成熟)
- 适合复杂交互 (实时行情、WebSocket)

**关键依赖**:
```json
{
  "react": "^18.2.0",
  "typescript": "^5.0.0",
  "recharts": "^2.10.0",         // 图表
  "antd": "^5.12.0",             // UI 组件库
  "@tanstack/react-query": "^5.0.0", // 数据请求/缓存
  "zustand": "^4.4.0",           // 状态管理
  "react-router-dom": "^6.20.0"  // 路由
}
```

### 3.2 备选方案: 纯 HTML/JS/CSS

适用于简单原型或轻量级展示页面。

---

## 4. 后端 API 设计

### 4.1 技术选型: FastAPI

**优势**:
- 异步支持好，适合 I/O 密集型任务
- 自动生成 OpenAPI 文档
- 类型安全，与 Python 后端无缝衔接
- 高性能 (基于 Starlette)

### 4.2 API 端点

| 方法 | 路径 | 功能 | 请求体 | 响应 |
|------|------|------|--------|------|
| `POST` | `/api/v1/analyze/stock` | 单股分析 | `{stock_code, stock_name?, risk_preference, max_urls?}` | `{recommendation, quote, financials, sources, processing_time}` |
| `POST` | `/api/v1/analyze/market` | 市场分析 | `{search_queries?, risk_preference, max_urls?}` | `{recommendation, sources, timestamp}` |
| `POST` | `/api/v1/analyze/batch` | 批量分析 | `{stocks: [{code, name}], risk_preference}` | `{results: [{stock_code, recommendation, status}]}` |
| `GET` | `/api/v1/quote/{stock_code}` | 实时行情 | - | `{stock_code, stock_name, current_price, change_percent, volume, timestamp}` |
| `GET` | `/api/v1/financials/{stock_code}` | 财务数据 | - | `{pe_ratio, pb_ratio, roe, debt_ratio, revenue_growth, profit_growth}` |
| `GET` | `/api/v1/kline/{stock_code}` | K线数据 | `?period=daily&adjust=qfq` | `{dates, prices, volumes}` |
| `GET` | `/api/v1/quotes/realtime` | 批量实时行情 | `?codes=600000,000001` | `{stock_code: quote, ...}` |
| `GET` | `/api/v1/health` | 健康检查 | - | `{status: "ok"}` |

### 4.3 API 响应格式

**成功响应**:
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2026-05-24T10:30:00Z"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "STOCK_NOT_FOUND",
    "message": "股票代码不存在"
  },
  "timestamp": "2026-05-24T10:30:00Z"
}
```

### 4.4 请求/响应示例

**单股分析请求**:
```json
POST /api/v1/analyze/stock
{
  "stock_code": "600519",
  "stock_name": "贵州茅台",
  "risk_preference": "low",
  "max_urls": 15
}
```

**单股分析响应**:
```json
{
  "success": true,
  "data": {
    "stock_code": "600519",
    "stock_name": "贵州茅台",
    "recommendation": "建议持有...",
    "quote": {
      "current_price": 1680.00,
      "change_percent": 1.25,
      "volume": 3250000
    },
    "financials": {
      "pe_ratio": 32.5,
      "pb_ratio": 10.2,
      "roe": 45.6
    },
    "processing_time": 12.5,
    "sources": ["https://...", "https://..."]
  }
}
```

---

## 5. 数据流设计

### 5.1 整体数据流

```
┌──────────────────────────────────────────────────────────────────────┐
│                           Frontend (React)                            │
│                                                                       │
│   User Input ──► API Client ──► Loading State ──► UI Update         │
│                          │                                            │
│                          ▼                                            │
│                   React Query Cache                                   │
└──────────────────────────│────────────────────────────────────────────┘
                           │ HTTP Request
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        Backend (FastAPI)                              │
│                                                                       │
│   API Endpoint ──► Request Validation ──► Business Logic             │
│                          │                                            │
│                          ▼                                            │
│                  StockAgent.analyze_*()                               │
│                          │                                            │
│         ┌────────────────┼────────────────┐                         │
│         ▼                ▼                ▼                           │
│   SearchEngine    WebCrawler    LLMProcessor                         │
│   (搜索URL)       (爬取内容)     (分析内容)                             │
│         │                │                │                           │
│         └────────────────┼────────────────┘                         │
│                          ▼                                            │
│                  DataProvider (AKShare)                                │
│                  (行情/财务数据)                                       │
└──────────────────────────│────────────────────────────────────────────┘
                           │
                           ▼
                    返回分析结果
```

### 5.2 核心模块依赖

```
DataProvider (AKShare)
       │
       ▼
SearchEngine (Google/Baidu/MiniMax)
       │
       ▼
WebCrawler (爬取网页)
       │
       ▼
LLMProcessor (MiniMax API 分析)
       │
       ▼
StockAgent (编排工作流)
       │
       ▼
FastAPI Routes (API 接口)
```

### 5.3 异步任务流程 (批量分析)

```
┌─────────────────────────────────────────────────────────┐
│  批量分析请求                                           │
│  POST /api/v1/analyze/batch                            │
└────────────────────────┬──────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  创建任务 ID，返回 202 Accepted                          │
│  {task_id: "uuid-xxx", status: "pending"}              │
└────────────────────────┬──────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  前端轮询: GET /api/v1/tasks/{task_id}                  │
│                          │                              │
│         ┌────────────────┼────────────────┐           │
│         ▼                ▼                ▼             │
│   Stock-1 分析    Stock-2 分析    Stock-N 分析          │
│   (并发执行)       (并发执行)       (并发执行)           │
│         │                │                │             │
│         └────────────────┼────────────────┘           │
│                          ▼                              │
│              汇总结果，存储到数据库                       │
└────────────────────────┬──────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  前端获取: GET /api/v1/tasks/{task_id}                  │
│  返回: {status: "completed", results: [...]}           │
└─────────────────────────────────────────────────────────┘
```

---

## 6. 项目目录结构

```
stocks/
├── src/                    # Python 后端源码
│   ├── __init__.py
│   ├── main.py            # Flask/FastAPI 入口
│   ├── stock_agent.py     # Agent 主逻辑
│   ├── search_engine.py   # 搜索引擎
│   ├── crawler.py         # 网页爬虫
│   ├── llm_processor.py   # LLM 处理
│   ├── data_provider.py   # AKShare 数据
│   ├── config.py          # 配置
│   └── api/
│       ├── __init__.py
│       ├── routes.py       # API 路由
│       ├── schemas.py     # Pydantic 模型
│       └── middleware.py  # 中间件
│
├── web/                    # 前端源码 (React)
│   ├── public/
│   ├── src/
│   │   ├── components/    # React 组件
│   │   ├── pages/         # 页面
│   │   ├── hooks/         # 自定义 Hooks
│   │   ├── services/      # API 客户端
│   │   ├── stores/        # 状态管理
│   │   ├── types/         # TypeScript 类型
│   │   └── utils/         # 工具函数
│   ├── package.json
│   └── vite.config.ts
│
├── docs/                   # 文档
│   └── web-architecture.md
│
└── docker-compose.yml       # 容器编排
```

---

## 7. WebSocket 实时推送 (可选)

用于实时行情和任务进度推送:

```python
# 后端
from fastapi import WebSocket

@router.websocket("/ws/quotes")
async def quote_websocket(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await get_realtime_quotes()
        await websocket.send_json(data)
        await asyncio.sleep(5)  # 5秒推送一次

# 前端
const ws = new WebSocket("ws://localhost:8000/ws/quotes");
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateQuoteTable(data);
};
```

---

## 8. 关键技术决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 前端框架 | React + TypeScript | 组件化、类型安全、生态成熟 |
| 后端框架 | FastAPI | 异步支持、自动文档、高性能 |
| 状态管理 | Zustand + React Query | 轻量、缓存机制完善 |
| 图表库 | Recharts | React 原生、支持 K 线 |
| 实时推送 | WebSocket | 低延迟、真实时 |
| 任务队列 | Redis + Celery | 批量分析异步处理 |

---

## 9. 安全考虑

1. **API 认证**: JWT Token 或 API Key
2. **CORS**: 配置允许的域
3. **请求限流**: 防止滥用
4. **输入校验**: Pydantic 模型验证
5. **敏感信息**: 环境变量存储 API Key