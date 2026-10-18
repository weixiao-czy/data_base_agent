"""
状态机模块：控制对话流程与轮次
"""

from enum import Enum, auto
from typing import Optional


class AgentState(Enum):
    """Agent 状态枚举"""
    IDLE = auto()                    # 等待用户初始描述
    RESTATE = auto()                 # 复述并给选项
    CONFIRM_INTERPRETATION = auto()  # 确认理解
    PROBE_KEY_FORK = auto()          # 关键分叉追问
    GENERATE_PLAN_CARD = auto()      # 生成需求翻译卡
    USER_CONFIRM = auto()            # 用户确认
    CALL_SEARCH = auto()             # 调用检索工具
    PRESENT_RESULTS = auto()         # 展示结果
    FALLBACK = auto()                # 降级处理


class StateMachine:
    """状态机：管理对话状态与轮次控制"""
    
    def __init__(self, max_rounds: int = 3):
        self.current_state = AgentState.IDLE
        self.max_rounds = max_rounds
        self.current_round = 0
        self.clarification_history = []
    
    def transition(self, next_state: AgentState) -> None:
        """状态转换"""
        self.current_state = next_state
    
    def increment_round(self) -> None:
        """增加澄清轮次"""
        self.current_round += 1
    
    def can_clarify(self) -> bool:
        """是否还能继续澄清"""
        return self.current_round < self.max_rounds
    
    def reset(self) -> None:
        """重置状态机"""
        self.current_state = AgentState.IDLE
        self.current_round = 0
        self.clarification_history.clear()
