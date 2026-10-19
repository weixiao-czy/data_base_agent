"""
真实文献检索提供者（免费、无需 API Key）

数据来源：
- Crossref：覆盖绝大多数已发表期刊/会议论文，返回 DOI、标题、作者、年份、venue、摘要
- arXiv：预印本，计算机科学 / 物理 / 数学等领域覆盖极好

两个来源都用官方公开 HTTP API，通过标准库 urllib 调用，无需额外依赖。
"""

import os
import re
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional

from .provider import SearchProvider


class RealSearchProvider(SearchProvider):
    """组合 Crossref + arXiv 的真实文献检索提供者"""

    def __init__(self, timeout: Optional[int] = None):
        self.timeout = timeout or int(os.getenv("SEARCH_TIMEOUT", "30"))
        self.search_limit = int(os.getenv("SEARCH_DEFAULT_LIMIT", "10"))
        self.user_agent = "LiteratureSearchAgent/1.0 (student research tool)"

    def is_available(self) -> bool:
        """真实公开 API，只要联网就可用"""
        return True

    def search(self, query: str, limit: int = None, **kwargs) -> List[Dict[str, Any]]:
        """
        执行真实检索：先查 Crossref，再补 arXiv，去重后返回。

        Args:
            query: 检索查询词
            limit: 返回结果数量

        Returns:
            论文列表，每篇包含 title/abstract/authors/url/doi/year/venue/source/bibtex
        """
        if limit is None:
            limit = self.search_limit

        papers: List[Dict[str, Any]] = []
        seen_doi = set()
        seen_title = set()

        # 1) Crossref
        for p in self._search_crossref(query, limit):
            key = self._dedup_key(p)
            if key in seen_doi:
                continue
            seen_doi.add(key)
            seen_title.add(self._norm_title(p.get("title", "")))
            papers.append(p)

        # 2) arXiv（补足 Crossref 里没有的预印本）
        remaining = max(0, limit - len(papers))
        if remaining > 0:
            for p in self._search_arxiv(query, remaining + 3):
                norm = self._norm_title(p.get("title", ""))
                key = self._dedup_key(p)
                if key in seen_doi or norm in seen_title:
                    continue
                seen_doi.add(key)
                seen_title.add(norm)
                papers.append(p)
                if len(papers) >= limit:
                    break

        return papers[:limit]

    # ---------------- Crossref ----------------

    def _search_crossref(self, query: str, limit: int) -> List[Dict[str, Any]]:
        params = {
            "query.bibliographic": query,
            "rows": str(min(limit, 20)),
            "select": "DOI,title,author,issued,container-title,abstract,URL,type",
        }
        url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
        data = self._http_get_json(url)
        if not data:
            return []

        items = data.get("message", {}).get("items", [])
        results = []
        for it in items:
            title_list = it.get("title") or []
            title = self._clean_text(title_list[0]) if title_list else ""
            if not title:
                continue

            authors = []
            for a in (it.get("author") or []):
                if "family" in a or "given" in a:
                    name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                else:
                    name = a.get("name", "")
                if name:
                    authors.append(name)

            year = ""
            issued = it.get("issued", {}).get("date-parts", [[None]])
            if issued and issued[0] and issued[0][0]:
                year = str(issued[0][0])

            venue_list = it.get("container-title") or []
            venue = self._clean_text(venue_list[0]) if venue_list else it.get("type", "")

            doi = it.get("DOI", "")
            paper_url = it.get("URL") or (f"https://doi.org/{doi}" if doi else "")

            abstract = self._clean_text(it.get("abstract", ""))

            results.append({
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "url": paper_url,
                "doi": doi,
                "year": year,
                "venue": venue,
                "source": "Crossref",
                "bibtex": self._build_bibtex(title, authors, year, venue, doi),
            })
        return results

    # ---------------- arXiv ----------------

    def _search_arxiv(self, query: str, limit: int) -> List[Dict[str, Any]]:
        params = {
            "search_query": f"all:{query}",
            "start": "0",
            "max_results": str(min(limit, 20)),
        }
        url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
        xml_text = self._http_get_text(url)
        if not xml_text:
            return []

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        results = []
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return []

        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            title = self._clean_text(title_el.text if title_el is not None else "")
            if not title:
                continue

            authors = []
            for a in entry.findall("atom:author", ns):
                name_el = a.find("atom:name", ns)
                if name_el is not None and name_el.text:
                    authors.append(name_el.text.strip())

            summary_el = entry.find("atom:summary", ns)
            abstract = self._clean_text(summary_el.text if summary_el is not None else "")

            published_el = entry.find("atom:published", ns)
            year = ""
            if published_el is not None and published_el.text:
                year = published_el.text[:4]

            link_el = entry.find("atom:id", ns)
            paper_url = link_el.text.strip() if link_el is not None and link_el.text else ""

            # arXiv 没有传统 DOI，用 arXiv id 作为标识
            arxiv_id = paper_url.rsplit("/", 1)[-1] if paper_url else ""

            results.append({
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "url": paper_url,
                "doi": "",
                "year": year,
                "venue": "arXiv preprint",
                "source": "arXiv",
                "bibtex": self._build_bibtex(title, authors, year, "arXiv", arxiv_id),
            })
        return results

    # ---------------- helpers ----------------

    def _http_get_json(self, url: str) -> Optional[Dict[str, Any]]:
        text = self._http_get_text(url)
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def _http_get_text(self, url: str) -> Optional[str]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            print(f"[检索请求失败] {url} -> {e}")
            return None

    @staticmethod
    def _clean_text(text: str) -> str:
        """去除 HTML/JATS 标签并规整空白"""
        if not text:
            return ""
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def _norm_title(title: str) -> str:
        return re.sub(r"[^a-z0-9\u4e00-\u9fa5]", "", (title or "").lower())

    @classmethod
    def _dedup_key(cls, paper: Dict[str, Any]) -> str:
        doi = paper.get("doi", "")
        if doi:
            return f"doi:{doi.lower()}"
        return f"url:{paper.get('url', '').lower()}"

    @staticmethod
    def _build_bibtex(title: str, authors: List[str], year: str,
                      venue: str, key: str) -> str:
        cite_key = re.sub(r"[^A-Za-z0-9]", "", (authors[0].split()[-1] if authors else "ref"))
        cite_key = f"{cite_key}{year}" if cite_key else (key or "ref")
        author_str = " and ".join(authors)
        lines = [
            f"@article{{{cite_key},",
            f"  title = {{{title}}},",
        ]
        if author_str:
            lines.append(f"  author = {{{author_str}}},")
        if year:
            lines.append(f"  year = {{{year}}},")
        if venue:
            lines.append(f"  journal = {{{venue}}},")
        if key and not key.startswith("10."):
            lines.append(f"  eprint = {{{key}}},")
        lines.append("}")
        return "\n".join(lines)
