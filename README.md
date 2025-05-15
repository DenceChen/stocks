# 股票投资Agent

一个自动化的股票投资分析工具，能够自动搜索、爬取和分析股票相关信息，并生成专业的投资建议。

## 项目特点

- **自动化搜索**：利用Google和百度搜索引擎获取最新的股票相关信息
- **智能爬虫**：使用trafilatura高效爬取网页内容，自动提取关键信息
- **专业分析**：利用大型语言模型分析海量信息，生成专业的投资分析
- **综合建议**：提供全面、具体、可操作的投资建议，包括买入价格、止损点等
- **批量处理**：支持单只股票深度分析和多只股票批量分析
- **风险偏好**：支持低、中、高三种风险偏好，提供个性化投资建议
- **详细日志**：提供彩色日志输出，方便跟踪和调试

## 安装说明

### 1. 克隆仓库

```bash
git clone https://github.com/DenceChen/stocks.git
cd stocks
```

### 2. 创建虚拟环境

#### 使用venv创建（Python内置）

```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate
```

#### 使用Conda创建

```bash
# 创建名为stock-env的新环境，指定Python版本为3.8
conda create -n stock-env python=3.8

# 激活环境
conda activate stock-env

# 如果需要退出环境
# conda deactivate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

创建一个`.env`文件，添加以下内容：

```
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

## 使用方法

### 单只股票分析

```bash
python -m stocks.src.main -s AAPL -n "Apple Inc."
```

选项说明：
- `-s, --stock`: 股票代码
- `-n, --name`: 股票名称（可选）
- `-u, --urls`: 最大处理URL数量（默认为15）
- `-r, --risk`: 投资风险偏好 (low/medium/high, 默认为low)
- `-v, --verbose`: 启用详细日志
- `-o, --output`: 指定输出目录

### 批量分析多只股票

```bash
python -m stocks.src.main -b stocks.txt
```

`stocks.txt`格式为每行一只股票，例如：
```
AAPL,Apple Inc.
MSFT,Microsoft Corporation
GOOGL,Alphabet Inc.
```

### 市场整体分析

```bash
python -m stocks.src.main -m
```

### 快速启动（交互式）

```bash
python run.py
```

## 项目结构

```
stocks/
├── data/              # 数据存储目录
├── results/           # 分析结果存储目录
├── src/               # 源代码
│   ├── __init__.py
│   ├── search_engine.py  # 搜索引擎模块
│   ├── crawler.py     # 网页爬虫模块
│   ├── llm_processor.py  # LLM处理模块
│   ├── stock_agent.py # 主Agent模块
│   ├── config.py      # 配置模块
│   ├── prompts.py     # 提示词模板
│   ├── utils.py       # 工具函数
│   └── main.py        # 主程序入口
├── .env               # 环境变量（不包含在版本控制中）
├── requirements.txt   # 依赖列表
└── README.md          # 项目说明
```

## 配置详解

可以通过修改`src/config.py`文件来自定义程序行为，主要包括：

- **搜索引擎配置**：搜索引擎选择、结果数量、搜索模板等
- **爬虫配置**：并发数、超时时间、重试策略等
- **LLM配置**：模型选择、温度参数、最大token等
- **日志配置**：日志级别、输出格式、保存路径等
- **Agent配置**：结果保存路径、缓存策略等

## 高级使用

### 自定义搜索模板

可以在`config.py`中的`SEARCH_CONFIG`部分修改搜索模板，以满足不同需求：

```python
"templates": [
    "{stock_code} {stock_name} financial results quarterly",
    "{stock_code} {stock_name} revenue profit margin",
    # 添加更多自定义模板
]
```

### 调整LLM参数

可以在`config.py`中修改LLM相关参数，以控制分析的深度和创造性：

```python
"LLM_CONFIG": {
    "DEFAULT_MODEL": "gpt-4-turbo",
    "TEMPERATURE": 0.2,  # 调低更保守，调高更有创造性
    # 更多参数
}
```

### 自定义风险偏好

系统支持三种风险偏好设置，通过`-r`或`--risk`参数指定：

- **low**: 低风险偏好，更注重资金安全和稳定收益
- **medium**: 中等风险偏好，平衡收益与风险
- **high**: 高风险偏好，追求高收益，能承受较大波动

## 常见问题

1. **搜索引擎访问受限**：可能需要使用代理或降低请求频率
2. **网页爬取失败**：部分网站可能有反爬机制，可尝试调整headers或使用备用方法
3. **分析不够深入**：可以尝试修改提示词模板或增加搜索范围
4. **API密钥问题**：确保已设置正确的LLM_API_KEY环境变量或在.env文件中配置

## 贡献指南

欢迎提交Pull Request或Issue！贡献前请确保：

1. 代码风格符合PEP 8
2. 添加适当的注释和文档
3. 所有测试通过

## 许可证

MIT License

## 免责声明

本工具仅供研究和参考，不构成投资建议。投资有风险，决策需谨慎。用户应当根据自身情况做出判断，项目作者不对因使用本工具产生的任何损失负责。 