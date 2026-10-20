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
        
        # MockLLMClient 只会返回固定模板，连续多轮会重复同一句。
        # 模拟模式下直接走规则追问，才能体现真实的十轮澄清。
        if isinstance(self.llm_client, MockLLMClient):
            return self._rule_based_probe(interpretation, current_round, history)
        
        try:
            response = self.llm_client.chat(messages, temperature=0.7)
            return response
        except Exception as e:
            # 降级到规则逻辑
            print(f"LLM 调用失败，使用规则逻辑: {e}")
            return self._rule_based_probe(interpretation, current_round, history)
    
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
    
    def _rule_based_probe(self, interpretation: str,
                          current_round: int = 1,
                          history: Optional[List[Dict[str, Any]]] = None) -> str:
        """基于规则的追问（降级方案）
        
        支持多轮：按轮次依次提出不同维度的问题。
        原来固定返回同一句，恢复十轮追问后会连续问同一个问题，
        所以这里按「澄清维度」排布，并结合历史跳过已经收集过的信息。
        """
        # 六个澄清维度，按「从粗到细」排列：
        # 先锁定问题域，再往下切角度、方法、证据、产出、边界
        dimensions = [
            ("研究角度", "你想从哪个角度切入这个研究？",
             ["A. 理论分析", "B. 实验验证", "C. 系统实现"]),
            ("具体场景", "你希望在什么样的具体场景下验证你的想法？",
             ["A. 真实用户/数据集", "B. 公开基准测试", "C. 实验室原型"]),
            ("方法路线", "你更倾向沿用成熟方法，还是探索新方法？",
             ["A. 沿用并改进现有方法", "B. 组合多种方法", "C. 提出全新思路"]),
            ("数据与工具", "你目前手上有可用的数据或工具吗？",
             ["A. 有数据", "B. 有工具/平台", "C. 都还没有"]),
            ("评判标准", "你打算用什么标准判断做得好不好？",
             ["A. 量化指标", "B. 用户研究", "C. 案例分析"]),
            ("产出形式", "最终你希望产出什么？",
             ["A. 论文", "B. 可运行系统", "C. 调研报告"]),
            ("时间与规模", "这个研究的时间尺度大概是？",
             ["A. 一学期内", "B. 一年左右", "C. 长期项目"]),
            ("已知基础", "这个方向上你已经读过哪些工作？",
             ["A. 只了解大概", "B. 读过几篇", "C. 比较熟悉"]),
            ("风险偏好", "你更愿意做稳妥的增量工作，还是高风险高回报的探索？",
             ["A. 稳妥增量", "B. 高风险探索", "C. 两者结合"]),
            ("边界", "有什么是你明确不想做的？",
             ["A. 不想做工程实现", "B. 不想做理论推导", "C. 暂时没有"]),
        ]
        
        # 第 1 轮结合解读中的关键词，让问题更贴合（只在首轮使用，避免重复）
        if current_round <= 1:
            if "交互" in interpretation or "设计" in interpretation:
                return ("你更关心具体的交互设计方案，还是用户体验评估方法？\n"
                        "A. 交互设计方案\nB. 用户体验评估\nC. 都关心")
            if "算法" in interpretation or "检索" in interpretation:
                return ("你更关注检索算法的改进，还是检索效果的评估？\n"
                        "A. 检索算法改进\nB. 检索效果评估\nC. 都关注")
        
        idx = min(max(current_round - 1, 0), len(dimensions) - 1)
        name, question, options = dimensions[idx]
        
        # 若该维度的问题已在历史里出现，往后找一个没问过的。
        # 判重必须比对「问题本身」而不是选项文本：
        # 不同维度的 A 选项往往是「理论分析 / 有数据 / 论文」这类高频词，用选项判重会误伤。
        asked = " ".join(
            str(e.get("content", "")) for e in (history or [])
            if e.get("role") == "agent"
        )
        for offset in range(len(dimensions)):
            _, q, opts = dimensions[(idx + offset) % len(dimensions)]
            if q not in asked:
                question, options = q, opts
                break
        
        return f"{question}\n" + "\n".join(options)
