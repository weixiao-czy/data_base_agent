"""
文献地图（Literature Map）

在原有「需求翻译卡 + 单次检索」之上，补一层「按项目周期组织文献」的能力：
以研究主题为根节点，按 6 个科研维度发散出可执行的检索方向，
每个方向挂真实检索到的文献，产出一张可折叠的交互式思维导图。

对外 API：
    from litmap import build_map, LiteratureMapBuilder

    from search.real_search import RealSearchProvider
    litmap = build_map("retrieval augmented generation", RealSearchProvider())

模块划分：
    models.py    节点与地图数据结构
    terms.py     概念词抽取（无 LLM 时的发散基础）
    expander.py  维度发散（LLM / 规则 双策略）
    builder.py   检索 + 组装
    render.py    HTML / Markdown / JSON 渲染
    cli.py       命令行入口
"""

from .builder import LiteratureMapBuilder, summarize
from .models import LiteratureMap, LitNode
from .render import to_html, to_json, to_markdown

__all__ = [
    "LiteratureMapBuilder",
    "LiteratureMap",
    "LitNode",
    "build_map",
    "summarize",
    "to_html",
    "to_markdown",
    "to_json",
]

__version__ = "0.1.0"


def build_map(topic: str, provider, llm_client=None, **kwargs) -> LiteratureMap:
    """一行代码构建文献地图

    Args:
        topic: 研究主题
        provider: 检索提供者（SearchProvider 子类）
        llm_client: 可选，LLM 客户端；不传则走规则发散
        **kwargs: 透传给 LiteratureMapBuilder（seed_limit / per_topic 等）

    Returns:
        LiteratureMap
    """
    return LiteratureMapBuilder(
        provider=provider, llm_client=llm_client, **kwargs
    ).build(topic)
