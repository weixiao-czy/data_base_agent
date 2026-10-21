"""
术语抽取：从种子文献的标题与摘要中提炼「概念词」

用途：在没有大模型可用时，靠这些概念词与维度模板组合出检索式，
      保证文献地图在纯离线/无 Key 的情况下依然能发散出有意义的层级。
"""

import re
from collections import Counter
from typing import Dict, Iterable, List, Sequence

# 英文停用词（科研语料高频但无区分度）
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "that", "this",
    "these", "those", "of", "in", "on", "at", "to", "for", "with", "by", "from",
    "as", "is", "are", "was", "were", "be", "been", "being", "it", "its", "we",
    "our", "you", "your", "they", "their", "he", "she", "his", "her", "i",
    "can", "could", "may", "might", "will", "would", "shall", "should", "must",
    "do", "does", "did", "have", "has", "had", "not", "no", "nor", "so", "such",
    "there", "here", "which", "who", "whom", "what", "when", "where", "why",
    "how", "all", "any", "both", "each", "few", "more", "most", "other", "some",
    "only", "own", "same", "too", "very", "just", "also", "however", "thus",
    "therefore", "moreover", "furthermore", "while", "although", "because",
    "between", "among", "within", "without", "into", "through", "during",
    "about", "over", "under", "up", "down", "out", "off", "again", "once",
    "paper", "papers", "study", "studies", "result", "results", "approach",
    "method", "methods", "propose", "proposed", "show", "shows", "shown",
    "based", "using", "used", "use", "new", "novel", "existing", "recent",
    "two", "three", "one", "first", "second", "well", "much", "many", "large",
    "high", "low", "different", "significant", "important", "key", "main",
    "work", "works", "research", "article", "review", "analysis", "data",
    "et", "al", "e.g", "i.e", "cf", "vs", "via", "per", "non", "pre",
}

# 中文虚词/泛词（用于切分与过滤）
CN_STOP = {
    "的", "了", "和", "与", "及", "在", "是", "有", "对", "为", "以", "等",
    "研究", "方法", "本文", "我们", "结果", "分析", "基于", "一种", "进行",
    "提出", "通过", "可以", "以及", "这个", "这些", "问题", "应用", "系统",
}

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-]{2,}")
_CN_RE = re.compile(r"[\u4e00-\u9fa5]{2,8}")


def _tokens(text: str) -> List[str]:
    """按句子顺序返回小写英文词串（保留顺序，用于构造 bigram）"""
    return [w.lower() for w in _WORD_RE.findall(text or "")]


# 通用修饰词：语法上像术语，语义上没有领域指向，会把导图带偏
GENERIC_MODIFIERS = {
    "achieve", "achieving", "achieved", "across", "multiple", "higher", "deeper",
    "better", "lower", "larger", "smaller", "various", "several", "different",
    "toward", "towards", "beyond", "generating", "generated", "abstract",
    "overall", "general", "specific", "certain", "potential", "effective",
    "efficient", "robust", "accurate", "complex", "simple", "future", "current",
    "previous", "following", "related", "similar", "additional", "further",
    "wide", "broad", "range", "level", "type", "types", "kind", "aspect",
    "case", "cases", "term", "terms", "number", "amount", "part", "parts",
    # 学术评价类泛词：在几乎任何论文里都高频，完全没有区分度
    "accuracy", "performance", "quality", "evaluation", "optimization",
    "dynamic", "relevance", "academic", "addresses", "advancements",
    "integrating", "improve", "improving", "improved", "enhance", "enhancing",
    "ensure", "ensuring", "provide", "provides", "require", "requires",
    "include", "includes", "consist", "comprises", "enable", "enables",
    "allow", "allows", "support", "supports", "consider", "considering",
    "increase", "increasing", "decrease", "reducing", "reduce",
    "challenge", "challenges", "limitation", "limitations", "problem",
    "problems", "solution", "solutions", "issue", "issues", "benefit",
    "advantage", "advantages", "outcome", "outcomes", "impact", "impacts",
    "context", "contexts", "environment", "environments", "domain", "domains",
    "scenario", "scenarios", "setting", "settings", "condition", "conditions",
    "measure", "measurement", "metric", "metrics", "score", "scores",
    "human", "user", "users", "people", "student", "students", "researcher",
    "researchers", "author", "authors", "text", "texts", "content",
    "task", "tasks", "dataset", "datasets", "benchmark", "benchmarks",
    "model", "models", "system", "systems", "method", "methods",
    "approach", "approaches", "technique", "techniques", "framework",
    "analysis", "analyses", "review", "survey", "overview", "summary",
    "process", "processes", "structure", "structure", "component",
    "stage", "stages", "step", "steps", "goal", "goals", "objective",
    "significant", "substantial", "considerable", "notable", "promising",
    "extensive", "comprehensive", "detailed", "preliminary", "empirical",
    "experimental", "theoretical", "practical", "real", "world", "time",
    "large", "scale", "small", "high", "low", "long", "short", "new",
    "open", "state", "art", "end", "end", "base", "based", "driven",
}


def _ok_word(w: str, min_len: int, excl: set) -> bool:
    """单词是否是候选术语"""
    if len(w) < min_len or w in STOPWORDS or w in GENERIC_MODIFIERS:
        return False
    if w in excl:
        return False
    if w.endswith("ly"):
        return False
    return True


def extract_acronyms(titles: Sequence[str], top_k: int = 6) -> List[str]:
    """从标题中抽取大写缩写（RAG / LLM / BERT 这类）

    缩写是领域内最高精度的术语信号：它几乎不会跨领域通用，
    且出现在标题里通常意味着是该文献的核心对象。
    """
    counter: Counter = Counter()
    for title in titles:
        found = set()
        for raw in re.findall(r"\b[A-Z][A-Za-z]{0,6}(?:-[A-Z][A-Za-z]{0,6})?\b", title or ""):
            # 允许 RAG、LLM、SciMaster、Retrieval-Augmented 这类
            if len(raw) < 3 or raw.lower() in STOPWORDS:
                continue
            if raw.isupper() and 2 <= len(raw) <= 6:
                found.add(raw)
            elif "-" in raw and raw[0].isupper():
                found.add(raw)
        counter.update(found)
    return [w for w, d in counter.most_common(top_k) if d >= 2]


def extract_terms(
    texts: Sequence[str],
    top_k: int = 12,
    min_len: int = 4,
    exclude: Iterable[str] = (),
    min_df: int = 3,
) -> List[str]:
    """从多段文本中抽取概念词

    关键点是按**文档频次**（df）而不是词频排序：一个词只在单篇文献里反复出现，
    说明它是那篇文章的自造词（如某个系统名），不该拿来代表整个领域。
    只有跨多篇文献稳定出现的词，才是真正的领域术语。

    粒度：unigram + bigram。bigram 要求两个词自身也都是高频词，
    这样 "achieve deeper" 这类偶然相邻会被自然过滤掉。

    Args:
        texts: 文本列表（通常是种子文献的 标题+摘要）
        top_k: 返回数量
        min_len: 单词最小长度
        exclude: 需要排除的词（例如主题本身已包含的词）

    Returns:
        按重要性排序的概念词列表
    """
    excl = {e.lower() for e in exclude}
    docs: List[List[str]] = []

    for text in texts:
        words = [w.lower() for w in _WORD_RE.findall(text or "")]
        docs.append(words)

    df_uni: Counter = Counter()
    df_bi: Counter = Counter()

    for words in docs:
        seen_u, seen_b = set(), set()
        for w in words:
            if _ok_word(w, min_len, excl):
                seen_u.add(w)
        for a, b in zip(words, words[1:]):
            if _ok_word(a, min_len + 1, excl) and _ok_word(b, min_len, excl):
                seen_b.add(f"{a} {b}")
        df_uni.update(seen_u)
        df_bi.update(seen_b)

    seen_uni = {t for t, d in df_uni.items() if d >= min_df}
    strong_uni = {t for t, d in df_uni.items() if d >= min_df + 1}
    strong_bi = {
        t for t, d in df_bi.items()
        if d >= min_df - 1 and all(w in seen_uni for w in t.split())
    }

    # 不做逐级放宽：低门槛放进来的多是 "utilised retrieve" 这类语法碎片，
    # 宁可少给几个概念词、由上层用主题兜底，也不制造无效节点。
    scored: Dict[str, float] = {}
    for t in strong_bi:
        scored[t] = df_bi[t] * 2.4
    for t in strong_uni:
        scored[t] = df_uni[t] * 1.0

    # 去掉被更长 bigram 完全包含的低分 unigram
    bigram_words = {w for t in scored if " " in t for w in t.split()}
    out = [
        (t, s) for t, s in scored.items()
        if " " in t or t not in bigram_words or len(scored) < top_k
    ]
    out.sort(key=lambda x: (-x[1], x[0]))
    return [t for t, _ in out[:top_k]]


def extract_cn_terms(texts: Sequence[str], top_k: int = 8) -> List[str]:
    """从中文文本中抽取中文短语（简单词频，不依赖分词库）"""
    counter: Counter = Counter()
    for text in texts:
        for phrase in _CN_RE.findall(text or ""):
            if phrase in CN_STOP or len(phrase) < 2:
                continue
            counter[phrase] += 1
    return [w for w, c in counter.most_common(top_k) if c >= 1]


def extract_title_terms(
    titles: Sequence[str],
    top_k: int = 8,
    exclude: Iterable[str] = (),
) -> List[str]:
    """从标题中抽取术语

    标题是作者精心写过的名词短语集合，比摘要干净得多：
    摘要里大量 "we propose ... which can ..." 的语法碎片在这里不存在，
    所以同样的 n-gram 方法在标题上精度高得多。
    """
    excl = {e.lower() for e in exclude}
    df_bi: Counter = Counter()
    df_uni: Counter = Counter()

    for title in titles:
        words = [w.lower() for w in _WORD_RE.findall(title or "")]
        uni = {w for w in words if _ok_word(w, 4, excl)}
        bi = {
            f"{a} {b}" for a, b in zip(words, words[1:])
            if _ok_word(a, 5, excl) and _ok_word(b, 4, excl)
        }
        df_uni.update(uni)
        df_bi.update(bi)

    good_uni = {t for t, d in df_uni.items() if d >= 2}
    scored: Dict[str, float] = {
        t: d * 2.6 for t, d in df_bi.items()
        if d >= 2 and all(w in good_uni for w in t.split())
    }
    for t, d in df_uni.items():
        if d >= 2 and len(t) >= 7:
            scored.setdefault(t, d * 1.0)

    out = sorted(scored.items(), key=lambda x: (-x[1], x[0]))
    return [t for t, _ in out[:top_k]]


# 中文主题的口语外壳：用户常写「我想研究 X 的应用」，这些词进了检索式只会
# 稀释关键词，Crossref / arXiv 对整句的匹配是模糊的，必须剥掉。
_CJK_LEAD_RE = re.compile(
    r"^(?:我(?:们)?(?:想|打算|计划|准备|希望|要|正在)?(?:研究|做|了解|关注|探索|分析|学习)|"
    r"帮(?:我|忙)?(?:研究|找|查|看看)|关于|有关|请问|如何|怎么)"
)
_CJK_TAIL_RE = re.compile(
    r"(?:的)?(?:相关)?(?:研究|应用|工作|文献|方向|课题|领域|进展|问题|方法)+$"
)
_CJK_SPLIT_RE = re.compile(r"[在的中与和及或、，,；;：:（）()\s]+")
# 口语动词后常见的虚词尾巴：「了解一下」「看看这方面的…」
_CJK_LEAD_FILLER_RE = re.compile(r"^(?:一下|一点|一些|下|一点点的?)")


def _cjk_topic_terms(topic: str) -> List[str]:
    """中文主题 -> 若干检索片段

    「我想研究深度学习在医学影像诊断中的应用」应拆成
    ["深度学习", "医学影像诊断"]，而不是整句丢给检索接口。
    不做真正的分词（无词典依赖），只剥口语外壳 + 按连接词切分，
    切出来的片段仍是完整名词短语，检索效果足够。
    """
    text = topic.strip()
    text = _CJK_LEAD_RE.sub("", text).strip()
    # 外壳可能叠两层，例如「我想了解一下…」
    text = _CJK_LEAD_RE.sub("", text).strip()
    text = _CJK_LEAD_FILLER_RE.sub("", text).strip()
    stripped = _CJK_TAIL_RE.sub("", text).strip()
    # 只剥到还剩内容为止，避免把「医学影像」这类本身就是名词的主题剥空
    if len(stripped) >= 4:
        text = stripped

    parts = [p.strip() for p in _CJK_SPLIT_RE.split(text) if p.strip()]
    parts = [p for p in parts if len(p) >= 2 and p not in _CJK_FILLER]
    if not parts:
        return [text] if text else []
    return parts


# 切分后没有领域指向的碎片
_CJK_FILLER = {
    "最新", "一些", "相关", "这个", "那个", "内容", "东西", "方面",
    "情况", "部分", "基础", "初步", "简单",
}


def topic_terms(topic: str) -> List[str]:
    """把用户输入的主题拆成词，用于构造检索式"""
    terms = _tokens(topic)
    terms = [t for t in terms if t not in STOPWORDS and len(t) >= 2]
    if terms:
        return terms
    # 中文主题：剥掉口语外壳后按连接词切分
    return _cjk_topic_terms(topic)
