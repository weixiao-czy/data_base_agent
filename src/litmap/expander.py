"""
维度发散：把研究主题拆成 6 个科研维度，并为每个维度生成可执行的检索方向

两种策略：
  - LLMExpander  ：有大模型时，由模型结合种子文献生成子主题（层级更贴合领域）
  - RuleExpander ：无大模型时，用概念词 × 维度模板组合（离线可用，保证不空转）

两者输出结构一致，builder 无需关心来源。
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from .terms import (
    extract_acronyms,
    extract_terms,
    extract_title_terms,
    topic_terms,
)


@dataclass
class TopicPlan:
    """一个可执行的检索方向"""
    label: str
    query: str


@dataclass
class AspectPlan:
    """一个研究维度"""
    key: str
    label: str
    note: str = ""
    topics: List[TopicPlan] = field(default_factory=list)


# 六个维度：覆盖「做一个项目要读哪些文献」的完整闭环
# templates 里每项是 (英文检索修饰词, 中文标签)：
#   有概念词时用「概念词 + 修饰词」，标签取概念词；
#   概念词不足时退回「主题 + 修饰词」，标签取中文，避免出现 "Approach" 这种空标签
ASPECT_SPECS = [
    {
        "key": "survey",
        "label": "综述与奠基",
        "note": "先建立全局认知：这个方向有哪些综述、奠基性工作",
        "templates": [
            ("survey", "综述总览"),
            ("systematic review", "系统综述"),
            ("literature review", "文献回顾"),
        ],
    },
    {
        "key": "method",
        "label": "核心方法",
        "note": "主流技术路线与关键算法，决定你的方案选型",
        "templates": [
            ("method", "方法总览"),
            ("framework", "技术框架"),
            ("algorithm", "算法路线"),
        ],
    },
    {
        "key": "task",
        "label": "任务与应用",
        "note": "这个方向在解决什么任务、被用在哪些场景",
        "templates": [
            ("application", "应用场景"),
            ("case study", "案例研究"),
            ("in practice", "实践落地"),
        ],
    },
    {
        "key": "data",
        "label": "数据集与评测",
        "note": "可复用的数据集与 benchmark，实验设计的依据",
        "templates": [
            ("dataset", "数据集"),
            ("benchmark", "评测基准"),
            ("evaluation metrics", "评价指标"),
        ],
    },
    {
        "key": "challenge",
        "label": "挑战与开放问题",
        "note": "领域公认的痛点，往往是选题切入点",
        "templates": [
            ("challenges", "主要挑战"),
            ("limitations", "局限性"),
            ("open problems", "开放问题"),
        ],
    },
    {
        "key": "frontier",
        "label": "前沿与最新进展",
        "note": "近两年的新工作，判断方向是否还在升温",
        "templates": [
            ("recent advances", "最新进展"),
            ("state of the art", "前沿综述"),
            ("2025", "年度动态"),
        ],
    },
]

ASPECT_LABELS = {s["key"]: s["label"] for s in ASPECT_SPECS}

# 中文主题（Crossref 也收录大量中文期刊文献）要用中文修饰词构造检索式，
# 否则会拼出「深度学习 survey」这种中英混排，接口几乎全部返回空。
ASPECT_TEMPLATES_CN = {
    "survey": [("综述", "综述总览"), ("系统综述", "系统综述"), ("文献回顾", "文献回顾")],
    "method": [("方法", "方法总览"), ("模型", "技术框架"), ("算法", "算法路线")],
    "task": [("应用", "应用场景"), ("临床", "案例研究"), ("实践", "实践落地")],
    "data": [("数据集", "数据集"), ("基准", "评测基准"), ("指标", "评价指标")],
    "challenge": [("挑战", "主要挑战"), ("局限", "局限性"), ("开放问题", "开放问题")],
    "frontier": [("最新进展", "最新进展"), ("前沿", "前沿综述"), ("2025", "年度动态")],
}

_CJK_RE = re.compile(r"[\u4e00-\u9fa5]")


class RuleExpander:
    """无 LLM 时的规则发散：概念词 × 维度模板"""

    name = "rule"

    def __init__(self, topics_per_aspect: int = 3):
        self.topics_per_aspect = topics_per_aspect

    def expand(
        self,
        topic: str,
        seed_papers: Sequence[Dict[str, Any]],
    ) -> List[AspectPlan]:
        titles = [p.get("title", "") for p in seed_papers]
        texts = [
            f"{p.get('title', '')} {p.get('abstract', '')}" for p in seed_papers
        ]
        base_terms = topic_terms(topic)
        core = " ".join(base_terms[:4]) or topic

        # 概念池按精度从高到低拼装：标题缩写 > 标题术语 > 摘要术语
        acronyms = extract_acronyms(titles, top_k=5)
        lower_excl = {t.lower() for t in base_terms} | {a.lower() for a in acronyms}
        title_terms = extract_title_terms(titles, top_k=8, exclude=lower_excl)
        abstract_terms = extract_terms(
            texts,
            top_k=10,
            exclude=lower_excl | {t.lower() for t in title_terms},
            min_df=3,
        )
        pool = acronyms + title_terms + abstract_terms

        plans: List[AspectPlan] = []
        used: set = set()
        cursor = 0
        use_cn = bool(_CJK_RE.search(topic))

        for spec in ASPECT_SPECS:
            templates = (
                ASPECT_TEMPLATES_CN[spec["key"]] if use_cn else spec["templates"]
            )
            plan = AspectPlan(key=spec["key"], label=spec["label"], note=spec["note"])
            for j in range(self.topics_per_aspect):
                mod_en, label_cn = templates[j % len(templates)]

                # 依次取尚未使用的概念词：保证不同维度的子主题不重复，
                # 否则六个分支会长得一模一样，失去「层级」的意义
                concept = None
                for _ in range(len(pool)):
                    c = pool[cursor % len(pool)]
                    cursor += 1
                    if c.lower() not in used:
                        concept = c
                        break

                if concept is not None:
                    used.add(concept.lower())
                    plan.topics.append(
                        TopicPlan(
                            label=self._humanize(concept),
                            query=f"{concept} {mod_en}",
                        )
                    )
                else:
                    # 概念池不足：用主题核心词补齐。
                    # 相关性有保证，只是发散度较低——这比塞进垃圾术语好。
                    plan.topics.append(
                        TopicPlan(label=label_cn, query=f"{core} {mod_en}")
                    )
            plans.append(plan)
        return plans

    @staticmethod
    def _humanize(term: str) -> str:
        """概念词 -> 可读标签"""
        if term.isupper() or "-" in term:
            return term
        return " ".join(w.capitalize() for w in term.split())


_PROMPT = """你是科研选题助手。研究者想做的方向是：

「{topic}」

以下是这个方向检索到的若干代表性文献（标题 + 摘要片段）：
{snippets}

请把该研究方向拆解为 6 个维度，并为每个维度给出 {n} 个**可执行的中英文检索方向**。
维度固定为：
- survey：综述与奠基
- method：核心方法
- task：任务与应用
- data：数据集与评测
- challenge：挑战与开放问题
- frontier：前沿与最新进展

要求：
1. 每个子主题的 label 用简短中文概括（不超过 14 字）
2. query 用英文检索式，2-6 个词，必须能被 Crossref / arXiv 有效检索
3. 子主题之间不要重复，尽量覆盖不同侧重
4. 只输出 JSON，不要任何解释文字

输出格式：
{{
  "survey": [{{"label": "中文概括", "query": "english query"}}],
  "method": [...],
  "task": [...],
  "data": [...],
  "challenge": [...],
  "frontier": [...]
}}"""


class LLMExpander:
    """有大模型时的发散：让模型结合种子文献给出领域化的子主题"""

    name = "llm"

    def __init__(self, llm_client, topics_per_aspect: int = 3):
        self.llm = llm_client
        self.topics_per_aspect = topics_per_aspect

    def expand(
        self,
        topic: str,
        seed_papers: Sequence[Dict[str, Any]],
    ) -> List[AspectPlan]:
        snippets = "\n".join(
            f"{i}. {p.get('title', '')} | {(p.get('abstract') or '')[:180]}"
            for i, p in enumerate(seed_papers[:6], 1)
        )
        prompt = _PROMPT.format(
            topic=topic, snippets=snippets, n=self.topics_per_aspect
        )

        try:
            raw = self.llm.chat([{"role": "user", "content": prompt}])
            data = _parse_json(raw)
        except Exception:
            data = None

        if not data:
            # 模型输出不可解析时，规则发散兜底，保证流程不中断
            return RuleExpander(self.topics_per_aspect).expand(topic, seed_papers)

        plans: List[AspectPlan] = []
        for spec in ASPECT_SPECS:
            items = data.get(spec["key"]) or []
            plan = AspectPlan(key=spec["key"], label=spec["label"], note=spec["note"])
            for it in items[: self.topics_per_aspect]:
                if isinstance(it, str):
                    plan.topics.append(TopicPlan(label=it, query=it))
                elif isinstance(it, dict) and it.get("query"):
                    plan.topics.append(
                        TopicPlan(
                            label=str(it.get("label") or it["query"])[:30],
                            query=str(it["query"]),
                        )
                    )
            if not plan.topics:
                fallback = RuleExpander(self.topics_per_aspect).expand(
                    topic, seed_papers
                )
                plan.topics = next(
                    (f.topics for f in fallback if f.key == spec["key"]), []
                )
            plans.append(plan)
        return plans


def make_expander(llm_client, topics_per_aspect: int = 3):
    """按可用性选择发散策略"""
    if llm_client is not None:
        return LLMExpander(llm_client, topics_per_aspect)
    return RuleExpander(topics_per_aspect)


def _parse_json(text: str) -> Optional[Dict[str, Any]]:
    """从模型输出中抠出 JSON（容忍 ```json 包裹与前后废话）"""
    if not text:
        return None
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            text = text[start : end + 1]
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None
