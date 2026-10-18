"""
状态机测试
"""

import pytest
from src.agent.state_machine import StateMachine, AgentState


def test_initial_state():
    """测试初始状态"""
    sm = StateMachine()
    assert sm.current_state == AgentState.IDLE
    assert sm.current_round == 0


def test_transition():
    """测试状态转换"""
    sm = StateMachine()
    sm.transition(AgentState.RESTATE)
    assert sm.current_state == AgentState.RESTATE


def test_increment_round():
    """测试轮次增加"""
    sm = StateMachine()
    sm.increment_round()
    assert sm.current_round == 1


def test_can_clarify():
    """测试澄清判断"""
    sm = StateMachine(max_rounds=3)
    assert sm.can_clarify() is True
    
    sm.current_round = 3
    assert sm.can_clarify() is False


def test_reset():
    """测试重置"""
    sm = StateMachine()
    sm.transition(AgentState.RESTATE)
    sm.increment_round()
    sm.reset()
    
    assert sm.current_state == AgentState.IDLE
    assert sm.current_round == 0
