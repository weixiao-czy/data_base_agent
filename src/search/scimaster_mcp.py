"""
SciMaster MCP 调用实现

通过 MCP Python SDK 连接 scimaster-cli（Node.js MCP Server），
调用 search_papers 工具执行真实文献检索。
失败时返回空列表，由上层自动降级到 Crossref/arXiv。
"""

import os
import asyncio
import json
import re
from typing import List, Dict, Any, Optional
from .provider import SearchProvider
from dotenv import load_dotenv

load_dotenv()


class SciMasterMCPProvider(SearchProvider):
    """通过 MCP 协议调用 SciMaster 检索"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("SCIMASTER_API_KEY")
        self.base_url = base_url or os.getenv("SCIMASTER_BASE_URL", "https://scimaster.bohrium.com")
        self.search_limit = int(os.getenv("SEARCH_DEFAULT_LIMIT", "10"))
        self.timeout = int(os.getenv("SEARCH_TIMEOUT", "30"))

    def is_available(self) -> bool:
        """检查是否具备调用条件：真实 API Key + npx 可用"""
        if not self.api_key:
            return False
        placeholder = "your-scimaster-api-key-here"
        if self.api_key.strip().lower() == placeholder:
            return False
        # 检查 npx 是否可用（scimaster-cli 通过 npx 启动）
        import shutil
        return shutil.which("npx") is not None

    def search(self, query: str, limit: int = None, **kwargs) -> List[Dict[str, Any]]:
        """
        通过 MCP 调用 search_papers

        Args:
            query: 检索查询词
            limit: 返回结果数量

        Returns:
            论文列表，每篇包含 title/abstract/authors/url/doi/year/venue/source/bibtex
            失败时返回空列表（触发上层降级）
        """
        if limit is None:
            limit = self.search_limit

        if not self.is_available():
            return []

        try:
            return asyncio.run(self._mcp_search(query, limit))
        except Exception as e:
            print(f"[SciMaster MCP] 调用失败: {e}（将降级到 Crossref/arXiv）")
            return []

    async def _mcp_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """异步执行 MCP 调用"""
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client, StdioServerParameters

        # 通过环境变量将 API Key 传递给 scimaster-cli
        env = os.environ.copy()
        env["SCIMASTER_API_KEY"] = self.api_key

        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "scimaster-cli"],
            env=env,
        )

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                # 调用 search_papers 工具
                result = await session.call_tool(
                    "search_papers",
                    arguments={"query": query, "limit": limit},
                )

        return self._parse_response(result, query)

    def _parse_response(self, result, query: str) -> List[Dict[str, Any]]:
        """解析 MCP 工具返回结果"""
        papers = []

        # MCP call_tool 返回 CallToolResult，content 是列表
        content_list = result.content if hasattr(result, "content") else []

        for content in content_list:
            # content 可能是 TextContent 对象
            text = content.text if hasattr(content, "text") else str(content)

            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                continue

            # SciMaster 返回格式可能是列表或包含 papers 字段的对象
            items = data if isinstance(data, list) else data.get("papers", data.get("results", []))

            for item in items:
                paper = self._normalize_paper(item, query)
                if paper and paper.get("title"):
                    papers.append(paper)

        return papers

    def _normalize_paper(self, item: Dict[str, Any], query: str) -> Optional[Dict[str, Any]]:
        """将 SciMaster 返回的论文标准化为统一格式"""
        title = item.get("title") or item.get("paper_title") or ""
        if not title:
            return None

        authors = item.get("authors") or item.get("author") or []
        if isinstance(authors, str):
            authors = [a.strip() for a in authors.split(",") if a.strip()]

        year = item.get("year") or item.get("published_year") or ""
        venue = item.get("venue") or item.get("journal") or item.get("conference") or ""
        doi = item.get("doi") or ""
        url = item.get("url") or item.get("link") or (f"https://doi.org/{doi}" if doi else "")
        abstract = item.get("abstract") or item.get("summary") or ""

        # 生成 BibTeX
        bibtex = self._build_bibtex(title, authors, year, venue, doi)

        return {
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "url": url,
            "doi": doi,
            "year": str(year),
            "venue": venue,
            "source": "SciMaster",
            "bibtex": bibtex,
        }

    @staticmethod
    def _build_bibtex(title: str, authors: List[str], year: str,
                      venue: str, doi: str) -> str:
        cite_key = re.sub(r"[^A-Za-z0-9]", "", (authors[0].split()[-1] if authors else "ref"))
        cite_key = f"{cite_key}{year}" if cite_key else (doi or "ref")
        author_str = " and ".join(authors)
        lines = [f"@article{{{cite_key},", f"  title = {{{title}}},"]
        if author_str:
            lines.append(f"  author = {{{author_str}}},")
        if year:
            lines.append(f"  year = {{{year}}},")
        if venue:
            lines.append(f"  journal = {{{venue}}},")
        if doi:
            lines.append(f"  doi = {{{doi}}},")
        lines.append("}")
        return "\n".join(lines)
