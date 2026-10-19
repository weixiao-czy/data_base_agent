"""
检索服务测试脚本
"""

import sys
sys.path.insert(0, 'src')

from search.scimaster_mcp import SciMasterMCPProvider
from search.scimaster_cli import SciMasterCLIProvider


def test_search_providers():
    """测试检索服务"""
    print("="*60)
    print("检索服务测试")
    print("="*60)
    
    # 测试 MCP 提供者
    print("\n[1] 测试 SciMaster MCP Provider")
    try:
        mcp_provider = SciMasterMCPProvider()
        print(f"  API Key: {'已配置' if mcp_provider.api_key else '未配置'}")
        print(f"  Base URL: {mcp_provider.base_url}")
        print(f"  可用: {mcp_provider.is_available()}")
        
        if mcp_provider.is_available():
            print("\n  执行测试检索...")
            results = mcp_provider.search("大模型 文献检索", limit=3)
            print(f"  找到 {len(results)} 篇论文")
            
            if results:
                print("\n  第一篇论文:")
                paper = results[0]
                print(f"    标题: {paper.get('title', '无标题')}")
                print(f"    作者: {', '.join(paper.get('authors', []))}")
                print(f"    年份: {paper.get('year', '未知')}")
                print(f"    链接: {paper.get('url', '无链接')}")
    except Exception as e:
        print(f"  [ERROR] MCP Provider 测试失败: {e}")
    
    # 测试 CLI 提供者
    print("\n[2] 测试 SciMaster CLI Provider")
    try:
        cli_provider = SciMasterCLIProvider()
        print(f"  CLI 命令: {cli_provider.cli_command}")
        print(f"  可用: {cli_provider.is_available()}")
        
        if cli_provider.is_available():
            print("\n  执行测试检索...")
            results = cli_provider.search("大模型 文献检索", limit=3)
            print(f"  找到 {len(results)} 篇论文")
        else:
            print("  CLI 不可用（可能未安装 scimaster-cli）")
    except Exception as e:
        print(f"  [ERROR] CLI Provider 测试失败: {e}")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    test_search_providers()
