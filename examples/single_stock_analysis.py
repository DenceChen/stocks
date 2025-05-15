#!/usr/bin/env python3
"""
单只股票分析示例脚本
"""
import os
import sys
import time
from datetime import datetime

# 将项目根目录添加到模块搜索路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from stocks.src.stock_agent import StockAgent
from stocks.src.utils import print_colored_title, Colors

def analyze_single_stock(stock_code, stock_name=None, max_urls=10, output_dir=None):
    """
    分析单只股票的示例函数
    
    Args:
        stock_code: 股票代码
        stock_name: 股票名称（可选）
        max_urls: 最大处理URL数量
        output_dir: 输出目录（可选）
    """
    print_colored_title(f"开始分析股票: {stock_name or ''}({stock_code})", Colors.BRIGHT_CYAN)
    
    # 初始化Agent
    config = None
    if output_dir:
        # 自定义输出目录
        from stocks.src.config import get_config
        config = get_config()
        config["AGENT_CONFIG"]["OUTPUT_DIR"] = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    agent = StockAgent(config=config)
    
    # 开始计时
    start_time = time.time()
    
    # 执行分析
    results = agent.analyze_stock(
        stock_code=stock_code,
        stock_name=stock_name,
        max_urls=max_urls,
        save_results=True
    )
    
    # 计算处理时间
    elapsed_time = time.time() - start_time
    
    # 打印结果摘要
    if "error" in results:
        print_colored_title(f"分析失败: {results['error']}", Colors.BRIGHT_RED)
        return
    
    print_colored_title("分析完成", Colors.BRIGHT_GREEN)
    print(f"处理时间: {elapsed_time:.2f}秒")
    print(f"分析了 {len(results.get('sources', []))} 个信息源")
    
    # 打印投资建议摘要
    recommendation = results.get('recommendation', '')
    if recommendation:
        print_colored_title("投资建议摘要", Colors.BRIGHT_YELLOW)
        # 打印前500个字符作为摘要
        print(f"{recommendation[:500]}...\n")
        
        # 保存文件路径
        output_dir = results.get('output_dir', agent.output_dir)
        print(f"完整结果已保存到: {output_dir}")
    
    return results

if __name__ == "__main__":
    # 可以在这里修改股票代码和名称
    STOCK_CODE = "AAPL"
    STOCK_NAME = "Apple Inc."
    
    # 执行分析
    result = analyze_single_stock(STOCK_CODE, STOCK_NAME, max_urls=15) 