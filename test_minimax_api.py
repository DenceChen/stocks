#!/usr/bin/env python3
"""
MiniMax API 测试脚本
用法:
    python test_minimax_api.py

需要设置环境变量:
    export LLM_API_KEY="your_api_key"
"""
import os
import sys
import json
import requests

# API 配置
API_KEY = os.getenv("LLM_API_KEY", "sk-cp-LgTiOgPQdjuhkRMDIahYhL3k-Tkmjh3DzqYrn7X7FjiIeHsPdIGEs3iiQtDh_QzpF3M6AYtk8l4qU8iwdN3fQbLjX3IAI5DsIl1Qw1nFOVPabO0kyuVX5Y4")
BASE_URL = "https://api.minimaxi.com"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def test_search_api():
    """测试 MiniMax 搜索 API"""
    print("\n" + "="*50)
    print("测试 1: MiniMax 搜索 API")
    print("="*50)

    try:
        response = requests.post(
            f"{BASE_URL}/v1/coding_plan/search",
            json={"q": "Python asyncio 2025"},
            headers=HEADERS,
            timeout=30
        )

        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")

        try:
            result = response.json()
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
        except:
            print(f"响应文本: {response.text[:500]}")

        if response.status_code == 200:
            result = response.json()
            # 搜索结果可能在 "organic" 字段中
            organic = result.get('organic', [])
            if organic:
                print(f"\n成功! 获取到 {len(organic)} 条结果")
                return True
        return False

    except Exception as e:
        print(f"请求失败: {e}")
        return False


def test_chat_api():
    """测试 MiniMax Chat Completion API"""
    print("\n" + "="*50)
    print("测试 2: MiniMax Chat Completion API")
    print("="*50)

    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json={
                "model": "MiniMax-M2.7-highspeed",
                "messages": [
                    {"role": "system", "content": "你是一个专业的股票投资分析师。"},
                    {"role": "user", "content": "你好，请用一句话介绍自己。"}
                ],
                "stream": False
            },
            headers=HEADERS,
            timeout=30
        )

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"响应: {content[:300]}...")

            usage = result.get("usage", {})
            print(f"\nToken 使用: prompt={usage.get('prompt_tokens', 0)}, completion={usage.get('completion_tokens', 0)}")
            return True
        else:
            print(f"响应: {response.text[:300]}")
            return False

    except Exception as e:
        print(f"请求失败: {e}")
        return False


def test_with_openai_client():
    """使用 OpenAI SDK 风格的客户端测试"""
    print("\n" + "="*50)
    print("测试 3: OpenAI SDK 兼容模式")
    print("="*50)

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL
        )

        response = client.chat.completions.create(
            model="MiniMax-M2.7-highspeed",
            messages=[
                {"role": "user", "content": "用一句话解释什么是股票。"}
            ]
        )

        print(f"模型: {response.model}")
        print(f"响应: {response.choices[0].message.content}")
        print(f"Token: {response.usage.total_tokens}")

        return True

    except Exception as e:
        print(f"OpenAI SDK 测试失败: {e}")
        return False


def test_stock_agent():
    """测试 StockAgent 使用 MiniMax"""
    print("\n" + "="*50)
    print("测试 4: StockAgent 集成")
    print("="*50)

    try:
        from src.stock_agent import StockAgent
        from src.config import get_config

        config = get_config()
        print(f"LLM Base URL: {config['LLM']['BASE_URL']}")
        print(f"LLM Model: {config['LLM']['MODEL']}")

        agent = StockAgent()
        print("StockAgent 初始化成功!")

        return True

    except Exception as e:
        print(f"StockAgent 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_minimax_search_integration():
    """测试 SearchEngine 的 MiniMax 搜索集成"""
    print("\n" + "="*50)
    print("测试 5: SearchEngine MiniMax 搜索")
    print("="*50)

    try:
        from src.search_engine import SearchEngine

        engine = SearchEngine()
        print(f"SearchEngine 初始化成功!")

        # 测试 minimax_search 方法存在
        if hasattr(engine, 'minimax_search'):
            print("minimax_search 方法存在")

            # 执行搜索
            result = engine.minimax_search("A股今日行情")
            print(f"搜索结果: {json.dumps(result, indent=2, ensure_ascii=False)[:300]}...")

            return True
        else:
            print("minimax_search 方法不存在!")
            return False

    except Exception as e:
        print(f"SearchEngine 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*50)
    print("MiniMax API 完整测试")
    print("="*50)
    print(f"API Key: {API_KEY[:20]}...")
    print(f"Base URL: {BASE_URL}")

    os.environ['LLM_API_KEY'] = API_KEY

    results = []

    # 测试 1: 搜索 API
    results.append(("搜索 API", test_search_api()))

    # 测试 2: Chat API
    results.append(("Chat API", test_chat_api()))

    # 测试 3: OpenAI SDK
    results.append(("OpenAI SDK", test_with_openai_client()))

    # 测试 4: StockAgent
    results.append(("StockAgent", test_stock_agent()))

    # 测试 5: SearchEngine
    results.append(("SearchEngine", test_minimax_search_integration()))

    # 汇总
    print("\n" + "="*50)
    print("测试结果汇总")
    print("="*50)

    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print("="*50)

    if all_passed:
        print("🎉 所有测试通过!")
        sys.exit(0)
    else:
        print("⚠️ 部分测试失败")
        sys.exit(1)
