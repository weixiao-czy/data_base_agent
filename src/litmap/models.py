"""
文献地图数据模型

层级结构：
    root  研究主题
      └─ aspect  研究维度（综述 / 方法 / 应用 / 数据集 / 挑战 / 前沿）
           └─ topic  子主题（一个可执行的检索方向）
                └─ paper  文献条目（叶子）

与原有 agent/plan_card.py 的定位不同：需求翻译卡面向「一次检索」，
文献地图面向「一个项目周期内的文献获取路线」，强调层级与覆盖面。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional
from datetime import datetime

# 节点类型
KIND_ROOT = "root"
KIND_ASPECT = "aspect"
KIND_TOPIC = "topic"
KIND_PAPER = "paper"


@dataclass
class LitNode:
    """文献地图节点"""

    id: str
    label: str
    kind: str = KIND_TOPIC
    query: str = ""
    note: str = ""
    papers: List[Dict[str, Any]] = field(default_factory=list)
    children: List["LitNode"] = field(default_factory=list)

    # ---------- 组装 ----------

    def add_child(self, node: "LitNode") -> "LitNode":
        self.children.append(node)
        return node

    def new_child(self, label: str, kind: str = KIND_TOPIC,
                  query: str = "", note: str = "") -> "LitNode":
        node = LitNode(
            id=f"{self.id}/{_slug(label, len(self.children))}",
            label=label,
            kind=kind,
            query=query,
            note=note,
        )
        self.children.append(node)
        return node

    # ---------- 统计 ----------

    @property
    def own_paper_count(self) -> int:
        return len(self.papers)

    @property
    def total_paper_count(self) -> int:
        """含所有子孙节点的文献数"""
        return len(self.papers) + sum(c.total_paper_count for c in self.children)

    @property
    def topic_count(self) -> int:
        """可执行检索方向数量"""
        return (1 if self.kind == KIND_TOPIC else 0) + sum(
            c.topic_count for c in self.children
        )

    # ---------- 遍历 ----------

    def walk(self) -> Iterator["LitNode"]:
        yield self
        for c in self.children:
            yield from c.walk()

    def all_papers(self) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        seen = set()
        for node in self.walk():
            for p in node.papers:
                key = _paper_key(p)
                if key in seen:
                    continue
                seen.add(key)
                item = dict(p)
                item["_node"] = node.label
                out.append(item)
        return out

    # ---------- 序列化 ----------

    def to_dict(self, depth: int = 0) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "kind": self.kind,
            "query": self.query,
            "note": self.note,
            "depth": depth,
            "paper_count": self.own_paper_count,
            "total_paper_count": self.total_paper_count,
            "papers": self.papers,
            "children": [c.to_dict(depth + 1) for c in self.children],
        }


@dataclass
class LiteratureMap:
    """一张完整的文献地图"""

    topic: str
    root: LitNode
    meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_papers(self) -> int:
        return len(self.root.all_papers())

    @property
    def total_topics(self) -> int:
        return self.root.topic_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "generated_at": self.meta.get(
                "generated_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            "meta": {k: v for k, v in self.meta.items() if k != "generated_at"},
            "stats": {
                "total_papers": self.total_papers,
                "total_topics": self.total_topics,
                "total_nodes": sum(1 for _ in self.root.walk()),
            },
            "root": self.root.to_dict(),
        }


# ---------------- helpers ----------------

def _slug(text: str, fallback: int = 0) -> str:
    """生成稳定的节点 id 片段（保留中英文，去掉符号）"""
    keep = [c for c in (text or "") if c.isalnum() or "\u4e00" <= c <= "\u9fa5"]
    s = "".join(keep)[:24].lower()
    return s or f"n{fallback}"


def _paper_key(p: Dict[str, Any]) -> str:
    """论文去重键：DOI > arXiv url > 标题"""
    doi = (p.get("doi") or "").strip().lower()
    if doi:
        return f"doi:{doi}"
    url = (p.get("url") or "").strip().lower()
    if url:
        return f"url:{url}"
    return "title:" + "".join((p.get("title") or "").lower().split())


def paper_brief(p: Dict[str, Any]) -> Dict[str, Any]:
    """裁剪论文记录，避免地图数据过于臃肿"""
    abstract = p.get("abstract") or ""
    return {
        "title": p.get("title", ""),
        "authors": (p.get("authors") or [])[:6],
        "year": p.get("year", ""),
        "venue": p.get("venue", ""),
        "doi": p.get("doi", ""),
        "url": p.get("url", ""),
        "source": p.get("source", ""),
        "abstract": (abstract[:400] + "…") if len(abstract) > 400 else abstract,
        "cited_by": p.get("cited_by"),
    }
