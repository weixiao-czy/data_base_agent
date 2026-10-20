"""
文献地图命令行入口

用法（在本项目根目录下执行）：

    # 基本用法：生成交互式思维导图 + Markdown 大纲 + JSON
    python src/litmap_cli.py "large language models for literature retrieval"

    # 控制规模与耗时
    python src/litmap_cli.py "retrieval augmented generation" \
        --seed-limit 8 --per-topic 3 --topics-per-aspect 3 --max-queries 18

    # 强制走规则发散（不调用大模型）
    python src/litmap_cli.py "graph neural networks" --no-llm

    # 指定输出目录
    python src/litmap_cli.py "..." -o output/maps

产物：
    <slug>.html  自包含交互式思维导图（双击即可离线打开）
    <slug>.md     层级大纲，可直接贴进笔记
    <slug>.json   结构化数据，便于二次开发或接入 GUI
"""

import argparse
import os
import re
import sys
from typing import Optional

# 允许 `python src/litmap/cli.py` 直接运行（把 src 加入模块搜索路径）
_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from litmap.builder import LiteratureMapBuilder, summarize  # noqa: E402
from litmap.render import to_html, to_json, to_markdown      # noqa: E402
from search.real_search import RealSearchProvider            # noqa: E402


def _slugify(text: str) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fa5]+", "_", (text or "").strip().lower())
    return s.strip("_")[:48] or "literature_map"


def _header(msg: str) -> None:
    print(msg, flush=True)


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="litmap",
        description="把研究主题发散成层级化的文献地图（思维导图）",
    )
    parser.add_argument("topic", help="研究主题，例如 \"retrieval augmented generation\"")
    parser.add_argument("-o", "--outdir", default="output/maps", help="输出目录")
    parser.add_argument("--seed-limit", type=int, default=8, help="种子文献数量")
    parser.add_argument("--per-topic", type=int, default=3, help="每个检索方向取几篇")
    parser.add_argument("--topics-per-aspect", type=int, default=3,
                        help="每个维度生成几个检索方向")
    parser.add_argument("--max-queries", type=int, default=18, help="检索请求上限")
    parser.add_argument("--no-llm", action="store_true", help="不调用大模型，走规则发散")
    parser.add_argument("--no-open", action="store_true", help="生成后不自动打开导图")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="显示发散策略的来源说明")
    args = parser.parse_args(argv)

    # Windows 控制台中文输出保护
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    topic = args.topic.strip()
    if not topic:
        print("请提供研究主题")
        return 2

    # ---- 检索提供者 ----
    provider = RealSearchProvider()
    if not provider.is_available():
        print("检索服务不可用，请检查网络")
        return 3

    # ---- LLM（可选）----
    llm = None
    if not args.no_llm:
        try:
            from llm.client import OpenAIClient
            llm = OpenAIClient()
            _header(f"使用大模型发散：{llm.model}")
        except Exception as e:
            _header(f"未启用大模型（{type(e).__name__}: {e}）→ 改用规则模板发散")

    _header("=" * 62)
    _header(f"文献地图构建：{topic}")
    _header("=" * 62)

    if args.verbose and not llm:
        _header("提示：当前未启用大模型，子主题由「术语统计 + 维度模板」生成。")
        _header("      配置有效的 OPENAI_API_KEY 后，子主题会由模型结合种子文献发散，质量更高。")
        _header("")

    builder = LiteratureMapBuilder(
        provider=provider,
        llm_client=llm,
        seed_limit=args.seed_limit,
        per_topic=args.per_topic,
        topics_per_aspect=args.topics_per_aspect,
        max_queries=args.max_queries,
        progress=_header,
    )
    litmap = builder.build(topic)

    # ---- 输出 ----
    os.makedirs(args.outdir, exist_ok=True)
    slug = _slugify(topic)
    paths = {
        "html": os.path.join(args.outdir, f"{slug}.html"),
        "md": os.path.join(args.outdir, f"{slug}.md"),
        "json": os.path.join(args.outdir, f"{slug}.json"),
    }
    with open(paths["html"], "w", encoding="utf-8") as f:
        f.write(to_html(litmap))
    with open(paths["md"], "w", encoding="utf-8") as f:
        f.write(to_markdown(litmap))
    with open(paths["json"], "w", encoding="utf-8") as f:
        f.write(to_json(litmap))

    _header("")
    _header(summarize(litmap))
    _header("")
    _header("-" * 62)
    for name, p in paths.items():
        _header(f"{name:5s} → {os.path.abspath(p)}")

    if litmap.meta.get("errors"):
        _header("")
        _header(f"检索告警 {len(litmap.meta['errors'])} 条（前 3 条）：")
        for e in litmap.meta["errors"][:3]:
            _header(f"  · {e}")

    if not args.no_open:
        try:
            import webbrowser
            webbrowser.open("file://" + os.path.abspath(paths["html"]))
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
