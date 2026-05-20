# 股票投资Agent优化设计方案

## 1. 项目概述

**项目名称：** stocks - 股票投资智能分析Agent
**项目类型：** Python异步命令行工具 + 可选Web界面
**核心功能：** 自动搜索、爬取、分析股票相关信息，通过LLM生成投资建议
**目标用户：** 个人投资者、金融研究人员

## 2. 现状问题

### 2.1 安全问题
- **P0** API密钥硬编码在`config.py`第38行
- 敏感信息暴露在版本控制中

### 2.2 架构问题
- **P0** `batch_analyze()`方法是同步的，但应在异步框架下并发执行
- **P1** `_search()`是同步方法被async上下文调用，可能阻塞事件循环
- **P1** 导入方式不统一（直接导入vs相对导入）

### 2.3 功能缺失
- **P1** 无真实股价数据源（K线、成交量、财务指标）
- **P1** 输出格式单一，仅支持文本
- **P2** 无技术指标计算（MACD、RSI、布林带等）
- **P2** 无投资组合回测功能
- **P3** 无Web界面

### 2.4 工程问题
- **P1** 无依赖版本锁定（requirements.txt无版本上限）
- **P2** 测试覆盖率低
- **P2** 无结构化日志和监控指标

## 3. 优化目标

### 3.1 短期目标（本次迭代）
1. 修复所有P0级别安全问题
2. 修复异步架构问题
3. 集成AKShare获取真实行情数据
4. 添加结构化JSON输出
5. 锁定依赖版本

### 3.2 中期目标（后续迭代）
1. 添加技术指标计算
2. 实现回测功能
3. 提升测试覆盖率至70%
4. 添加Web界面

## 4. 技术方案

### 4.1 安全修复
**文件：** `src/config.py`
**变更：**
```python
# 删除硬编码密钥
"API_KEY": os.getenv("LLM_API_KEY"),  # 必须从环境变量读取

# 添加.env.example作为模板
LLM_API_KEY=your_api_key_here
```

### 4.2 架构修复
**文件：** `src/stock_agent.py`

**变更1：`batch_analyze`改为async**
```python
# Before
def batch_analyze(self, stocks, ...):
    for stock in stocks:
        result = self.analyze_stock(...)  # 串行

# After
async def batch_analyze(self, stocks, ...):
    tasks = [self.analyze_stock_async(stock) for stock in stocks]
    results = await asyncio.gather(*tasks)  # 并发
```

**变更2：`_search`改为async**
```python
# Before
def _search(self, queries, method, max_urls):
    # 同步实现

# After
async def _search(self, queries, method, max_urls):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, self._search_sync, ...)
```

### 4.3 数据源集成
**新增文件：** `src/data_provider.py`
**依赖：** `akshare>=1.12.0`

**功能：**
- 获取实时股价：`get_realtime_quote(stock_code)`
- 获取K线数据：`get_kline_data(stock_code, period='daily', adjust='qfq')`
- 获取财务指标：`get_financial_data(stock_code)`

**接口设计：**
```python
class DataProvider:
    async def get_quote(self, stock_code: str) -> Dict[str, Any]:
        """获取实时行情"""

    async def get_kline(self, stock_code: str, period: str = "daily") -> pd.DataFrame:
        """获取K线数据"""

    async def get_financials(self, stock_code: str) -> Dict[str, Any]:
        """获取财务数据"""
```

### 4.4 结构化输出
**文件：** `src/llm_processor.py`
**新增：** `generate_investment_advice_structured()` 方法

**输出格式：**
```json
{
  "summary": "简短总结",
  "risk_assessment": {
    "level": "medium",
    "factors": ["因素1", "因素2"]
  },
  "recommendations": [
    {
      "action": "买入",
      "target_price": "150",
      "stop_loss": "140",
      "rationale": "理由"
    }
  ],
  "indicators": {
    "pe_ratio": 25.5,
    "roe": 15.2,
    "debt_ratio": 0.45
  },
  "sources": ["url1", "url2"]
}
```

### 4.5 依赖版本锁定
**文件：** `requirements.txt` → `pyproject.toml`

```toml
[project]
dependencies = [
    "requests>=2.25.0,<3.0.0",
    "beautifulsoup4>=4.9.3,<5.0.0",
    "openai>=1.0.0,<2.0.0",
    "akshare>=1.12.0,<2.0.0",
    "pandas>=2.0.0,<3.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
]
```

## 5. 文件变更清单

### 5.1 修改文件
| 文件 | 变更类型 | 优先级 |
|------|----------|--------|
| `src/config.py` | 删除硬编码API_KEY | P0 |
| `src/stock_agent.py` | 异步化batch_analyze | P0 |
| `src/stock_agent.py` | 修复_search异步 | P1 |
| `src/llm_processor.py` | 添加结构化输出 | P1 |
| `requirements.txt` | 添加akshare，版本锁定 | P1 |

### 5.2 新增文件
| 文件 | 说明 | 优先级 |
|------|------|--------|
| `src/data_provider.py` | AKShare数据源封装 | P1 |
| `pyproject.toml` | 依赖版本锁定 | P1 |
| `tests/test_data_provider.py` | 数据源单元测试 | P2 |
| `tests/test_stock_agent.py` | Agent异步测试 | P2 |

### 5.3 删除文件
| 文件 | 原因 |
|------|------|
| 无 | - |

## 6. 测试策略

### 6.1 单元测试
- `test_data_provider.py`: Mock AKShare API，验证数据解析
- `test_stock_agent.py`: Mock LLM和爬虫，验证异步流程
- `test_llm_processor.py`: 验证结构化输出格式

### 6.2 集成测试
- 使用VCR.py录制真实API响应
- 定时执行完整流程测试

## 7. 实施顺序

```
[Week 1]
├── Day 1-2: 安全修复 + 架构修复
├── Day 3-4: data_provider.py开发
└── Day 5: 集成测试

[Week 2]
├── Day 1-2: 结构化输出
├── Day 3-4: pyproject.toml + 测试覆盖率
└── Day 5: 代码审查 + 合并
```

## 8. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| AKShare接口不稳定 | 数据获取失败 | 添加备用数据源（Tushare） |
| 异步改造引入bug | 功能退化 | 充分单元测试覆盖 |
| LLM结构化输出格式不稳定 | 解析失败 | 添加输出验证和降级处理 |

## 9. 成功标准

- [ ] API密钥不再出现在源码中
- [ ] `batch_analyze`支持并发处理股票列表
- [ ] 新增`get_quote`方法可获取实时股价
- [ ] 新增结构化JSON输出选项
- [ ] `pyproject.toml`锁定所有依赖版本
- [ ] 测试覆盖率提升至50%以上
