"""
澄清模块测试
"""

import pytest
from src.agent.clarifier import Clarifier


def test_clarifier_init():
    """测试初始化"""
    clarifier = Clarifier()
    assert clarifier is not None


def test_restate():
    """测试复述功能"""
    clarifier = Clarifier()
    result = clarifier.restate("我想做大模型辅助文献检索")
    
    assert "restatement" in result
    assert "options" in result
    assert isinstance(result["options"], list)


def test_should_converge():
    """测试收敛判断"""
    clarifier = Clarifier()
    
    assert clarifier.should_converge(2, 3) is False
    assert clarifier.should_converge(3, 3) is True
    assert clarifier.should_converge(4, 3) is True
