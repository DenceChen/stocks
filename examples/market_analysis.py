#!/usr/bin/env python3
"""
市场整体分析示例脚本
"""
import os
import sys
import time
import asyncio
from datetime import datetime

# 将项目根目录添加到模块搜索路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.stock_agent import StockAgent
from src.utils import print_colored_title, Colors
from src.config import DEFAULT_SEARCH_QUERIES

async def market_analysis(output_dir=None, max_urls=20, risk_preference="low"):
    """
    市场整体分析示例函数
    
    Args:
        output_dir: 输出目录（可选）
        max_urls: 最大处理URL数量
        risk_preference: 投资风险偏好 ('low', 'medium', 'high')
    
    Returns:
        分析结果
    """
    print_colored_title("开始市场整体分析", Colors.BRIGHT_CYAN)
    
    # 显示风险偏好
    risk_names = {'low': '低风险', 'medium': '中风险', 'high': '高风险'}
    print(f"风险偏好: {risk_names.get(risk_preference, '低风险')}")
    
    # 初始化Agent
    config = None
    if output_dir:
        # 自定义输出目录
        from src.config import get_config
        config = get_config()
        config["AGENT_CONFIG"]["OUTPUT_DIR"] = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    agent = StockAgent(config=config)
    
    # 获取搜索关键词
    search_queries = DEFAULT_SEARCH_QUERIES
    
    # 开始计时
    start_time = time.time()
    
    # 执行市场分析
    results = await agent.analyze_market(
        search_queries=search_queries[:10],  # 为了示例更快完成，只使用前10个关键词
        max_urls=max_urls,
        risk_preference=risk_preference
    )
    
    # 计算处理时间
    elapsed_time = time.time() - start_time
    
    # 打印结果摘要
    print_colored_title("市场分析完成", Colors.BRIGHT_GREEN)
    print(f"总处理时间: {elapsed_time:.2f}秒")
    
    if isinstance(results, dict) and "recommendation" in results:
        recommendation = results["recommendation"]
        output_file = results.get("output_file", "未知文件路径")
        
        print(f"分析了 {len(results.get('sources', []))} 个信息源")
        print(f"完整结果已保存至: {output_file}")
        
        # 打印摘要（前500个字符）
        if recommendation:
            print_colored_title("投资建议摘要", Colors.BRIGHT_YELLOW)
            print(f"{recommendation[:500]}...\n")
    else:
        print_colored_title("市场分析结果", Colors.BRIGHT_YELLOW)
        print(results)
    
    return results

if __name__ == "__main__":
    # 可以选择风险偏好: low(低风险)、medium(中风险)、high(高风险)
    RISK_PREFERENCE = "medium"
    
    # 执行市场分析
    try:
        results = asyncio.run(market_analysis(
            max_urls=10,  # 为了示例更快完成，只处理10个URL
            risk_preference=RISK_PREFERENCE
        ))
    except KeyboardInterrupt:
        print("\n程序已被用户中断")
        sys.exit(1) 