"""
大模型处理模块 - 负责分析和总结爬取的内容，提供投资建议
"""
import logging
import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI

# 使用直接导入而非相对导入
from src.prompts import (
    INFO_EXTRACTION_SYSTEM_PROMPT,
    INFO_EXTRACTION_USER_PROMPT_TEMPLATE,
    INVESTMENT_ADVICE_SYSTEM_PROMPT,
    INVESTMENT_ADVICE_USER_PROMPT_TEMPLATE,
    BROKER_REPORT_SYSTEM_PROMPT,
    BROKER_REPORT_USER_PROMPT_TEMPLATE,
    POLICY_ANALYSIS_SYSTEM_PROMPT,
    POLICY_ANALYSIS_USER_PROMPT_TEMPLATE,
    MARKET_ANALYSIS_SYSTEM_PROMPT,
    MARKET_ANALYSIS_USER_PROMPT_TEMPLATE
)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMProcessor:
    def __init__(self, api_key: str = "sk-1c5050f8829e45d18b1b8d0f124c2219", base_url: str = "https://api.deepseek.com", model: str = "deepseek-chat"):
        """
        初始化LLM处理器
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 使用的模型名称
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        logger.info(f"LLM处理器初始化完成，使用模型: {model}")
        
    def extract_info_from_document(self, document: Dict) -> Dict:
        """
        从单个网页文档中提取关键信息
        
        Args:
            document: 包含网页内容的字典
            
        Returns:
            包含提取信息的字典
        """
        url = document.get("url", "未知URL")
        title = document.get("title", "未知标题")
        content = document.get("content", "")
        
        if not content:
            logger.warning(f"文档内容为空: {url}")
            return {
                "url": url,
                "title": title,
                "extracted_info": None,
                "error": "文档内容为空"
            }
            
        logger.info(f"从文档提取信息: {title} ({url})")
        
        # 限制内容长度，避免超出模型最大输入长度
        if len(content) > 14000:  # 给系统和用户提示词预留空间
            content = content[:14000] + "..."
            logger.info(f"文档内容已截断: {title}")
        
        # 根据URL和标题决定使用哪种提示词
        system_prompt = INFO_EXTRACTION_SYSTEM_PROMPT
        user_prompt = INFO_EXTRACTION_USER_PROMPT_TEMPLATE.format(
            title=title,
            url=url,
            content=content
        )
        
        # 如果是券商研报，使用特定的提示词
        if self._is_broker_report(url, title, content):
            logger.info(f"检测到券商研报: {title}")
            system_prompt = BROKER_REPORT_SYSTEM_PROMPT
            user_prompt = BROKER_REPORT_USER_PROMPT_TEMPLATE.format(
                title=title,
                url=url,
                content=content
            )
        
        # 如果是政策文件，使用特定的提示词
        elif self._is_policy_document(url, title, content):
            logger.info(f"检测到政策文件: {title}")
            system_prompt = POLICY_ANALYSIS_SYSTEM_PROMPT
            user_prompt = POLICY_ANALYSIS_USER_PROMPT_TEMPLATE.format(
                title=title,
                url=url,
                content=content
            )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=False
            )
            
            extracted_info = response.choices[0].message.content
            logger.info(f"信息提取成功: {title}")
            
            # 尝试解析为JSON格式，如果失败则保留原始文本
            try:
                extracted_info = json.loads(extracted_info)
            except:
                logger.warning(f"提取的信息无法解析为JSON: {title}")
                # 保持原始文本格式
                
            return {
                "url": url,
                "title": title,
                "extracted_info": extracted_info
            }
            
        except Exception as e:
            logger.error(f"从文档提取信息出错: {str(e)}")
            return {
                "url": url,
                "title": title,
                "extracted_info": None,
                "error": str(e)
            }
    
    def generate_investment_advice(self, extracted_docs: List[Dict], risk_preference: str = "low") -> str:
        """
        基于提取的信息生成投资建议
        
        Args:
            extracted_docs: 包含提取信息的文档列表
            risk_preference: 投资风险偏好 ('low', 'medium', 'high')
            
        Returns:
            投资建议文本
        """
        if not extracted_docs:
            logger.warning("没有文档可供分析")
            return "没有足够的信息生成投资建议。"
            
        logger.info(f"基于 {len(extracted_docs)} 个文档生成投资建议，风险偏好: {risk_preference}")
        
        # 构建汇总文本
        summary_text = ""
        for i, doc in enumerate(extracted_docs, 1):
            title = doc.get("title", "未知标题")
            url = doc.get("url", "未知URL")
            info = doc.get("extracted_info", "无有效信息")
            
            # 如果信息是字典，转为格式化文本
            if isinstance(info, dict):
                info_text = ""
                for key, value in info.items():
                    info_text += f"- {key}: "
                    if isinstance(value, list):
                        info_text += "\n  " + "\n  ".join([f"- {item}" for item in value])
                    else:
                        info_text += str(value)
                    info_text += "\n"
            else:
                info_text = str(info)
                
            summary_text += f"文档{i}：【{title}】({url})\n{info_text}\n\n"
            
        # 限制汇总文本长度
        if len(summary_text) > 14000:
            summary_text = summary_text[:14000] + "..."
            logger.info("汇总文本已截断")
            
        # 使用提示词模板
        system_prompt = INVESTMENT_ADVICE_SYSTEM_PROMPT
        
        # 根据风险偏好调整用户提示词
        risk_descriptions = {
            "low": "我偏好低风险投资，更看重资金安全和稳定收益，希望投资组合波动性较小。请推荐更多价值型、防御型板块和蓝筹股，以及风险较低的投资策略。",
            "medium": "我接受中等风险投资，希望在风险可控的前提下获得较好收益，能够承受一定的市场波动。请平衡推荐成长型和价值型投资标的，并提供均衡的投资策略。",
            "high": "我偏好高风险高收益的投资，能够承受较大的市场波动，追求超额收益。请推荐更多高成长性板块和潜力股，以及进取型的投资策略。"
        }
        
        risk_description = risk_descriptions.get(risk_preference, risk_descriptions["medium"])
        
        user_prompt = INVESTMENT_ADVICE_USER_PROMPT_TEMPLATE.format(
            summary_text=summary_text
        )
        
        # 在用户提示词中添加风险偏好说明
        user_prompt += f"\n\n{risk_description}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=False
            )
            
            investment_advice = response.choices[0].message.content
            logger.info("投资建议生成成功")
            return investment_advice
            
        except Exception as e:
            logger.error(f"生成投资建议出错: {str(e)}")
            return f"生成投资建议时出错: {str(e)}"
            
    def generate_market_analysis(self, extracted_docs: List[Dict], risk_preference: str = "low") -> str:
        """
        基于提取的信息生成市场整体分析
        
        Args:
            extracted_docs: The list of documents with extracted information
            risk_preference: 投资风险偏好 ('low', 'medium', 'high')
            
        Returns:
            The market analysis text
        """
        if not extracted_docs:
            logger.warning("没有文档可供分析")
            return "没有足够的信息生成市场分析。"
            
        logger.info(f"基于 {len(extracted_docs)} 个文档生成市场整体分析，风险偏好: {risk_preference}")
        
        # 构建汇总文本
        summary_text = ""
        for i, doc in enumerate(extracted_docs, 1):
            title = doc.get("title", "未知标题")
            url = doc.get("url", "未知URL")
            info = doc.get("extracted_info", "无有效信息")
            
            # 如果信息是字典，转为格式化文本
            if isinstance(info, dict):
                info_text = ""
                for key, value in info.items():
                    info_text += f"- {key}: "
                    if isinstance(value, list):
                        info_text += "\n  " + "\n  ".join([f"- {item}" for item in value])
                    else:
                        info_text += str(value)
                    info_text += "\n"
            else:
                info_text = str(info)
                
            summary_text += f"文档{i}：【{title}】({url})\n{info_text}\n\n"
            
        # 限制汇总文本长度
        if len(summary_text) > 14000:
            summary_text = summary_text[:14000] + "..."
            logger.info("汇总文本已截断")
            
        # 使用市场分析提示词模板
        system_prompt = MARKET_ANALYSIS_SYSTEM_PROMPT
        
        # 根据风险偏好调整用户提示词
        risk_descriptions = {
            "low": "我偏好低风险投资，更看重资金安全和稳定收益，希望投资组合波动性较小。请推荐更多价值型、防御型板块和蓝筹股，以及风险较低的投资策略。",
            "medium": "我接受中等风险投资，希望在风险可控的前提下获得较好收益，能够承受一定的市场波动。请平衡推荐成长型和价值型投资标的，并提供均衡的投资策略。",
            "high": "我偏好高风险高收益的投资，能够承受较大的市场波动，追求超额收益。请推荐更多高成长性板块和潜力股，以及进取型的投资策略。"
        }
        
        risk_description = risk_descriptions.get(risk_preference, risk_descriptions["medium"])
        
        user_prompt = MARKET_ANALYSIS_USER_PROMPT_TEMPLATE.format(
            summary_text=summary_text
        )
        
        # 在用户提示词中添加风险偏好说明
        user_prompt += f"\n\n{risk_description}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=False
            )
            
            market_analysis = response.choices[0].message.content
            logger.info("市场分析生成成功")
            return market_analysis
            
        except Exception as e:
            logger.error(f"生成市场分析出错: {str(e)}")
            return f"生成市场分析时出错: {str(e)}"
            
    def save_advice_to_file(self, advice: str, data_dir: str = "../data") -> str:
        """
        保存投资建议到文件
        
        Args:
            advice: 投资建议文本
            data_dir: 数据目录
            
        Returns:
            文件路径
        """
        from datetime import datetime
        
        os.makedirs(data_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(data_dir, f"investment_advice_{timestamp}.txt")
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(advice)
            logger.info(f"投资建议已保存至: {filename}")
            return filename
        except Exception as e:
            logger.error(f"保存投资建议出错: {str(e)}")
            return ""
            
    def _is_broker_report(self, url: str, title: str, content: str) -> bool:
        """
        判断是否为券商研报
        
        Args:
            url: 网页URL
            title: 网页标题
            content: 网页内容
            
        Returns:
            是否为券商研报
        """
        # 通过URL判断
        broker_domains = [
            "research.cmbi.com", "research.csc.com.cn", "research.china-invs.cn",
            "www.gtja.com/stock/research", "www.cicc.com/research", "research.china-invs.cn",
            "research.guosen.com.cn", "yanbao.stock.hexun.com", "research.ebscn.com",
            "www.swsresearch.com", "research.foundersc.com"
        ]
        
        if any(domain in url.lower() for domain in broker_domains):
            return True
            
        # 通过标题判断
        broker_keywords = [
            "研究报告", "研报", "券商", "证券", "投资评级", "目标价", "研究所",
            "首次覆盖", "投资分析", "行业研究", "公司研究"
        ]
        
        if any(keyword in title for keyword in broker_keywords):
            return True
            
        # 通过内容判断
        report_indicators = [
            "投资评级", "目标价格", "买入", "增持", "中性", "减持", "卖出",
            "研究报告", "行业研究", "公司研究", "盈利预测", "风险提示", 
            "分析师", "证券研究所", "证券分析师"
        ]
        
        if any(indicator in content[:2000] for indicator in report_indicators):
            return True
            
        return False
        
    def _is_policy_document(self, url: str, title: str, content: str) -> bool:
        """
        判断是否为政策文件
        
        Args:
            url: 网页URL
            title: 网页标题
            content: 网页内容
            
        Returns:
            是否为政策文件
        """
        # 通过URL判断
        policy_domains = [
            "www.pbc.gov.cn", "www.csrc.gov.cn", "www.mof.gov.cn", "www.gov.cn",
            "www.ndrc.gov.cn", "www.miit.gov.cn", "www.safe.gov.cn", "www.sse.com.cn",
            "www.szse.cn", "www.stats.gov.cn", "www.circ.gov.cn", "www.cbirc.gov.cn"
        ]
        
        if any(domain in url.lower() for domain in policy_domains):
            return True
            
        # 通过标题判断
        policy_keywords = [
            "政策", "通知", "规定", "条例", "办法", "规则", "指引", "指导意见",
            "央行", "证监会", "财政部", "国务院", "发改委", "部署", "措施",
            "实施", "公布", "发布", "印发", "经济政策", "货币政策", "监管政策"
        ]
        
        if any(keyword in title for keyword in policy_keywords):
            return True
            
        # 通过内容判断
        policy_indicators = [
            "各省、自治区、直辖市", "经研究决定", "现将", "有关事项通知如下",
            "特此通知", "现就", "现印发", "实施意见", "政策措施", "各有关部门"
        ]
        
        if any(indicator in content[:2000] for indicator in policy_indicators):
            return True
            
        return False
            
if __name__ == "__main__":
    # 测试代码
    processor = LLMProcessor()
    test_doc = {
        "url": "https://www.example.com",
        "title": "测试文档",
        "content": "这是一个测试内容，模拟央行最新政策表示将继续实施稳健的货币政策，保持流动性合理充裕。证监会表示将继续支持科技创新企业上市融资。最近科技股和新能源板块表现活跃，多只个股创新高。"
    }
    
    # 测试信息提取
    result = processor.extract_info_from_document(test_doc)
    print("提取的信息:")
    print(result.get("extracted_info"))
    
    # 测试生成投资建议
    advice = processor.generate_investment_advice([result])
    print("\n生成的投资建议:")
    print(advice)
    
    # 测试生成市场分析
    market_analysis = processor.generate_market_analysis([result])
    print("\n生成的市场分析:")
    print(market_analysis) 