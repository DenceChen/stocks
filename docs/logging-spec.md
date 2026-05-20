# 日志系统规范

## 概述

本项目使用统一的日志系统进行日志管理，支持分级日志、日志文件轮转、彩色控制台输出。

## 日志配置

**模块位置**: `src/logging_config.py`

**日志格式**:
```
%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s
时间        | 级别        | 模块             | 消息
```

## 日志级别

| 级别 | 数值 | 用途 |
|------|------|------|
| DEBUG | 10 | 详细调试信息 |
| INFO | 20 | 一般信息 |
| WARNING | 30 | 警告信息 |
| ERROR | 40 | 错误信息 |
| CRITICAL | 50 | 严重错误 |

**环境变量**: `LOG_LEVEL` (默认: `INFO`)

## 日志文件

日志文件位于 `logs/` 目录:

| 文件 | 内容 | 级别过滤 |
|------|------|----------|
| `logs/app.log` | 应用日志 | 全部 |
| `logs/error.log` | 错误日志 | ERROR 及以上 |
| `logs/api.log` | API 调用日志 | 全部 |

**轮转设置**:
- 单文件最大 10MB
- 保留 5 个备份

## 使用方法

### 1. 获取日志记录器

```python
from src.logging_config import get_logger

logger = get_logger(__name__)
```

### 2. 预配置日志记录器

```python
from src.logging_config import get_app_logger, get_api_logger, get_error_logger

app_logger = get_app_logger()      # 应用日志
api_logger = get_api_logger()       # API 日志
error_logger = get_error_logger()    # 错误日志
```

### 3. 便捷函数

**API 调用日志**:
```python
from src.logging_config import log_api_call

log_api_call(
    logger,
    method="POST",
    url="https://api.example.com",
    status_code=200,
    duration=1.234
)
```

**函数调用日志**:
```python
from src.logging_config import log_function_call

log_function_call(
    logger,
    func_name="process_data",
    args=("arg1", "arg2"),
    kwargs={"key": "value"},
    result={"status": "success"},
    duration=0.5
)
```

### 4. 快捷日志函数

```python
from src.logging_config import debug, info, warning, error, critical

info("这是一条信息")
error("发生错误: %s", error_msg)
```

## 日志查询

### 查看错误日志
```bash
grep "ERROR" logs/error.log
grep "CRITICAL" logs/error.log
```

### 实时查看应用日志
```bash
tail -f logs/app.log
```

### 按模块过滤
```bash
grep "stocks.api" logs/app.log
grep "stocks.error" logs/error.log
```

### 按时间范围查询
```bash
# 今天以来的日志
grep "2026-05-20" logs/app.log

# 最近 100 条
tail -100 logs/app.log
```

### 日志分析
```bash
# 统计错误数量
grep -c "ERROR" logs/error.log

# 提取错误信息
grep "ERROR" logs/error.log | awk -F'|' '{print $4}'

# 分析 API 响应时间
grep "duration" logs/api.log | awk -F'duration=' '{print $2}' | sort -n
```

## 模块命名约定

| 模块 | 日志记录器名称 |
|------|---------------|
| 主程序 | `stocks` |
| API 模块 | `stocks.api` |
| 错误处理 | `stocks.error` |
| 搜索引擎 | `stocks.search` |
| LLM 处理器 | `stocks.llm` |
| 爬虫 | `stocks.crawler` |

## 最佳实践

1. **使用 `__name__` 作为日志记录器名称**，便于追踪日志来源
2. **敏感信息脱敏**：日志中不要记录 API Key、密码等敏感信息
3. **合理选择日志级别**：
   - DEBUG: 仅开发调试使用
   - INFO: 重要业务流程节点
   - WARNING: 潜在问题但不影响功能
   - ERROR: 影响部分功能
   - CRITICAL: 系统无法继续运行
4. **结构化日志**：使用 `log_function_call` 等便捷函数记录结构化信息
5. **错误日志包含上下文**：记录足够的上下文信息便于排查问题

## 故障排查

### 日志无输出
1. 检查 `LOG_LEVEL` 环境变量
2. 确认 `logs/` 目录存在且有写入权限

### 日志文件过大
- 检查是否有大量 DEBUG 日志
- 调整 `LOG_LEVEL` 为 INFO 或 WARNING

### 排查流程
1. 先看 `logs/error.log` 找错误
2. 用 `grep` 按模块过滤
3. 结合时间戳定位问题区间
