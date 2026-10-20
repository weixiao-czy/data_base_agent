"""
聊天显示组件 — 消息流、欢迎页、思考动画、结构化卡片
"""

import html
import re

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame,
    QLabel, QPushButton,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor

from .styles import COLORS, FONT_MONO

_URL_RE = re.compile(r"(https?://[^\s<>\"']+)")
# 已有 markdown 链接括号里的 URL 不再重复包一层：[text](https://a) 里的 url
_URL_MD_RE = re.compile(r"(?<!\]\()(https?://[^\s<>()\[\]]+)")
_CONTENT_MAX_WIDTH = 980

# ---------------------------------------------------------------- markdown 渲染
# Agent 的回复是 markdown（**加粗**、列表、代码块、表格等），QLabel 直接显示
# 会把这些记号原样打出来。用 markdown-it 转成 QLabel 支持的 HTML 子集；
# Qt 富文本不认外部样式表，样式必须内联在标签上。

try:
    from markdown_it import MarkdownIt
    _MD = MarkdownIt("commonmark", {"breaks": True, "html": False}).enable("table")
except ImportError:  # 兜底：库缺失时退回纯文本转义，功能不崩
    _MD = None


def _md(text: str) -> str:
    """markdown → Qt 富文本可用的 HTML；库缺失时退回 _rich"""
    if _MD is None:
        return _rich(text)

    # 裸 URL 先转成 markdown 链接，交给 markdown-it 统一处理
    text = _URL_MD_RE.sub(r"[\1](\1)", text)
    out = _MD.render(text)

    mono = f"font-family:{FONT_MONO};"
    accent = COLORS["accent"]
    code_bg = COLORS["bg_subtle"]
    border = COLORS["border_light"]
    secondary = COLORS["text_secondary"]
    repl = [
        ("<a href=", f'<a style="color:{accent};text-decoration:none;" href='),
        ("<h1>", '<h1 style="font-size:16.5px;font-weight:600;margin:10px 0 4px 0;">'),
        ("<h2>", '<h2 style="font-size:15.5px;font-weight:600;margin:9px 0 4px 0;">'),
        ("<h3>", '<h3 style="font-size:14.5px;font-weight:600;margin:8px 0 3px 0;">'),
        ("<h4>", '<h4 style="font-size:13.5px;font-weight:600;margin:8px 0 3px 0;">'),
        ("<p>", '<p style="margin:5px 0;">'),
        ("<ul>", '<ul style="margin:5px 0 5px 20px;">'),
        ("<ol>", '<ol style="margin:5px 0 5px 20px;">'),
        ("<li>", '<li style="margin:2px 0;">'),
        ("<blockquote>",
         f'<blockquote style="color:{secondary};margin:6px 0;padding-left:10px;'
         f'border-left:3px solid {border};">'),
        ("<code>", f'<code style="{mono}background-color:{code_bg};">'),
        ("<pre>", f'<pre style="{mono}background-color:{code_bg};padding:8px;">'),
        ("<table",
         f'<table cellspacing="0" cellpadding="5" style="border-collapse:collapse;'
         f'font-size:12.5px;margin:6px 0;">'),
        ("<th>", f'<th style="background-color:{code_bg};text-align:left;">'),
        ("<td>", f'<td style="border-top:1px solid {border};">'),
        ("<hr>", f'<hr style="border:none;border-top:1px solid {border};">'),
    ]
    for old, new in repl:
        out = out.replace(old, new)
    return out


def _rich(text: str) -> str:
    """纯文本转 HTML：转义 + 自动识别链接"""
    esc = html.escape(text)
    return _URL_RE.sub(
        lambda m: f'<a href="{m.group(1)}" style="color:{COLORS["accent"]};text-decoration:none;">{m.group(1)}</a>',
        esc,
    )


def _make_label(object_name: str, text: str, rich: bool = False) -> QLabel:
    label = QLabel(text)
    label.setObjectName(object_name)
    label.setWordWrap(True)
    label.setTextInteractionFlags(
        Qt.TextInteractionFlag.TextSelectableByMouse
        | Qt.TextInteractionFlag.LinksAccessibleByMouse
    )
    label.setOpenExternalLinks(True)
    if rich:
        label.setTextFormat(Qt.TextFormat.RichText)
    return label


class Avatar(QLabel):
    """圆形头像"""

    def __init__(self, char: str, object_name: str, size: int = 30, parent=None):
        super().__init__(char, parent)
        self.setObjectName(object_name)
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class _CenteredColumn(QWidget):
    """居中限宽列容器"""

    def __init__(self, parent=None):
        super().__init__(parent)
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addStretch(1)
        self.column = QWidget()
        self.column.setMaximumWidth(_CONTENT_MAX_WIDTH)
        self.column_layout = QVBoxLayout(self.column)
        self.column_layout.setContentsMargins(0, 0, 0, 0)
        self.column_layout.setSpacing(0)
        outer.addWidget(self.column)
        outer.addStretch(1)


class MessageRow(_CenteredColumn):
    """一条消息：Agent 为头像+文本，用户为右侧气泡"""

    def __init__(self, text: str, is_user: bool, parent=None):
        super().__init__(parent)
        if is_user:
            row = QHBoxLayout()
            row.setContentsMargins(0, 3, 0, 3)
            row.addStretch(1)
            bubble = QFrame()
            bubble.setObjectName("user_bubble")
            bubble.setMaximumWidth(620)
            bl = QVBoxLayout(bubble)
            bl.setContentsMargins(14, 10, 14, 10)
            bl.addWidget(_make_label("user_bubble_text", _rich(text), rich=True))
            row.addWidget(bubble)
            self.column_layout.addLayout(row)
        else:
            row = QHBoxLayout()
            row.setContentsMargins(0, 6, 0, 6)
            row.setSpacing(12)
            row.addWidget(Avatar("文", "avatar_agent"), alignment=Qt.AlignmentFlag.AlignTop)
            row.addWidget(
                _make_label("agent_text", _md(text), rich=True),
                1,
                alignment=Qt.AlignmentFlag.AlignTop,
            )
            self.column_layout.addLayout(row)


class DotGrid(QWidget):
    """2×3 点阵加载动画"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 14)
        self._phase = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(280)

    def _tick(self):
        self._phase = (self._phase + 1) % 6
        self.update()

    def stop(self):
        self._timer.stop()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(Qt.PenStyle.NoPen)
        base = QColor(COLORS["text_tertiary"])
        i = 0
        for r in range(2):
            for c in range(3):
                d = (self._phase - i) % 6
                alpha = 235 if d == 0 else (140 if d == 1 else 70)
                color = QColor(base)
                color.setAlpha(alpha)
                p.setBrush(color)
                p.drawEllipse(2 + c * 7, 2 + r * 7, 4, 4)
                i += 1


class ThinkingIndicator(_CenteredColumn):
    """Agent 正在处理时的等待提示"""

    DEFAULT_TEXT = "Waiting for reply…"

    def __init__(self, parent=None):
        super().__init__(parent)
        row = QHBoxLayout()
        row.setContentsMargins(0, 8, 0, 8)
        row.setSpacing(10)
        self.dots = DotGrid()
        row.addWidget(self.dots, alignment=Qt.AlignmentFlag.AlignTop)
        self.label = QLabel(self.DEFAULT_TEXT)
        self.label.setObjectName("thinking_label")
        row.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignTop)
        row.addStretch(1)
        self.column_layout.addLayout(row)

    def set_status(self, text: str):
        self.label.setText(text or self.DEFAULT_TEXT)

    def stop(self):
        self.dots.stop()


class PlanCardWidget(_CenteredColumn):
    """需求翻译卡 — 结构化卡片"""

    def __init__(self, card: dict, parent=None):
        super().__init__(parent)
        outer_row = QHBoxLayout()
        outer_row.setContentsMargins(0, 8, 0, 8)
        outer_row.addSpacing(42)  # 与 Agent 文本对齐（头像 30 + 间距 12）

        frame = QFrame()
        frame.setObjectName("plan_card_widget")
        vbox = QVBoxLayout(frame)
        vbox.setContentsMargins(0, 0, 0, 16)
        vbox.setSpacing(0)

        # 头部
        header = QFrame()
        header.setObjectName("plan_card_header")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(18, 12, 18, 12)
        title = QLabel("需求翻译卡")
        title.setObjectName("plan_card_title")
        hl.addWidget(title)
        hl.addStretch(1)
        badge = QLabel("PLAN CARD")
        badge.setObjectName("plan_card_badge")
        hl.addWidget(badge)
        vbox.addWidget(header)

        body = QVBoxLayout()
        body.setContentsMargins(18, 14, 18, 0)
        body.setSpacing(12)

        self._add_section(body, "研究兴趣", card.get("research_interest", ""))
        self._add_section(body, "解读问题", card.get("interpreted_question", ""))
        intent = card.get("research_intent_type", "")
        if intent:
            self._add_section(body, "研究类型", intent)
        self._add_list(body, "关键维度", card.get("key_dimensions", []))

        kw = card.get("suggested_keywords", {}) or {}
        kw_lines = []
        if kw.get("primary"):
            kw_lines.append("主要：" + "、".join(kw["primary"]))
        if kw.get("variants"):
            kw_lines.append("变体：" + "、".join(kw["variants"]))
        if kw.get("adjacent_fields"):
            kw_lines.append("相邻领域：" + "、".join(kw["adjacent_fields"]))
        if kw_lines:
            self._add_section(body, "建议关键词", "\n".join(kw_lines))

        self._add_list(body, "不确定性", card.get("uncertainties", []))

        sp = card.get("search_plan", {}) or {}
        queries = sp.get("suggested_queries", [])
        if queries:
            mode = sp.get("mode", "")
            text = "\n".join(f"{i}. {q}" for i, q in enumerate(queries, 1))
            if mode:
                text = f"检索模式：{mode}\n{text}"
            self._add_section(body, "检索计划", text)

        self._add_list(body, "下一步行动", card.get("next_actions", []))

        vbox.addLayout(body)
        outer_row.addWidget(frame, 1)
        self.column_layout.addLayout(outer_row)

    def _add_section(self, layout, label: str, value: str):
        if not value:
            return
        layout.addWidget(_make_label("plan_section_label", label))
        layout.addWidget(_make_label("plan_section_value", value))

    def _add_list(self, layout, label: str, items: list):
        if not items:
            return
        text = "\n".join(f"•  {item}" for item in items)
        self._add_section(layout, label, text)


class PaperCard(QFrame):
    """单篇文献卡片"""

    def __init__(self, paper: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("paper_card")
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(18, 14, 18, 14)
        vbox.setSpacing(6)

        # 标题
        title = paper.get("title", "无标题")
        url = paper.get("url", "")
        title_label = QLabel()
        title_label.setObjectName("paper_title")
        title_label.setWordWrap(True)
        title_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        title_label.setOpenExternalLinks(True)
        if url:
            title_label.setText(
                f'<a href="{html.escape(url)}" style="color:{COLORS["text_primary"]};text-decoration:none;">{html.escape(title)}</a>'
            )
        else:
            title_label.setText(title)
        vbox.addWidget(title_label)

        # 作者 · 年份 · 期刊
        meta_parts = []
        authors = paper.get("authors", [])
        if authors:
            shown = authors[:4]
            meta = "、".join(shown)
            if len(authors) > 4:
                meta += f" 等 {len(authors)} 人"
            meta_parts.append(meta)
        if paper.get("year"):
            meta_parts.append(str(paper["year"]))
        if paper.get("venue"):
            meta_parts.append(paper["venue"])
        if meta_parts:
            vbox.addWidget(_make_label("paper_meta", "  ·  ".join(meta_parts)))

        # 摘要（截断）
        abstract = (paper.get("abstract") or "").strip()
        if abstract:
            if len(abstract) > 260:
                abstract = abstract[:260].rstrip() + "…"
            vbox.addWidget(_make_label("paper_abstract", abstract))

        # 底部：来源徽章 + DOI/链接
        footer = QHBoxLayout()
        footer.setSpacing(8)
        source = paper.get("source", "")
        if source:
            badge = QLabel(source)
            badge.setObjectName("paper_badge")
            footer.addWidget(badge)
        doi = paper.get("doi", "")
        if doi:
            footer.addWidget(
                _make_label("paper_link", f'<a href="https://doi.org/{html.escape(doi)}" style="color:{COLORS["text_tertiary"]};">DOI: {html.escape(doi)}</a>', rich=True)
            )
        footer.addStretch(1)
        vbox.addLayout(footer)


class SearchResultsBlock(_CenteredColumn):
    """检索结果整体块：计数 + 卡片列表"""

    def __init__(self, results: list, parent=None):
        super().__init__(parent)
        head = QHBoxLayout()
        head.setContentsMargins(42, 10, 0, 2)
        count = QLabel(f"检索到 {len(results)} 篇文献")
        count.setObjectName("results_count_label")
        head.addWidget(count)
        head.addStretch(1)
        self.column_layout.addLayout(head)

        for paper in results:
            row = QHBoxLayout()
            row.setContentsMargins(0, 4, 0, 4)
            row.addSpacing(42)
            card = PaperCard(paper)
            row.addWidget(card, 1)
            self.column_layout.addLayout(row)


class WelcomeView(_CenteredColumn):
    """空对话欢迎页"""

    suggestion_clicked = pyqtSignal(str)

    SUGGESTIONS = [
        "我想研究深度学习在医学影像诊断中的应用",
        "帮我检索大语言模型对齐（alignment）方向的综述",
        "对量子计算纠错感兴趣，如何系统地检索文献？",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 48, 0, 0)
        vbox.setSpacing(0)

        logo_row = QHBoxLayout()
        logo = QLabel("文")
        logo.setObjectName("welcome_logo")
        logo.setFixedSize(52, 52)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_row.addWidget(logo)
        vbox.addLayout(logo_row)

        vbox.addSpacing(16)
        title = QLabel("把模糊的想法，翻译成精准的检索")
        title.setObjectName("welcome_title")
        vbox.addWidget(title)
        vbox.addSpacing(6)
        sub = QLabel("描述你的研究兴趣，我会通过最多 10 轮澄清帮你生成需求翻译卡，并自动检索相关文献。")
        sub.setObjectName("welcome_sub")
        sub.setWordWrap(True)
        vbox.addWidget(sub)

        vbox.addSpacing(22)
        for text in self.SUGGESTIONS:
            chip = QPushButton(text)
            chip.setObjectName("suggestion_chip")
            chip.setCursor(Qt.CursorShape.PointingHandCursor)
            chip.clicked.connect(lambda _=False, t=text: self.suggestion_clicked.emit(t))
            vbox.addWidget(chip)
            vbox.addSpacing(8)

        vbox.addStretch(1)
        self.column_layout.addLayout(vbox)


class ChatDisplay(QWidget):
    """聊天显示区域"""

    suggestion_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chat_area")
        self._thinking = None
        self._welcome = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.messages_container = QWidget()
        self.messages_container.setObjectName("messages_container")
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(14, 14, 14, 16)
        self.messages_layout.setSpacing(6)
        self.messages_layout.addStretch(1)

        self.scroll_area.setWidget(self.messages_container)
        layout.addWidget(self.scroll_area)

    # ------------------------------------------------ 消息

    def add_message(self, text: str, is_user: bool = False):
        at_bottom = self._near_bottom()
        self._insert_widget(MessageRow(text, is_user))
        if at_bottom or is_user:
            self._scroll_to_bottom()

    def add_plan_card(self, card_dict: dict):
        at_bottom = self._near_bottom()
        self._insert_widget(PlanCardWidget(card_dict))
        if at_bottom:
            self._scroll_to_bottom()

    def add_search_cards(self, results: list):
        at_bottom = self._near_bottom()
        self._insert_widget(SearchResultsBlock(results))
        if at_bottom:
            self._scroll_to_bottom()

    def show_welcome(self):
        if self._welcome is not None:
            return
        self._welcome = WelcomeView()
        self._welcome.suggestion_clicked.connect(self.suggestion_clicked)
        self._insert_widget(self._welcome)
        QTimer.singleShot(0, lambda: self.scroll_area.verticalScrollBar().setValue(0))

    def hide_welcome(self):
        if self._welcome is not None:
            self._welcome.deleteLater()
            self._welcome = None

    # ------------------------------------------------ 思考动画

    def show_thinking(self, status: str = "正在思考"):
        if self._thinking is None:
            self._thinking = ThinkingIndicator()
            self._insert_widget(self._thinking)
        self._thinking.set_status(status)
        self._scroll_to_bottom()

    def set_thinking_status(self, status: str):
        if self._thinking is not None:
            self._thinking.set_status(status)

    def hide_thinking(self):
        if self._thinking is not None:
            self._thinking.stop()
            self._thinking.deleteLater()
            self._thinking = None

    # ------------------------------------------------ 其他

    def clear(self):
        self.hide_thinking()
        self.hide_welcome()
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _insert_widget(self, widget: QWidget):
        count = self.messages_layout.count()
        self.messages_layout.insertWidget(count - 1, widget)

    def _near_bottom(self) -> bool:
        sb = self.scroll_area.verticalScrollBar()
        return sb.value() >= sb.maximum() - 140

    def _scroll_to_bottom(self):
        QTimer.singleShot(0, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))
