"""
澄清模块：复述、分叉、收敛逻辑
"""

from typing import List, Dict, Any, Optional
import re
from llm.client import LLMClient, MockLLMClient
from llm.prompt_manager import PromptManager


class Clarifier:
    """对话澄清器：实现复述、分叉、收敛逻辑"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        初始化澄清器
        
        Args:
            llm_client: LLM 客户端，如果不提供则使用 MockLLMClient
        """
        self.llm_client = llm_client or MockLLMClient()
        self.prompt_manager = PromptManager()
        self.interpretations = []
    
    def restate(self, user_input: str) -> Dict[str, Any]:
        """
        复述用户输入，给出 2-3 种可能的解读
        
        Args:
            user_input: 用户原始输入
            
        Returns:
            包含复述和选项的字典
        """
        # 使用 LLM 生成复述
        prompt = self.prompt_manager.build_restate_prompt(user_input)
        
        messages = [
            {"role": "system", "content": "你是一个文献检索辅助助手，帮助用户澄清研究兴趣。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.llm_client.chat(messages, temperature=0.7)
            
            # 解析回复，提取复述和选项
            restatement, options = self._parse_restate_response(response)
            
            return {
                "restatement": restatement,
                "options": options,
                "keywords": self._extract_keywords(user_input)
            }
        except Exception as e:
            # 降级到规则逻辑
            print(f"LLM 调用失败，使用规则逻辑: {e}")
            return self._rule_based_restate(user_input)
    
    def probe_key_fork(self, context: Dict[str, Any]) -> str:
        """
        提出一个关键分叉问题
        
        Args:
            context: 当前对话上下文
            
        Returns:
            问题字符串
        """
        interpretation = context.get("interpretation", "")
        history = context.get("history", [])
        current_round = context.get("current_round", 1)
        max_rounds = context.get("max_rounds", 10)
        
        # 构建历史文本
        history_text = "\n".join([
            f"{entry.get('role', 'user')}: {entry.get('content', '')}"
            for entry in history[-6:]  # 只取最近3轮对话
        ])
        
        # 使用 LLM 生成追问
        prompt = self.prompt_manager.build_probe_prompt(
            interpretation, history_text, current_round, max_rounds
        )
        
        messages = [
            {"role": "system", "content": "你是一个文献检索辅助助手，帮助用户明确研究方向。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.llm_client.chat(messages, temperature=0.7)
            return response
        except Exception as e:
            # 降级到规则逻辑
            print(f"LLM 调用失败，使用规则逻辑: {e}")
            return self._rule_based_probe(interpretation)
    
    def should_converge(self, round_count: int, max_rounds: int) -> bool:
        """判断是否应该收敛"""
        return round_count >= max_rounds
    
    def confirm_interpretation(self, user_choice: str, options: List[str]) -> str:
        """确认用户选择"""
        if user_choice.lower() in ['a', '1']:
            return options[0] if len(options) > 0 else ""
        elif user_choice.lower() in ['b', '2']:
            return options[1] if len(options) > 1 else ""
        elif user_choice.lower() in ['c', '3']:
            return options[2] if len(options) > 2 else ""
        else:
            return user_choice  # 用户自定义输入
    
    def _parse_restate_response(self, response: str) -> tuple:
        """解析复述回复"""
        lines = response.strip().split('\n')
        
        restatement = ""
        options = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测选项（以数字或字母开头）
            if re.match(r'^[1-9]\.', line) or re.match(r'^[A-C]\.', line, re.IGNORECASE):
                # 提取选项文本
                option = re.sub(r'^[1-9]\.\s*', '', line)
                option = re.sub(r'^[A-C]\.\s*', '', option, flags=re.IGNORECASE)
                options.append(option)
            elif not restatement and len(line) > 10:
                restatement = line
        
        if not restatement:
            restatement = "我理解你的研究兴趣。"
        
        if not options:
            options = ["理论研究", "应用实践", "系统实现"]
        
        return restatement, options
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（简单实现）"""
        stop_words = {"我", "想", "要", "做", "的", "了", "是", "在", "和", "与", "或"}
        words = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+', text)
        return [w for w in words if w not in stop_words and len(w) > 1]
    
    def _rule_based_restate(self, user_input: str) -> Dict[str, Any]:
        """基于规则的复述（降级方案）"""
        keywords = self._extract_keywords(user_input)
        
        if "大模型" in user_input or "LLM" in user_input:
            options = [
                "大模型在文献检索中的应用（交互设计方向）",
                "大模型在文献检索中的应用（算法优化方向）",
                "大模型在文献检索中的应用（效果评估方向）"
            ]
        elif "文献" in user_input or "检索" in user_input:
            options = [
                "文献检索系统的用户体验优化",
                "文献检索算法的改进",
                "文献检索效果的评估方法"
            ]
        else:
            options = [
                f"围绕「{'、'.join(keywords[:2])}」的理论研究",
                f"围绕「{'、'.join(keywords[:2])}」的应用实践",
                f"围绕「{'、'.join(keywords[:2])}」的系统实现"
            ]
        
        return {
            "restatement": f"我理解你关注的是「{user_input}」相关的问题。",
            "options": options,
            "keywords": keywords
        }
    
    def _rule_based_probe(self, interpretation: str) -> str:
        """基于规则的追问（降级方案）"""
        if "交互" in interpretation or "设计" in interpretation:
            return "你更关心具体的交互设计方案，还是用户体验评估方法？\nA. 交互设计方案\nB. 用户体验评估\nC. 都关心"
        elif "算法" in interpretation or "检索" in interpretation:
            return "你更关注检索算法的改进，还是检索效果的评估？\nA. 检索算法改进\nB. 检索效果评估\nC. 都关注"
        else:
            return "你想从哪个角度切入这个研究？\nA. 理论分析\nB. 实验验证\nC. 系统实现"
