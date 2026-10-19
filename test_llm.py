"""
LLM 集成测试脚本
"""

import sys
sys.path.insert(0, 'src')

from llm.client import OpenAIClient
from llm.prompt_manager import PromptManager

def test_llm_connection():
    """测试 LLM 连接"""
    print("="*50)
    print("测试 LLM 连接")
    print("="*50)
    
    try:
        # 初始化客户端
        client = OpenAIClient()
        print(f"[OK] OpenAI 客户端初始化成功")
        print(f"  - Model: {client.model}")
        print(f"  - Base URL: {client.base_url or '默认'}")
        
        # 测试简单对话
        messages = [
            {"role": "system", "content": "你是一个助手"},
            {"role": "user", "content": "你好，请简单介绍一下自己"}
        ]
        
        print("\n发送测试消息...")
        response = client.chat(messages, temperature=0.7)
        
        # 处理编码问题
        try:
            response_safe = response.encode('gbk', errors='ignore').decode('gbk')
        except:
            response_safe = response
        
        print(f"\n[OK] LLM 回复成功:")
        print(f"  {response_safe[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] LLM 连接失败: {e}")
        return False


def test_restate():
    """测试复述功能"""
    print("\n" + "="*50)
    print("测试复述功能")
    print("="*50)
    
    try:
        from agent.clarifier import Clarifier
        
        clarifier = Clarifier()
        
        user_input = "我想做大模型辅助文献检索"
        print(f"\n用户输入: {user_input}")
        
        result = clarifier.restate(user_input)
        
        print(f"\n[OK] 复述成功:")
        print(f"  复述: {result['restatement']}")
        print(f"  选项:")
        for i, option in enumerate(result['options'], 1):
            print(f"    {i}. {option}")
        print(f"  关键词: {result['keywords']}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] 复述测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n开始 LLM 集成测试...\n")
    
    # 测试连接
    if test_llm_connection():
        # 测试复述
        test_restate()
    
    print("\n" + "="*50)
    print("测试完成")
    print("="*50)
