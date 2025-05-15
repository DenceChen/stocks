#!/usr/bin/env python3
"""
批量股票分析示例脚本
"""
import os
import sys
import time
from datetime import datetime

# 将项目根目录添加到模块搜索路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.stock_agent import StockAgent
from src.utils import print_colored_title, Colors

def read_stock_list(file_path):
    """
    从文件中读取股票列表
    
    Args:
        file_path: 股票列表文件路径，每行格式为: 股票代码,股票名称
        
    Returns:
        包含(股票代码, 股票名称)元组的列表
    """
    stocks = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            parts = line.split(',')
            code = parts[0].strip()
            name = parts[1].strip() if len(parts) > 1 else None
            
            stocks.append((code, name))
    
    return stocks

def batch_stock_analysis(stocks_file, max_urls_per_stock=10, output_dir=None, risk_preference="low"):
    """
    批量分析多只股票的示例函数
    
    Args:
        stocks_file: 股票列表文件路径
        max_urls_per_stock: 每只股票的最大处理URL数量
        output_dir: 输出目录（可选）
        risk_preference: 投资风险偏好 ('low', 'medium', 'high')
    """
    # 读取股票列表
    stocks = read_stock_list(stocks_file)
    
    print_colored_title(f"开始批量分析 {len(stocks)} 只股票", Colors.BRIGHT_CYAN)
    
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
    
    # 开始计时
    start_time = time.time()
    
    # 执行批量分析
    results = agent.batch_analyze(
        stocks=stocks,
        max_urls_per_stock=max_urls_per_stock,
        risk_preference=risk_preference
    )
    
    # 计算处理时间
    elapsed_time = time.time() - start_time
    
    # 统计成功和失败的数量
    success_count = sum(1 for r in results if "error" not in r)
    failure_count = len(stocks) - success_count
    
    # 打印结果摘要
    print_colored_title("批量分析完成", Colors.BRIGHT_GREEN)
    print(f"总处理时间: {elapsed_time:.2f}秒，平均每只股票: {elapsed_time/len(stocks):.2f}秒")
    print(f"成功: {success_count}，失败: {failure_count}")
    print(f"详细结果已保存到输出目录: {agent.output_dir}")
    
    return results

if __name__ == "__main__":
    # 股票列表文件路径
    STOCKS_FILE = os.path.join(current_dir, "stocks.txt")
    
    # 可以选择风险偏好: low(低风险)、medium(中风险)、high(高风险)
    RISK_PREFERENCE = "low"
    
    # 执行批量分析
    results = batch_stock_analysis(
        stocks_file=STOCKS_FILE,
        max_urls_per_stock=5,  # 每只股票分析5个URL（为了示例更快完成）
        risk_preference=RISK_PREFERENCE
    ) 