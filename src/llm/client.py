"""
LLM 客户端模块：封装大语言模型调用
"""

import os
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


class LLMClient(ABC):
    """LLM 客户端抽象基类"""
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            **kwargs: 其他参数
            
        Returns:
            模型回复文本
        """
        pass


class OpenAIClient(LLMClient):
    """OpenAI API 客户端"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        初始化 OpenAI 客户端
        
        Args:
            api_key: OpenAI API Key，如果不提供则从环境变量 OPENAI_API_KEY 读取
            model: 模型名称
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("请提供 API Key 或设置环境变量 OPENAI_API_KEY")
        
        try:
            import openai
            openai.api_key = self.api_key
        except ImportError:
            raise ImportError("请先安装 openai 包：pip install openai")
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        调用 OpenAI Chat API
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数（temperature, max_tokens 等）
            
        Returns:
            模型回复
        """
        import openai
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API 调用失败: {e}")


class MockLLMClient(LLMClient):
    """模拟 LLM 客户端（用于测试）"""
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """返回模拟回复"""
        last_message = messages[-1]["content"] if messages else ""
        
        # 简单的规则回复
        if "复述" in last_message or "解读" in last_message:
            return "我理解你关注的是这个研究方向。你更接近哪个方向？\n1. 理论研究\n2. 应用实践\n3. 系统实现"
        elif "追问" in last_message or "分叉" in last_message:
            return "你更关心理论分析还是实验验证？\nA. 理论分析\nB. 实验验证\nC. 都关心"
        else:
            return "这是一个很好的研究方向。"
