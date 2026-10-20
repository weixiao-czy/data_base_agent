"""
文献地图构建器

流程：
    1. 用研究主题检索种子文献（定位领域坐标系）
    2. 抽取概念词 / 交给大模型，把主题发散成 6 个维度的子主题
    3. 逐个子主题检索真实文献
    4. 全局去重后组装成层级树

设计要点：
    - 每篇文献在全图只出现一次（挂在最先命中的节点），避免导图被重复条目撑爆
    - 请求之间留间隔，遵守 Crossref / arXiv 的访问礼节
    - 任一子主题检索失败不影响整体，记录到 meta.errors
"""

import re
import time
from typing import Any, Callable, Dict, List, Optional, Sequence

from .expander import ASPECT_LABELS, make_expander
from .models import (
    KIND_ASPECT,
    KIND_ROOT,
    KIND_TOPIC,
    LiteratureMap,
    LitNode,
    _paper_key,
    paper_brief,
)

ProgressFn = Callable[[str], None]

_CJK_RE = re.compile(r"[\u4e00-\u9fa5]")


class LiteratureMapBuilder:
    """把「一个主题」变成「一张文献地图」"""

    def __init__(
        self,
        provider,
        llm_client=None,
        seed_limit: int = 8,
        per_topic: int = 3,
        topics_per_aspect: int = 3,
        max_queries: int = 20,
        request_interval: float = 0.4,
        progress: Optional[ProgressFn] = None,
    ):
        """
        Args:
            provider: 检索提供者（复用 search/ 下的 SearchProvider）
            llm_client: LLM 客户端，None 则走规则发散
            seed_limit: 种子文献数量
            per_topic: 每个子主题取几篇
            topics_per_aspect: 每个维度生成几个子主题
            max_queries: 检索请求上限（控制耗时与 API 压力）
            request_interval: 请求间隔秒数
            progress: 进度回调，默认打印到 stdout
        """
        self.provider = provider
        self.llm = llm_client
        self.seed_limit = seed_limit
        self.per_topic = per_topic
        self.topics_per_aspect = topics_per_aspect
        self.max_queries = max_queries
        self.request_interval = request_interval
        self._progress = progress or (lambda msg: print(msg, flush=True))

    # ------------------------------------------------------------ build

    def build(self, topic: str) -> LiteratureMap:
        """构建文献地图"""
        errors: List[str] = []
        search_topic = self._resolve_search_topic(topic)

        self._progress(f"[1/4] 检索种子文献：{search_topic}")
        if search_topic != topic:
            self._progress(f"      （显示主题：{topic}）")

        seeds = self._safe_search(search_topic, self.seed_limit, errors,
                                  label="种子文献")
        self._progress(f"      得到 {len(seeds)} 篇种子文献")
        if not seeds:
            self._progress(
                "      ⚠ 没有检索到种子文献：检查网络，或换更常用的英文表述"
            )

        root = LitNode(id="root", label=topic, kind=KIND_ROOT,
                       note="研究主题", papers=[])

        # 种子文献单独成一个维度，方便对照「我已知的 vs 我应该补的」
        if seeds:
            seed_node = root.new_child(
                "种子文献", kind=KIND_ASPECT,
                note="直接以主题检索到的代表性文献，作为发散起点",
            )
            seed_node.papers = [self._decorate(p, search_topic) for p in seeds]

        self._progress("[2/4] 发散研究维度")
        expander = make_expander(self.llm, self.topics_per_aspect)
        aspects = expander.expand(search_topic, seeds)
        strategy = "大模型" if getattr(expander, "name", "") == "llm" else "规则模板"
        self._progress(
            f"      策略：{strategy}，共 {len(aspects)} 个维度 / "
            f"{sum(len(a.topics) for a in aspects)} 个检索方向"
        )

        # 全局去重：种子文献已占用
        seen = set()
        for p in seeds:
            seen.add(_paper_key(p))

        self._progress("[3/4] 按维度展开检索")
        queries_used = 1  # 种子检索已算一次
        reused = 0

        for aspect in aspects:
            aspect_node = root.new_child(
                aspect.label, kind=KIND_ASPECT,
                note=aspect.note or ASPECT_LABELS.get(aspect.key, ""),
            )
            for tp in aspect.topics:
                if queries_used >= self.max_queries:
                    errors.append(f"已达检索上限 {self.max_queries}，跳过剩余方向")
                    break

                self._progress(f"      · {aspect.label} / {tp.label}  ←  {tp.query}")
                results = self._safe_search(
                    tp.query, self.per_topic, errors, label=tp.query
                )
                queries_used += 1

                topic_node = aspect_node.new_child(
                    tp.label, kind=KIND_TOPIC, query=tp.query,
                    note=f"检索式：{tp.query}",
                )

                kept: List[Dict[str, Any]] = []
                for p in results:
                    key = _paper_key(p)
                    if key in seen:
                        reused += 1
                        continue
                    seen.add(key)
                    kept.append(self._decorate(p, tp.query))

                topic_node.papers = kept
                if not kept:
                    topic_node.note += "（该方向暂无新增文献，可能已被上层覆盖）"

        # 清理：没有任何文献的分支会让导图显得空，但保留结构以便用户自己补
        self._progress("[4/4] 组装层级结构")

        meta = {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "search_topic": search_topic,
            "seed_count": len(seeds),
            "strategy": strategy,
            "queries_used": queries_used,
            "duplicates_removed": reused,
            "per_topic": self.per_topic,
            "errors": errors[:20],
        }
        return LiteratureMap(topic=topic, root=root, meta=meta)

    # ------------------------------------------------------------ helpers

    def _resolve_search_topic(self, topic: str) -> str:
        """Crossref / arXiv 以英文索引为主，中文主题直接检索基本查不到东西

        有大模型时自动翻译成英文检索用语；没有就明确告知用户，避免他拿到
        一张全是空节点的导图却不知道原因。
        """
        if not _CJK_RE.search(topic) or self.llm is None:
            if _CJK_RE.search(topic):
                self._progress(
                    "      ⚠ 检测到中文主题：Crossref/arXiv 以英文索引为主，"
                    "建议换成英文主题（配置 OPENAI_API_KEY 后可自动翻译）"
                )
            return topic

        try:
            eng = self.llm.chat([
                {"role": "user", "content": (
                    "把下面的研究主题翻译成最常用于英文论文检索的表达，"
                    "只输出英文本身，不要引号、不要解释：\n" + topic
                )}
            ])
            eng = (eng or "").strip().strip('"').strip().splitlines()[0].strip()
            if eng and not _CJK_RE.search(eng) and len(eng) <= 160:
                self._progress(f"      已自动翻译为检索用语：{eng}")
                return eng
        except Exception as e:  # noqa: BLE001
            self._progress(f"      主题翻译失败（{e}），按原文检索")
        return topic

    def _safe_search(
        self,
        query: str,
        limit: int,
        errors: List[str],
        label: str = "",
    ) -> List[Dict[str, Any]]:
        """单次检索，失败不抛出，只记录"""
        try:
            results = self.provider.search(query, limit=limit)
            return results or []
        except Exception as e:  # noqa: BLE001 - 外部 API，什么错都可能有
            errors.append(f"{label or query}: {e}")
            return []
        finally:
            if self.request_interval:
                time.sleep(self.request_interval)

    @staticmethod
    def _decorate(paper: Dict[str, Any], via: str) -> Dict[str, Any]:
        """裁剪 + 记录出处检索式"""
        brief = paper_brief(paper)
        brief["via"] = via
        return brief


def summarize(litmap: LiteratureMap) -> str:
    """生成一段人可读的地图摘要"""
    d = litmap.to_dict()
    lines = [
        f"主题：{d['topic']}",
        f"文献：{d['stats']['total_papers']} 篇 / 检索方向：{d['stats']['total_topics']} 个"
        f" / 节点：{d['stats']['total_nodes']} 个",
        "",
    ]
    for aspect in litmap.root.children:
        lines.append(
            f"  {aspect.label}（{aspect.total_paper_count} 篇）"
        )
        for topic in aspect.children:
            n = topic.total_paper_count
            mark = "·" if n else "×"
            lines.append(f"    {mark} {topic.label}  —— {topic.query}  [{n}]")
    return "\n".join(lines)
