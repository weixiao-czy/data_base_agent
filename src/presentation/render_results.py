"""
结果展示模块
"""

from typing import List, Dict, Any


def render_results(papers: List[Dict[str, Any]]) -> str:
    """
    渲染检索结果为可读格式
    
    Args:
        papers: 论文列表
        
    Returns:
        格式化后的字符串
    """
    if not papers:
        return "未找到相关论文"
    
    output = []
    for i, paper in enumerate(papers, 1):
        output.append(f"\n[{i}] {paper.get('title', '无标题')}")
        output.append(f"    摘要: {paper.get('abstract', '无摘要')[:200]}...")
        output.append(f"    URL: {paper.get('url', '无链接')}")
        if 'bibtex' in paper:
            output.append(f"    BibTeX: {paper['bibtex'][:100]}...")
    
    return "\n".join(output)


def render_plan_card(plan_card: Dict[str, Any]) -> str:
    """
    渲染需求翻译卡
    
    Args:
        plan_card: 需求翻译卡字典
        
    Returns:
        格式化后的字符串
    """
    output = []
    output.append("\n" + "="*50)
    output.append("需求翻译卡")
    output.append("="*50)
    
    output.append(f"\n研究兴趣: {plan_card.get('research_interest', '')}")
    output.append(f"解读问题: {plan_card.get('interpreted_question', '')}")
    output.append(f"研究类型: {plan_card.get('research_intent_type', '')}")
    
    output.append("\n关键维度:")
    for dim in plan_card.get('key_dimensions', []):
        output.append(f"  - {dim}")
    
    output.append("\n建议关键词:")
    keywords = plan_card.get('suggested_keywords', {})
    output.append(f"  主要: {', '.join(keywords.get('primary', []))}")
    output.append(f"  变体: {', '.join(keywords.get('variants', []))}")
    output.append(f"  相邻领域: {', '.join(keywords.get('adjacent_fields', []))}")
    
    output.append("\n不确定性:")
    for unc in plan_card.get('uncertainties', []):
        output.append(f"  - {unc}")
    
    output.append("\n检索计划:")
    search_plan = plan_card.get('search_plan', {})
    output.append(f"  模式: {search_plan.get('mode', '')}")
    output.append("  建议查询:")
    for query in search_plan.get('suggested_queries', []):
        output.append(f"    - {query}")
    
    output.append("\n下一步行动:")
    for action in plan_card.get('next_actions', []):
        output.append(f"  - {action}")
    
    output.append("\n" + "="*50)
    return "\n".join(output)
