# Stocks Investment Analysis System

一个基于 AI 的智能股票投资分析平台，整合实时行情数据、搜索引擎和大型语言模型，提供专业的投资建议和市场分析。

## 功能特性

- **实时行情数据** - 通过 AKShare 获取 A 股实时行情、财务数据和 K 线图表
- **AI 驱动分析** - 基于 MiniMax 大型语言模型的智能股票与市场分析
- **多源搜索** - 支持 Google、百度和 MiniMax 搜索引擎获取最新资讯
- **批量处理** - 支持单只股票深度分析、批量分析和整体市场分析
- **风险偏好定制** - 低、中、高三种风险偏好设置，生成个性化投资建议
- **流式响应** - SSE 流式输出，实时展示分析进度
- **Web 界面** - 基于 React + Ant Design 的现代化前端界面
- **RESTful API** - FastAPI 后端，提供完整的 API 服务

## 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                           前端 (React)                              │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐       │
│  │ Dashboard │  │  Quotes   │  │  Analysis │  │  Batch    │       │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘       │
│        └──────────────┴──────────────┴──────────────┘               │
│                          ┌─────────────────────┐                    │
│                          │   API Client        │                    │
│                          └──────────┬──────────┘                    │
└─────────────────────────────────────┼───────────────────────────────┘
                                       │ HTTPS/JSON
                                       │
┌─────────────────────────────────────┼───────────────────────────────┐
│                             后端 (FastAPI)                         │
│                              ┌─────────────┐                        │
│                              │   CORS +    │                        │
│                              │  Middleware │                        │
│                              └──────┬──────┘                        │
│     ┌──────────────────────────────┼────────────────────────────┐  │
│     │                              │                            │  │
│  ┌──┴───┐  ┌───────────┐  ┌───────┴───────┐  ┌─────────────┐  │  │
│  │行情数据│  │股票分析  │  │  批量分析    │  │  任务管理   │  │  │
│  │ API   │  │  API     │  │     API      │  │    API      │  │  │
│  └───┬───┘  └────┬─────┘  └───────┬───────┘  └──────┬──────┘  │  │
│      │           │                │                 │         │  │
└──────┼───────────┼────────────────┼─────────────────┼─────────┼──┘
       │           │                │                 │         │
┌──────┼───────────┼────────────────┼─────────────────┼─────────┼──┐
│  ┌───▼───┐  ┌────▼─────┐  ┌───────▼───────┐  ┌─────▼─────┐   │  │
│  │AKShare│  │StockAgent│  │LLMProcessor  │  │DataProvider│   │  │
│  └───────┘  └──────────┘  └───────┬───────┘  └───────────┘   │  │
│                                    │                            │  │
│                          ┌───────────┴───────────┐              │  │
│                          │  Search Engine       │              │  │
│                          │ (Google/Baidu/MiniMax)│              │  │
│                          └───────────┬───────────┘              │  │
│                                      │                          │  │
└──────────────────────────────────────┼──────────────────────────┼──┘
                                       │                          │
                              ┌────────▼────────┐        ┌────────▼────────┐
                              │  MiniMax API    │        │   AKShare API   │
                              │  (LLM + Search) │        │  (股票数据源)    │
                              └─────────────────┘        └─────────────────┘
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- MiniMax API Key

### 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/your-org/stocks.git
cd stocks
```

#### 2. 后端安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 前端安装

```bash
cd web
npm install
```

#### 4. 配置环境变量

复制 `.env.example` 到 `.env` 并修改配置：

```bash
cp .env.example .env
```

`.env` 文件内容：

```env
# MiniMax LLM 配置
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.minimaxi.com/v1
LLM_MODEL=MiniMax-M2.7-highspeed
```

#### 5. 启动服务

**启动后端：**

```bash
# 方式一：直接运行
python run_api.py

# 方式二：使用 uvicorn
uvicorn src.api.routes:create_app --reload --host 0.0.0.0 --port 8000
```

**启动前端：**

```bash
cd web
npm run dev
```

访问 http://localhost:5173

## 项目目录结构

```
stocks/
├── data/                    # 数据存储目录
├── docs/                    # 文档目录
│   ├── architecture.md      # 系统架构文档
│   ├── deployment.md       # 部署文档
│   └── ...
├── examples/                # 示例代码
├── logs/                    # 日志文件
├── results/                 # 分析结果
├── src/                     # 后端源代码
│   ├── api/                 # API 模块
│   │   ├── middleware.py    # 中间件（CORS、日志）
│   │   ├── routes.py        # 路由定义
│   │   └── schemas.py       # Pydantic 模型
│   ├── config.py            # 配置文件
│   ├── crawler.py           # 网页爬虫
│   ├── data_provider.py    # AKShare 数据封装
│   ├── llm_processor.py    # LLM 处理器
│   ├── logging_config.py    # 日志配置
│   ├── main.py              # CLI 入口
│   ├── prompts.py           # 提示词模板
│   ├── search_engine.py    # 搜索引擎
│   ├── stock_agent.py      # 核心分析 Agent
│   └── utils.py             # 工具函数
├── tests/                   # 测试用例
├── web/                     # 前端源代码
│   ├── src/
│   │   ├── pages/           # 页面组件
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Quotes.tsx
│   │   │   └── BatchAnalysis.tsx
│   │   ├── services/        # API 服务
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── .env.example             # 环境变量示例
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── Dockerfile
├── LICENSE
├── main.py
├── pyproject.toml
├── README.md
├── requirements.txt
├── run.py
├── run_api.py
└── setup.py
```

## API 接口概览

| 模块 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 健康检查 | GET | /api/v1/health | 服务健康状态 |
| 行情数据 | GET | /api/v1/quote/{stock_code} | 单只股票实时行情 |
| 行情数据 | GET | /api/v1/quotes/realtime | 批量实时行情 |
| 行情数据 | GET | /api/v1/financials/{stock_code} | 财务数据 |
| 行情数据 | GET | /api/v1/kline/{stock_code} | K 线数据 |
| 股票分析 | POST | /api/v1/analyze/stock | 单股分析 |
| 股票分析 | POST | /api/v1/analyze/stock/stream | 单股分析（流式） |
| 股票分析 | POST | /api/v1/analyze/market | 市场分析 |
| 股票分析 | POST | /api/v1/analyze/market/stream | 市场分析（流式） |
| 股票分析 | POST | /api/v1/analyze/batch | 批量分析 |
| 任务管理 | GET | /api/v1/tasks/{task_id} | 获取任务状态 |

完整 API 文档请访问：http://localhost:8000/docs

## 技术栈

### 后端

- **FastAPI** - 高性能 Web 框架
- **Pydantic** - 数据验证与序列化
- **AKShare** - A 股金融数据接口
- **MiniMax API** - 大型语言模型与搜索服务
- **Uvicorn** - ASGI 服务器
- **Trafilatura** - 网页内容提取
- **Pandas** - 数据处理

### 前端

- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Ant Design 5** - UI 组件库
- **Vite** - 构建工具
- **Axios** - HTTP 客戶端
- **React Router** - 路由管理
- **Recharts** - 图表库
- **React Markdown** - Markdown 渲染

## 截图

<!-- TODO: 添加 Dashboard 截图 -->
<!-- TODO: 添加 Quotes 页面截图 -->
<!-- TODO: 添加 Analysis 页面截图 -->
<!-- TODO: 添加 Batch Analysis 页面截图 -->

## 开发指南

详细开发文档请参考：

- [系统架构文档](docs/architecture.md)
- [部署文档](docs/deployment.md)

## 测试

```bash
# 后端测试
pytest tests/ -v

# 前端测试（Playwright E2E）
cd web
npm run test
```

## 贡献指南

欢迎提交 Pull Request！请参考 [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - 详见 [LICENSE](LICENSE) 文件

## 免责声明

本工具仅供研究和参考，不构成投资建议。投资有风险，决策需谨慎。
