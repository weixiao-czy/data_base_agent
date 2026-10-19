"""
检索服务测试脚本
"""

import sys
import io
sys.path.insert(0, 'src')

# Windows GBK 控制台兜底，避免中文/符号导致 UnicodeEncodeError
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass

from search.real_search import RealSearchProvider
from search.scimaster_mcp import SciMasterMCPProvider
from search.scimaster_cli import SciMasterCLIProvider


def _print_paper(paper):
    print(f"    标题: {paper.get('title', '无标题')}")
    authors = paper.get('authors', [])
    if authors:
        print(f"    作者: {', '.join(authors[:4])}")
    print(f"    年份: {paper.get('year', '未知')} | 来源: {paper.get('source', '-')}")
    print(f"    venue: {paper.get('venue', '-')}")
    print(f"    DOI: {paper.get('doi', '无')}")
    print(f"    链接: {paper.get('url', '无链接')}")
    abstract = paper.get('abstract', '')
    if abstract:
        print(f"    摘要: {abstract[:120]}...")


def test_search_providers():
    print("=" * 60)
    print("检索服务测试")
    print("=" * 60)

    # [1] 真实检索（Crossref + arXiv）
    print("\n[1] 测试真实检索 Provider（Crossref + arXiv）")
    try:
        provider = RealSearchProvider()
        print(f"  可用: {provider.is_available()}")
        print("  执行测试检索: 'large language model literature retrieval'")
        results = provider.search("large language model literature retrieval", limit=5)
        print(f"  找到 {len(results)} 篇论文")
        if results:
            print("\n  第一篇论文:")
            _print_paper(results[0])
            print("\n  所有标题:")
            for i, p in enumerate(results, 1):
                print(f"    {i}. [{p.get('source', '-')}] {p.get('title', '')[:70]}")
        else:
            print("  [ERROR] 未返回结果，请检查网络连接")
    except Exception as e:
        print(f"  [ERROR] 真实检索测试失败: {e}")

    # [2] SciMaster MCP（当前未实现真实调用，应诚实返回不可用/空）
    print("\n[2] 测试 SciMaster MCP Provider")
    try:
        mcp_provider = SciMasterMCPProvider()
        print(f"  API Key: {'已配置' if mcp_provider.api_key else '未配置'}")
        print(f"  可用: {mcp_provider.is_available()}")
        print("  说明: MCP 真实调用尚未实现，当前不会返回 mock 数据")
    except Exception as e:
        print(f"  [ERROR] MCP Provider 测试失败: {e}")

    # [3] SciMaster CLI 降级
    print("\n[3] 测试 SciMaster CLI Provider")
    try:
        cli_provider = SciMasterCLIProvider()
        print(f"  CLI 命令: {cli_provider.cli_command}")
        print(f"  可用: {cli_provider.is_available()}")
        if not cli_provider.is_available():
            print("  CLI 不可用（可能未安装 scimaster-cli）")
    except Exception as e:
        print(f"  [ERROR] CLI Provider 测试失败: {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_search_providers()
