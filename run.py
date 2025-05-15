#!/usr/bin/env python
"""
股票投资Agent启动脚本
"""
import os
import sys
import asyncio

# 添加项目根目录到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入main模块中的run_agent函数
from src.main import run_agent

async def main():
    """
    主函数 - 提供简单的命令行界面
    """
    print("\n" + "="*50)
    print("【股票投资智能Agent】".center(48))
    print("="*50)
    print("\n该Agent可以自动搜索、爬取和分析股票相关信息，并生成投资建议。\n")
    
    # 获取搜索方法
    print("请选择搜索引擎：")
    print("1. Google")
    print("2. 百度")
    
    choice = input("\n请输入选项编号 [默认1]: ").strip()
    search_method = "google" if not choice or choice == "1" else "baidu"
    
    # 获取自定义搜索关键词
    print("\n请输入搜索关键词，多个关键词用逗号分隔")
    print("如不输入，将使用默认关键词（央行政策、证监会公告、行业分析等）")
    
    keywords_input = input("\n搜索关键词: ").strip()
    queries = None
    if keywords_input:
        queries = [k.strip() for k in keywords_input.split(",") if k.strip()]
    
    # 获取处理的URL数量
    max_urls_input = input("\n处理的URL数量 [默认15]: ").strip()
    max_urls = 15
    if max_urls_input and max_urls_input.isdigit():
        max_urls = int(max_urls_input)
    
    # 获取最大并发数
    concurrency_input = input("\n爬虫最大并发数 [默认3]: ").strip()
    max_concurrency = 3
    if concurrency_input and concurrency_input.isdigit():
        max_concurrency = int(concurrency_input)
    
    # 获取投资风险偏好
    print("\n请选择您的投资风险偏好：")
    print("1. 低风险 - 更注重安全性和稳定收益")
    print("2. 中风险 - 平衡收益与风险")
    print("3. 高风险 - 追求高收益，能承受较大波动")
    
    risk_choice = input("\n请输入选项编号 [默认1]: ").strip()
    if not risk_choice or risk_choice == "1":
        risk_preference = "low"
    elif risk_choice == "2":
        risk_preference = "medium"
    elif risk_choice == "3":
        risk_preference = "high"
    else:
        print("无效的选择，使用默认的低风险偏好")
        risk_preference = "low"
    
    print("\n" + "="*50)
    print("开始运行股票投资Agent...")
    print("- 搜索引擎: " + ("Google" if search_method == "google" else "百度"))
    print("- 处理URL数量: " + str(max_urls))
    print("- 爬虫并发数: " + str(max_concurrency))
    print("- 投资风险偏好: " + {"low": "低风险", "medium": "中风险", "high": "高风险"}[risk_preference])
    print("="*50 + "\n")
    
    # 运行Agent
    advice = await run_agent(
        search_method=search_method,
        max_urls=max_urls,
        max_concurrency=max_concurrency,
        queries=queries,
        risk_preference=risk_preference,
        verbose=False
    )
    
    # 打印投资建议
    print("\n" + "="*50)
    print("【股票投资建议】")
    print("="*50)
    print(advice)
    print("="*50)
    
    input("\n按Enter键退出...")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n程序已被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        sys.exit(1) 