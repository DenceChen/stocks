# 测试目录

本目录包含项目的测试用例。

## 快速测试

验证导入是否正常工作：

```bash
python tests/test_imports.py
```

这将运行一个简单的测试，确保所有必要的模块都能正确导入。

## 测试前的准备

在运行测试前，请确保已安装所有依赖：

```bash
pip install -r requirements.txt
```

## 添加新测试

如需添加新的测试用例，请按照以下命名约定：

- 所有测试文件应以`test_`开头
- 测试方法应以`test_`开头
- 使用`unittest`模块进行测试

示例：

```python
import unittest

class TestMyFeature(unittest.TestCase):
    def test_some_functionality(self):
        # 测试代码
        self.assertTrue(True)
``` 