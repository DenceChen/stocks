# 测试用例库规范

## 概述

本项目使用 pytest 作为测试框架，采用 TDD（测试驱动开发）方法。每个功能开发前先写测试，测试通过后再实现功能。

## 测试结构

```
tests/
├── __init__.py              # 测试包标记
├── test_imports.py          # 导入测试
├── test_minimax_llm.py      # MiniMax LLM 集成测试
├── test_minimax_api.py      # MiniMax API 测试
├── test_search_engine.py     # 搜索引擎测试
├── test_llm_processor.py    # LLM 处理器测试
├── test_data_provider.py    # 数据提供者测试
├── test_crawler.py          # 爬虫测试
├── test_logging.py          # 日志系统测试
└── conftest.py              # pytest 配置和共享 fixtures
```

## 运行测试

### 运行所有测试
```bash
pytest tests/
```

### 运行特定测试文件
```bash
pytest tests/test_minimax_llm.py
```

### 运行特定测试类
```bash
pytest tests/test_minimax_llm.py::TestMiniMaxLLM
```

### 运行特定测试
```bash
pytest tests/test_minimax_llm.py::TestMiniMaxLLM::test_minimax_client_initialization
```

### 查看详细输出
```bash
pytest tests/ -v
```

### 生成覆盖率报告
```bash
pytest tests/ --cov=src --cov-report=html
```

## 测试用例清单

### 1. test_imports.py - 导入测试

| 测试名称 | 描述 | 预期结果 |
|---------|------|---------|
| `test_import_config` | 测试配置模块导入 | 模块成功导入 |
| `test_import_llm_processor` | 测试 LLM 处理器导入 | 模块成功导入 |
| `test_import_search_engine` | 测试搜索引擎导入 | 模块成功导入 |
| `test_import_data_provider` | 测试数据提供者导入 | 模块成功导入 |

### 2. test_minimax_llm.py - MiniMax LLM 测试

| 测试名称 | 描述 | 预期结果 |
|---------|------|---------|
| `test_minimax_client_initialization` | 验证 MiniMax 客户端初始化 | 客户端正确配置 |
| `test_chat_completion_format` | 验证聊天补全格式 | 返回正确格式 |
| `test_minimax_search_function_exists` | 验证搜索函数存在 | 方法存在 |
| `test_search_returns_content` | 验证搜索返回内容 | 返回搜索结果 |
| `test_config_uses_minimax_base_url` | 验证配置使用正确 Base URL | URL 正确 |
| `test_config_uses_minimax_model` | 验证配置使用正确模型 | 模型名称正确 |

### 3. test_search_engine.py - 搜索引擎测试

| 测试名称 | 描述 | 预期结果 |
|---------|------|---------|
| `test_search_engine_initialization` | 测试搜索引擎初始化 | 初始化成功 |
| `test_google_search` | 测试 Google 搜索 | 返回 URL 列表 |
| `test_baidu_search` | 测试百度搜索 | 返回结果列表 |
| `test_minimax_search` | 测试 MiniMax 搜索 | 返回标准化结果 |
| `test_search_with_metadata` | 测试带元数据的搜索 | 返回完整元数据 |
| `test_batch_search` | 测试批量搜索 | 返回去重结果 |

### 4. test_llm_processor.py - LLM 处理器测试

| 测试名称 | 描述 | 预期结果 |
|---------|------|---------|
| `test_llm_processor_initialization` | 测试处理器初始化 | 初始化成功 |
| `test_chat_completion` | 测试聊天补全 | 返回回复内容 |
| `test_streaming_response` | 测试流式响应 | 正确处理流式 |
| `test_error_handling` | 测试错误处理 | 正确捕获异常 |

### 5. test_data_provider.py - 数据提供者测试

| 测试名称 | 描述 | 预期结果 |
|---------|------|---------|
| `test_data_provider_initialization` | 测试数据提供者初始化 | 初始化成功 |
| `test_stock_data_retrieval` | 测试股票数据获取 | 返回数据 |
| `test_realtime_data` | 测试实时数据 | 返回实时行情 |
| `test_historical_data` | 测试历史数据 | 返回历史K线 |

### 6. test_crawler.py - 爬虫测试

| 测试名称 | 描述 | 预期结果 |
|---------|------|---------|
| `test_crawler_initialization` | 测试爬虫初始化 | 初始化成功 |
| `test_webpage_crawling` | 测试网页爬取 | 返回页面内容 |
| `test_content_extraction` | 测试内容提取 | 提取正文 |
| `test_error_recovery` | 测试错误恢复 | 重试机制 |

### 7. test_logging.py - 日志系统测试

| 测试名称 | 描述 | 预期结果 |
|---------|------|---------|
| `test_format_with_debug_level` | 测试 DEBUG 级别格式化 | 正确包含 DEBUG |
| `test_format_with_error_level` | 测试 ERROR 级别格式化 | 正确包含 ERROR |
| `test_setup_logger_returns_logger` | 测试 setup_logger 返回 | 返回 Logger 实例 |
| `test_setup_logger_with_file` | 测试带文件的日志设置 | 文件 handler 存在 |
| `test_setup_logger_does_not_duplicate_handlers` | 测试不重复添加 handler | 返回相同实例 |
| `test_get_logger_returns_logger` | 测试 get_logger 返回 | 返回 Logger 实例 |
| `test_log_api_call_without_error` | 测试记录成功 API 调用 | 正确记录参数 |
| `test_log_api_call_with_error` | 测试记录失败 API 调用 | 记录错误信息 |
| `test_log_function_call_with_args` | 测试记录带参数的函数 | 正确记录参数 |
| `test_log_function_call_with_result` | 测试记录带返回值的函数 | 正确记录结果 |
| `test_log_function_call_with_error` | 测试记录错误的函数调用 | 记录错误信息 |
| `test_get_app_logger` | 测试获取应用日志 | 返回正确 logger |
| `test_get_api_logger` | 测试获取 API 日志 | 返回正确 logger |
| `test_get_error_logger` | 测试获取错误日志 | level=ERROR |
| `test_log_level_from_env` | 测试从环境变量读取级别 | 读取正确值 |

## 回归测试

每次重大改动后，必须运行以下回归测试确保没有破坏现有功能：

### 核心功能回归

```bash
# 1. 导入测试 - 确保所有模块可导入
pytest tests/test_imports.py -v

# 2. 配置测试 - 确保配置正确加载
pytest tests/test_minimax_llm.py::TestMiniMaxConfig -v

# 3. 搜索引擎测试 - 确保搜索功能正常
pytest tests/test_search_engine.py -v

# 4. LLM 处理器测试 - 确保 LLM 调用正常
pytest tests/test_llm_processor.py -v
```

### 快速回归命令

```bash
# 运行所有测试
pytest tests/ -v --tb=short

# 仅运行单元测试（跳过需要网络的集成测试）
pytest tests/ -v -m "not integration"

# 生成简洁报告
pytest tests/ --tb=line -q
```

## 添加新测试

### 测试命名规范

- 测试文件: `test_<模块名>.py`
- 测试类: `Test<功能名>`
- 测试方法: `test_<具体行为>`

### 示例

```python
# tests/test_example.py
import pytest

class TestExample:
    """测试示例功能"""

    @pytest.fixture
    def example_instance(self):
        """共享的测试 fixture"""
        from src.example import Example
        return Example()

    def test_specific_behavior(self, example_instance):
        """测试具体行为"""
        result = example_instance.do_something()
        assert result == expected

    def test_edge_case(self, example_instance):
        """测试边界情况"""
        with pytest.raises(ValueError):
            example_instance.do_nothing()
```

### 测试隔离原则

1. **每个测试独立**: 测试之间不能有依赖
2. **使用 Fixture**: 共享 setup 用 `@pytest.fixture`
3. **Mock 外部依赖**: 网络请求、数据库等用 `unittest.mock`
4. **清理状态**: 测试后清理修改的状态

## Mock 使用指南

### Mock 网络请求

```python
from unittest.mock import patch, MagicMock

def test_api_call(self, mocker):
    mock_response = MagicMock()
    mock_response.json.return_value = {'result': 'success'}
    mock_response.status_code = 200

    mocker.patch('requests.post', return_value=mock_response)

    result = api.call()
    assert result['result'] == 'success'
```

### Mock API 密钥

```python
def test_with_env_key(mocker):
    mocker.patch.dict('os.environ', {'LLM_API_KEY': 'test-key'})
    # 测试代码
```

## 持续集成

每次提交 PR 前必须:

1. 运行所有测试: `pytest tests/ -v`
2. 检查测试覆盖率: `pytest tests/ --cov=src --cov-report=term-missing`
3. 确保没有警告

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| ImportError | 模块路径问题 | 添加 `sys.path.insert(0, ...)` |
| Mock 不生效 | patch 路径错误 | 确保 patch 正确的模块路径 |
| 测试超时 | 网络请求慢 | 增加 timeout 或 mock |
| 随机失败 | 测试有状态依赖 | 确保测试隔离 |

## 维护清单

- [ ] 新功能必须先写测试
- [ ] Bug 修复必须先写复现测试
- [ ] 每次 PR 必须通过所有测试
- [ ] 定期更新测试用例库文档
- [ ] 定期审查测试覆盖率
