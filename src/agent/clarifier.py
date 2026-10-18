"""
澄清模块：复述、分叉、收敛逻辑
"""

from typing import List, Dict, Any
import re


class Clarifier:
    """对话澄清器：实现复述、分叉、收敛逻辑"""
    
    def __init__(self):
        self.interpretations = []
    
    def restate(self, user_input: str) -> Dict[str, Any]:
        """
        复述用户输入，给出 2-3 种可能的解读
        
        Args:
            user_input: 用户原始输入
            
        Returns:
            包含复述和选项的字典
        """
        # 简单的规则-based 复述逻辑
        # 实际项目中应该使用 LLM
        
        # 检测关键词
        keywords = self._extract_keywords(user_input)
        
        # 生成解读选项
        options = self._generate_interpretations(keywords, user_input)
        
        return {
            "restatement": f"我理解你关注的是「{user_input}」相关的问题。",
            "options": options,
            "keywords": keywords
        }
    
    def probe_key_fork(self, context: Dict[str, Any]) -> str:
        """
        提出一个关键分叉问题
        
        Args:
            context: 当前对话上下文
            
        Returns:
            问题字符串
        """
        # 根据上下文生成关键分叉问题
        current_interpretation = context.get("interpretation", "")
        
        # 简单的规则逻辑
        if "交互" in current_interpretation or "设计" in current_interpretation:
            return "你更关心具体的交互设计方案，还是用户体验评估方法？\nA. 交互设计方案\nB. 用户体验评估\nC. 都关心"
        elif "算法" in current_interpretation or "检索" in current_interpretation:
            return "你更关注检索算法的改进，还是检索效果的评估？\nA. 检索算法改进\nB. 检索效果评估\nC. 都关注"
        else:
            return "你想从哪个角度切入这个研究？\nA. 理论分析\nB. 实验验证\nC. 系统实现"
    
    def should_converge(self, round_count: int, max_rounds: int) -> bool:
        """判断是否应该收敛"""
        return round_count >= max_rounds
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（简单实现）"""
        # 实际项目中应该使用 NLP 工具或 LLM
        stop_words = {"我", "想", "要", "做", "的", "了", "是", "在", "和", "与", "或"}
        words = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+', text)
        return [w for w in words if w not in stop_words and len(w) > 1]
    
    def _generate_interpretations(self, keywords: List[str], original: str) -> List[str]:
        """生成解读选项"""
        # 简单的规则逻辑，实际应该用 LLM
        if "大模型" in original or "LLM" in original:
            return [
                "大模型在文献检索中的应用（交互设计方向）",
                "大模型在文献检索中的应用（算法优化方向）",
                "大模型在文献检索中的应用（效果评估方向）"
            ]
        elif "文献" in original or "检索" in original:
            return [
                "文献检索系统的用户体验优化",
                "文献检索算法的改进",
                "文献检索效果的评估方法"
            ]
        else:
            return [
                f"围绕「{'、'.join(keywords[:2])}」的理论研究",
                f"围绕「{'、'.join(keywords[:2])}」的应用实践",
                f"围绕「{'、'.join(keywords[:2])}」的系统实现"
            ]
    
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
