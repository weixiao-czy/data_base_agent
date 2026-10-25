"""验证 GUI 聊天的 markdown 渲染与宽度调整（离屏运行，无需显示器）。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from gui.chat_widget import _md, _CONTENT_MAX_WIDTH, MessageRow
from gui.styles import COLORS

sample = (
    "# 研究方向\n\n"
    "**大模型语义检索**，重点看 `稠密检索` 与 `重排序`。\n\n"
    "- 评估指标：nDCG@10\n"
    "- 数据集：MS MARCO\n\n"
    "| 方法 | nDCG |\n"
    "|---|---|\n"
    "| BM25 | 0.42 |\n\n"
    "> 引用一句话\n\n"
    "```python\nprint('hello')\n```\n\n"
    "详见 https://arxiv.org/abs/2401.00000"
)

out = _md(sample)
print("=== 渲染结果（截断） ===")
print(out[:600])
print("...")

checks = {
    "<h1 style=": "标题带内联样式",
    "<strong>": "加粗生效",
    "<code style=": "行内代码带样式",
    "<table": "表格转换",
    "<th style=": "表头样式",
    "<li style=": "列表样式",
    "<blockquote style=": "引用块样式",
    "<pre style=": "代码块样式",
    f'<a style="color:{COLORS["accent"]}': "链接用强调色",
}
print("\n=== 检查 ===")
fail = 0
for k, desc in checks.items():
    ok = k in out
    print(f"  {'✓' if ok else '✗'} {desc}")
    fail += (not ok)

assert "**大模型语义检索**" not in out, "markdown 记号不应原样残留"
print("  ✓ 无残留 markdown 记号")

assert _CONTENT_MAX_WIDTH > 900, f"内容列上限应加宽，当前 {_CONTENT_MAX_WIDTH}"
print(f"  ✓ 内容列上限已放宽到 {_CONTENT_MAX_WIDTH}px")

from PyQt6.QtWidgets import QApplication
app = QApplication([])
row = MessageRow(sample, is_user=False)
row.resize(900, 200)
print("  ✓ MessageRow 可正常构建")
print("\n全部通过" if fail == 0 else f"\n{fail} 项失败")
sys.exit(1 if fail else 0)
