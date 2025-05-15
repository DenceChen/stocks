#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages

# 从__init__.py中读取版本号
with open(os.path.join("stocks", "src", "__init__.py"), "r", encoding="utf-8") as f:
    version_match = re.search(r'__version__ = ["\']([^"\']*)["\']', f.read())
    version = version_match.group(1) if version_match else "0.0.1"

# 读取README.md作为长描述
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# 从requirements.txt中读取依赖
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="stock-investment-agent",
    version=version,
    description="一个自动化的股票投资分析工具，能够自动搜索、爬取和分析股票相关信息，并生成专业的投资建议。",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Stock Investment Agent Contributors",
    author_email="your-email@example.com",  # 请更改为你的邮箱
    url="https://github.com/yourusername/stock-investment-agent",  # 请更改为你的仓库URL
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Chinese (Simplified)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    keywords="stock, investment, finance, analysis, AI, crawler",
    entry_points={
        "console_scripts": [
            "stock-agent=stocks.src.main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/stock-investment-agent/issues",
        "Source": "https://github.com/yourusername/stock-investment-agent",
        "Documentation": "https://github.com/yourusername/stock-investment-agent/blob/main/README.md",
    },
) 