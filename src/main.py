#!/usr/bin/env python3
"""
股票投资Agent主程序入口
"""
import os
import sys
import argparse
import time
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

# 将项目根目录添加到模块搜索路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.stock_agent import StockAgent
from src.utils import Logger, print_colored_title, Colors
from src.config import get_config, DEFAULT_SEARCH_QUERIES

# 创建日志记录器
logger = Logger.get_logger('main')

async def run_agent(
    search_method: str = "google", 
    max_urls: int = 15, 
    max_concurrency: int = 3, 
    queries: Optional[List[str]] = None, 
    risk_preference: str = "low",
    verbose: bool = False
) -> str:
    """
    运行股票投资Agent的异步函数，供run.py调用
    
    Args:
        search_method: 搜索方法，"google"或"baidu"
        max_urls: 最大处理URL数量
        max_concurrency: 爬虫最大并发数
        queries: 自定义搜索关键词列表，如果为None则使用默认值
        risk_preference: 投资风险偏好 ("low", "medium", "high")
        verbose: 是否启用详细日志
        
    Returns:
        str: 投资建议文本
    """
    # 设置日志级别
    if verbose:
        logger.setLevel("DEBUG")
    
    # 获取配置
    config = get_config()
    
    # 根据用户风险偏好更新配置
    config["INVESTMENT"]["RISK_TOLERANCE"] = {
        "low": "低",
        "medium": "中等",
        "high": "高"
    }.get(risk_preference, "中等")
    
    # 使用默认搜索关键词如果未提供
    if queries is None:
        queries = DEFAULT_SEARCH_QUERIES
    
    # 创建Agent实例
    agent = StockAgent(config=config)
    
    # 执行市场分析
    try:
        # 调用市场分析功能
        # 这里简化处理，实际上可能需要通过StockAgent提供更具体的市场分析方法
        results = await agent.analyze_market(
            search_queries=queries,
            search_method=search_method,
            max_urls=max_urls,
            max_concurrency=max_concurrency,
            risk_preference=risk_preference
        )
        
        # 提取投资建议
        if isinstance(results, dict) and "recommendation" in results:
            return results["recommendation"]
        elif isinstance(results, str):
            return results
        else:
            return "分析完成，但未能生成投资建议。"
            
    except Exception as e:
        error_msg = f"运行过程中发生错误: {str(e)}"
        logger.error(error_msg)
        return error_msg

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='股票投资Agent - 自动分析股票投资机会')
    
    # 定义参数组
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('-s', '--stock', help='单个股票分析模式，提供股票代码')
    mode_group.add_argument('-b', '--batch', help='批量分析模式，提供包含股票列表的文件路径')
    mode_group.add_argument('-m', '--market', action='store_true', help='市场整体分析模式')
    
    # 其他可选参数
    parser.add_argument('-n', '--name', help='股票名称（单个股票模式使用）')
    parser.add_argument('-u', '--urls', type=int, default=15, help='每个股票分析的最大URL数量')
    parser.add_argument('-o', '--output', help='指定输出目录')
    parser.add_argument('-v', '--verbose', action='store_true', help='启用详细日志输出')
    parser.add_argument('-r', '--risk', choices=['low', 'medium', 'high'], default='low', 
                       help='投资风险偏好: low(低风险)、medium(中风险)、high(高风险)')
    
    return parser.parse_args()

def read_stock_list(file_path: str) -> List[Tuple[str, Optional[str]]]:
    """
    从文件中读取股票列表
    
    Args:
        file_path: 股票列表文件路径，每行格式为: 股票代码,股票名称
        
    Returns:
        包含(股票代码, 股票名称)元组的列表
    """
    stocks = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                parts = line.split(',')
                code = parts[0].strip()
                name = parts[1].strip() if len(parts) > 1 else None
                
                stocks.append((code, name))
        
        logger.info(f"从文件 {file_path} 中加载了 {len(stocks)} 只股票")
        return stocks
        
    except Exception as e:
        logger.error(f"读取股票列表文件失败: {str(e)}")
        sys.exit(1)

def single_stock_analysis(agent: StockAgent, stock_code: str, stock_name: Optional[str], max_urls: int, risk_preference: str = "low"):
    """
    分析单个股票
    
    Args:
        agent: StockAgent实例
        stock_code: 股票代码
        stock_name: 股票名称
        max_urls: 最大分析URL数量
        risk_preference: 投资风险偏好
    """
    stock_identifier = f"{stock_name}({stock_code})" if stock_name else stock_code
    print_colored_title(f"开始分析股票: {stock_identifier}", Colors.BRIGHT_CYAN)
    
    risk_names = {'low': '低风险', 'medium': '中风险', 'high': '高风险'}
    print(f"风险偏好: {risk_names.get(risk_preference, '低风险')}")
    
    try:
        # 执行分析
        results = agent.analyze_stock(
            stock_code=stock_code,
            stock_name=stock_name,
            max_urls=max_urls,
            save_results=True,
            risk_preference=risk_preference
        )
        
        if "error" in results:
            print_colored_title(f"分析失败: {results['error']}", Colors.BRIGHT_RED)
            return
        
        # 打印分析结果摘要
        print_colored_title("分析完成", Colors.BRIGHT_GREEN)
        print(f"处理时间: {results.get('processing_time', 0):.2f}秒")
        print(f"分析了 {len(results.get('sources', []))} 个信息源")
        
        # 打印投资建议摘要
        recommendation = results.get('recommendation', '')
        if recommendation:
            print_colored_title("投资建议摘要", Colors.BRIGHT_YELLOW)
            # 打印前500个字符作为摘要
            print(f"{recommendation[:500]}...\n")
            print(f"完整结果已保存到输出目录")
        
    except Exception as e:
        logger.error(f"分析过程中发生错误: {str(e)}")
        print_colored_title(f"分析过程中发生错误: {str(e)}", Colors.BRIGHT_RED)

def batch_stock_analysis(agent: StockAgent, stocks: List[Tuple[str, Optional[str]]], max_urls_per_stock: int, risk_preference: str = "low"):
    """
    批量分析多只股票
    
    Args:
        agent: StockAgent实例
        stocks: 股票列表，每项为(代码, 名称)元组
        max_urls_per_stock: 每只股票的最大分析URL数量
        risk_preference: 投资风险偏好
    """
    total_stocks = len(stocks)
    print_colored_title(f"开始批量分析 {total_stocks} 只股票", Colors.BRIGHT_CYAN)
    
    risk_names = {'low': '低风险', 'medium': '中风险', 'high': '高风险'}
    print(f"风险偏好: {risk_names.get(risk_preference, '低风险')}")
    
    start_time = time.time()
    results = agent.batch_analyze(stocks, max_urls_per_stock=max_urls_per_stock, risk_preference=risk_preference)
    total_time = time.time() - start_time
    
    # 统计成功和失败的数量
    success_count = sum(1 for r in results if "error" not in r)
    failure_count = total_stocks - success_count
    
    # 打印批量分析结果摘要
    print_colored_title("批量分析完成", Colors.BRIGHT_GREEN)
    print(f"总处理时间: {total_time:.2f}秒，平均每只股票: {total_time/total_stocks:.2f}秒")
    print(f"成功: {success_count}，失败: {failure_count}")
    print(f"详细结果已保存到输出目录")

def market_analysis(agent: StockAgent, risk_preference: str = "low"):
    """
    市场整体分析
    
    Args:
        agent: StockAgent实例
        risk_preference: 投资风险偏好
    """
    print_colored_title("开始市场整体分析", Colors.BRIGHT_CYAN)
    risk_names = {'low': '低风险', 'medium': '中风险', 'high': '高风险'}
    print(f"风险偏好: {risk_names.get(risk_preference, '低风险')}")
    
    # 获取搜索关键词
    search_queries = DEFAULT_SEARCH_QUERIES
    
    # 执行市场分析
    try:
        # 设置较大的URL数量以获取更全面的信息
        max_urls = 20
        
        # 调用异步方法进行市场分析
        import asyncio
        results = asyncio.run(agent.analyze_market(
            search_queries=search_queries,
            max_urls=max_urls,
            risk_preference=risk_preference
        ))
        
        if isinstance(results, dict) and "recommendation" in results:
            recommendation = results["recommendation"]
            output_file = results.get("output_file", "未知文件路径")
            
            # 打印分析结果摘要
            print_colored_title("市场分析完成", Colors.BRIGHT_GREEN)
            print(f"分析了 {len(results.get('sources', []))} 个信息源")
            print(f"完整结果已保存至: {output_file}")
            
            # 打印摘要（前500个字符）
            if recommendation:
                print_colored_title("投资建议摘要", Colors.BRIGHT_YELLOW)
                print(f"{recommendation[:500]}...\n")
        else:
            print_colored_title("市场分析结果", Colors.BRIGHT_YELLOW)
            print(results)
            
    except Exception as e:
        logger.error(f"市场分析过程中发生错误: {str(e)}")
        print_colored_title(f"市场分析过程中发生错误: {str(e)}", Colors.BRIGHT_RED)

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置日志级别
    if args.verbose:
        # 设置更详细的日志级别
        logger.setLevel("DEBUG")
    
    # 如果指定了输出目录，更新配置
    config = get_config()
    if args.output:
        config["AGENT_CONFIG"]["OUTPUT_DIR"] = args.output
        os.makedirs(args.output, exist_ok=True)
    
    # 创建Agent实例
    agent = StockAgent(config=config)
    
    # 根据模式执行不同的分析
    try:
        if args.stock:
            # 单个股票分析模式
            single_stock_analysis(agent, args.stock, args.name, args.urls, args.risk)
            
        elif args.batch:
            # 批量分析模式
            stocks = read_stock_list(args.batch)
            batch_stock_analysis(agent, stocks, args.urls, args.risk)
            
        elif args.market:
            # 市场整体分析模式
            market_analysis(agent, args.risk)
    
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        print_colored_title("操作已中断", Colors.BRIGHT_YELLOW)
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"程序执行过程中发生错误: {str(e)}")
        print_colored_title(f"程序执行出错: {str(e)}", Colors.BRIGHT_RED)
        sys.exit(1)

if __name__ == "__main__":
    print_colored_title("股票投资Agent", Colors.BRIGHT_CYAN)
    main()
    sys.exit(0) 