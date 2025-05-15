# 贡献指南

感谢你对股票投资Agent项目的兴趣！我们欢迎各种形式的贡献，包括但不限于代码贡献、文档改进、bug报告和功能建议。

## 如何贡献

### 报告Bug

如果你发现了bug，请通过GitHub Issues提交报告，并包含以下信息：

1. Bug的简要描述
2. 复现步骤
3. 期望的行为
4. 实际的行为
5. 环境信息（操作系统、Python版本等）
6. 相关截图或日志（如有）

### 提交功能建议

如果你有新功能建议，请通过GitHub Issues提交，描述你想要的功能以及它如何对项目有所帮助。

### 提交Pull Request

1. Fork项目仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个Pull Request

## 开发规范

### 代码风格

我们使用[PEP 8](https://www.python.org/dev/peps/pep-0008/)作为Python代码风格指南。请确保你的代码遵循此规范。

推荐使用工具如`flake8`、`black`和`isort`来自动检查和格式化代码：

```bash
pip install flake8 black isort
flake8 stocks/
black stocks/
isort stocks/
```

### 类型注解

所有新代码应当包含类型注解，以增强代码可读性和IDE支持。

```python
def example_function(param1: str, param2: int) -> bool:
    # 函数实现
    return True
```

### 文档规范

所有模块、类和函数都应该有文档字符串，遵循[Google风格的Python文档](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)：

```python
def function_with_types_in_docstring(param1, param2):
    """示例函数描述

    Args:
        param1 (int): 第一个参数的描述
        param2 (str): 第二个参数的描述

    Returns:
        bool: 返回值的描述

    Raises:
        ValueError: 错误条件的描述
    """
    return True
```

### 测试规范

所有新功能都应该有相应的单元测试。我们使用`pytest`作为测试框架。

```python
# 在tests目录下创建测试文件
def test_my_function():
    # 实现测试
    assert my_function() == expected_result
```

运行测试：

```bash
pytest stocks/tests/
```

## 分支策略

- `main`: 稳定版本分支，用于发布
- `develop`: 开发分支，所有特性分支都应该从此分支创建
- `feature/*`: 新功能分支
- `bugfix/*`: Bug修复分支
- `hotfix/*`: 紧急修复分支

## 版本管理

我们使用[语义化版本](https://semver.org/)进行版本管理：

- MAJOR版本：当你做了不兼容的API修改
- MINOR版本：当你添加了向下兼容的功能
- PATCH版本：当你做了向下兼容的bug修复

## 发布流程

1. 更新版本号（在`__init__.py`中）
2. 更新CHANGELOG.md
3. 创建一个新的发布分支
4. 发布到PyPI（如适用）
5. 在GitHub上创建一个新的发布版本

## 行为准则

请保持礼貌和尊重。我们欢迎来自不同背景和经验水平的贡献者，共同营造一个积极和包容的社区。 