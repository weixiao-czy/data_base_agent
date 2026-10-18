"""
检索提供者测试
"""

import pytest
from src.search.provider import SearchProvider
from src.search.scimaster_mcp import SciMasterMCPProvider
from src.search.scimaster_cli import SciMasterCLIProvider


def test_mcp_provider_init():
    """测试 MCP 提供者初始化"""
    provider = SciMasterMCPProvider()
    assert provider is not None


def test_cli_provider_init():
    """测试 CLI 提供者初始化"""
    provider = SciMasterCLIProvider()
    assert provider is not None


def test_search_returns_list():
    """测试搜索返回列表"""
    provider = SciMasterMCPProvider()
    result = provider.search("test query")
    assert isinstance(result, list)
