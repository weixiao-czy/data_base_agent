"""
需求翻译卡模块：生成结构化的检索计划
"""

from typing import List, Dict, Any
from dataclasses import dataclass, asdict


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
        return asdict(self)
    
    def to_yaml(self) -> str:
        """转换为 YAML 格式字符串"""
        import yaml
        return yaml.dump(self.to_dict(), allow_unicode=True, default_flow_style=False)


class PlanCardGenerator:
    """需求翻译卡生成器"""
    
    def generate(self, clarification_history: List[Dict[str, Any]], 
                 user_input: str, interpretation: str) -> PlanCard:
        """
        根据澄清历史生成需求翻译卡
        
        Args:
            clarification_history: 澄清对话历史
            user_input: 用户原始输入
            interpretation: 最终确认的研究方向
            
        Returns:
            PlanCard 实例
        """
        # 提取关键词
        keywords = self._extract_keywords(interpretation)
        
        # 生成检索查询
        queries = self._generate_queries(keywords, interpretation)
        
        # 确定研究类型
        intent_type = self._determine_intent_type(interpretation)
        
        # 识别不确定性
        uncertainties = self._identify_uncertainties(clarification_history)
        
        return PlanCard(
            research_interest=user_input,
            interpreted_question=interpretation,
            research_intent_type=intent_type,
            key_dimensions=self._extract_dimensions(interpretation),
            suggested_keywords={
                "primary": keywords[:3],
                "variants": keywords[3:6] if len(keywords) > 3 else [],
                "adjacent_fields": self._suggest_adjacent_fields(keywords)
            },
            uncertainties=uncertainties,
            search_plan={
                "mode": "宽泛探索" if len(queries) > 2 else "精准检索",
                "suggested_queries": queries
            },
            next_actions=[
                "调用 SciMaster 检索",
                "导出到 Zotero/EndNote",
                "继续细化关键词"
            ]
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        import re
        stop_words = {"我", "想", "要", "做", "的", "了", "是", "在", "和", "与", "或", "研究", "问题"}
        words = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+', text)
        return [w for w in words if w not in stop_words and len(w) > 1]
    
    def _generate_queries(self, keywords: List[str], interpretation: str) -> List[str]:
        """生成检索查询"""
        queries = []
        
        # 主要查询
        if keywords:
            queries.append(" ".join(keywords[:3]))
        
        # 变体查询
        if len(keywords) > 2:
            queries.append(f"{keywords[0]} {keywords[2]}")
        
        # 英文查询（如果有中文关键词）
        if any('\u4e00' <= c <= '\u9fff' for c in interpretation):
            queries.append(f"{interpretation[:20]} research")
        
        return queries[:3]
    
    def _determine_intent_type(self, interpretation: str) -> str:
        """确定研究意图类型"""
        if "应用" in interpretation or "系统" in interpretation:
            return "项目驱动"
        elif "如何" in interpretation or "怎么" in interpretation:
            return "问题驱动"
        elif "兴趣" in interpretation or "探索" in interpretation:
            return "兴趣驱动"
        else:
            return "不确定"
    
    def _extract_dimensions(self, interpretation: str) -> List[str]:
        """提取研究维度"""
        dimensions = []
        
        if "设计" in interpretation or "交互" in interpretation:
            dimensions.append("交互设计")
        if "算法" in interpretation:
            dimensions.append("算法优化")
        if "评估" in interpretation or "效果" in interpretation:
            dimensions.append("效果评估")
        if "用户" in interpretation or "体验" in interpretation:
            dimensions.append("用户体验")
        
        if not dimensions:
            dimensions = ["理论研究", "实践应用"]
        
        return dimensions
    
    def _identify_uncertainties(self, history: List[Dict[str, Any]]) -> List[str]:
        """识别不确定性"""
        uncertainties = []
        
        # 检查是否有跳过或不知道的回答
        for entry in history:
            content = entry.get("content", "")
            if "不知道" in content or "跳过" in content:
                uncertainties.append("用户对某些方面不够确定，建议进一步探索")
                break
        
        if not uncertainties:
            uncertainties.append("研究方向已初步明确，可在检索过程中进一步细化")
        
        return uncertainties
    
    def _suggest_adjacent_fields(self, keywords: List[str]) -> List[str]:
        """建议相邻领域"""
        adjacent = []
        
        if any(k in keywords for k in ["大模型", "LLM", "AI"]):
            adjacent.extend(["自然语言处理", "信息检索", "人机交互"])
        elif any(k in keywords for k in ["检索", "搜索"]):
            adjacent.extend(["数据挖掘", "知识图谱", "推荐系统"])
        else:
            adjacent.extend(["相关领域研究"])
        
        return adjacent[:3]
