"""
需求翻译卡模块：生成结构化的检索计划
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class PlanCard:
    """需求翻译卡数据结构"""
    research_interest: str
    interpreted_question: str
    research_intent_type: str  # 兴趣驱动 | 问题驱动 | 项目驱动 | 不确定
    key_dimensions: List[str]
    suggested_keywords: Dict[str, List[str]]
    uncertainties: List[str]
    search_plan: Dict[str, Any]
    next_actions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "research_interest": self.research_interest,
            "interpreted_question": self.interpreted_question,
            "research_intent_type": self.research_intent_type,
            "key_dimensions": self.key_dimensions,
            "suggested_keywords": self.suggested_keywords,
            "uncertainties": self.uncertainties,
            "search_plan": self.search_plan,
            "next_actions": self.next_actions
        }


class PlanCardGenerator:
    """需求翻译卡生成器"""
    
    def generate(self, clarification_history: List[Dict[str, Any]]) -> PlanCard:
        """
        根据澄清历史生成需求翻译卡
        
        Args:
            clarification_history: 澄清对话历史
            
        Returns:
            PlanCard 实例
        """
        # TODO: 实现生成逻辑
        return PlanCard(
            research_interest="",
            interpreted_question="",
            research_intent_type="不确定",
            key_dimensions=[],
            suggested_keywords={"primary": [], "variants": [], "adjacent_fields": []},
            uncertainties=[],
            search_plan={"mode": "宽泛探索", "suggested_queries": []},
            next_actions=[]
        )
