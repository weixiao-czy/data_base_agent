"""
主窗口 — 商业级桌面应用风格
无边框窗口 + 自定义标题栏 + 侧边栏 + 聊天工作区
"""

import os
import json
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QTextEdit, QFrame, QFileDialog, QMessageBox,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QEvent, QSize
from PyQt6.QtGui import QColor

from .styles import (
    COLORS, GLOBAL_QSS, TITLEBAR_QSS, SIDEBAR_QSS, CHAT_QSS, MESSAGE_QSS,
)
from .chat_widget import ChatDisplay
from .agent_worker import AgentWorker
from .settings_dialog import SettingsDialog, load_config

_HISTORY_DIR = os.path.join(os.path.expanduser("~"), ".databaseagent", "conversations")


class TitleBar(QFrame):
    """自定义标题栏：logo + 标题 + 窗口控制"""

    def __init__(self, window: QMainWindow):
        super().__init__(window)
        self.setObjectName("titlebar")
        self.setFixedHeight(44)
        self._window = window
        self._drag_pos = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 10, 0)
        layout.setSpacing(10)

        logo = QLabel("文")
        logo.setObjectName("titlebar_logo")
        logo.setFixedSize(20, 20)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("文献检索需求翻译 Agent")
        title.setObjectName("titlebar_title")
        layout.addWidget(title)

        layout.addStretch(1)

        self.min_btn = self._make_win_btn("─", "win_btn", self._window.showMinimized)
        self.max_btn = self._make_win_btn("□", "win_btn", self._toggle_maximize)
        self.close_btn = self._make_win_btn("✕", "win_close", self._window.close)
        for btn in (self.min_btn, self.max_btn, self.close_btn):
            layout.addWidget(btn)

    def _make_win_btn(self, text: str, name: str, slot):
        btn = QPushButton(text)
        btn.setObjectName(name)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn.clicked.connect(slot)
        return btn

    def _toggle_maximize(self):
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximize()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            if self._window.isMaximized():
                return
            delta = event.globalPosition().toPoint() - self._drag_pos
            self._window.move(self._window.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()


class ConversationRow(QWidget):
    """对话历史单行：标题 + 悬停删除按钮"""

    def __init__(self, conv_id: str, title: str, on_delete, parent=None):
        super().__init__(parent)
        self.conv_id = conv_id
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 6, 0)
        layout.setSpacing(2)

        self.label = QLabel(title)
        self.label.setObjectName("conv_row_label")
        self.label.setToolTip(title)
        layout.addWidget(self.label, 1)

        self.del_btn = QPushButton("✕")
        self.del_btn.setObjectName("conv_del_btn")
        self.del_btn.setFixedSize(22, 22)
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.del_btn.setToolTip("删除对话")
        self.del_btn.hide()
        self.del_btn.clicked.connect(lambda: on_delete(conv_id))
        layout.addWidget(self.del_btn)

    def enterEvent(self, event):
        self.del_btn.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.del_btn.hide()
        super().leaveEvent(event)

    def set_selected(self, selected: bool):
        self.label.setProperty("selected", "true" if selected else "false")
        self.label.style().unpolish(self.label)
        self.label.style().polish(self.label)


class Sidebar(QWidget):
    """侧边栏：新建对话 + 对话历史 + 设置"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(250)

        self.new_chat_clicked = None
        self.conversation_selected = None
        self.settings_clicked = None
        self.delete_requested = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 10)
        layout.setSpacing(0)

        new_btn = QPushButton("＋  新建对话")
        new_btn.setObjectName("new_chat_btn")
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.clicked.connect(self._on_new_chat)
        layout.addWidget(new_btn)

        layout.addSpacing(18)

        section = QLabel("对话历史")
        section.setObjectName("section_title")
        layout.addWidget(section)
        layout.addSpacing(6)

        self.conv_list = QListWidget()
        self.conv_list.setObjectName("conv_list")
        self.conv_list.setFrameShape(QFrame.Shape.NoFrame)
        self.conv_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.conv_list.currentRowChanged.connect(self._on_conv_selected)
        layout.addWidget(self.conv_list, 1)

        footer = QFrame()
        footer.setObjectName("sidebar_footer")
        fl = QVBoxLayout(footer)
        fl.setContentsMargins(0, 8, 0, 0)

        settings_btn = QPushButton("设置")
        settings_btn.setObjectName("footer_btn")
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(self._on_settings)
        fl.addWidget(settings_btn)

        layout.addWidget(footer)

    def _on_new_chat(self):
        if self.new_chat_clicked:
            self.new_chat_clicked()

    def _on_conv_selected(self, row):
        self._refresh_selection()
        if row >= 0 and self.conversation_selected:
            item = self.conv_list.item(row)
            conv_id = item.data(Qt.ItemDataRole.UserRole)
            if conv_id:
                self.conversation_selected(conv_id)

    def _on_settings(self):
        if self.settings_clicked:
            self.settings_clicked()

    def _refresh_selection(self):
        for i in range(self.conv_list.count()):
            item = self.conv_list.item(i)
            row = self.conv_list.itemWidget(item)
            if isinstance(row, ConversationRow):
                row.set_selected(item.isSelected())

    def update_conversations(self, conversations: dict, current_id: str):
        self.conv_list.blockSignals(True)
        self.conv_list.clear()
        for conv_id, conv in sorted(
            conversations.items(),
            key=lambda x: x[1].get("timestamp", ""),
            reverse=True,
        ):
            title = conv.get("title", "新对话")
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 34))
            item.setData(Qt.ItemDataRole.UserRole, conv_id)
            self.conv_list.addItem(item)
            self.conv_list.setItemWidget(
                item, ConversationRow(conv_id, title, self._on_delete)
            )
            if conv_id == current_id:
                self.conv_list.setCurrentItem(item)
        self._refresh_selection()
        self.conv_list.blockSignals(False)

    def _on_delete(self, conv_id: str):
        if self.delete_requested:
            self.delete_requested(conv_id)


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setWindowTitle("文献检索需求翻译 Agent")
        self.setMinimumSize(1024, 680)
        self.resize(1240, 820)

        self.setStyleSheet(
            GLOBAL_QSS + TITLEBAR_QSS + SIDEBAR_QSS + CHAT_QSS + MESSAGE_QSS
        )

        self._config = load_config()
        self._conversations = {}
        self._current_conv_id = None
        self._busy = False
        self._worker = None

        self._setup_ui()
        self._load_conversations()
        self._ensure_worker()
        self._new_conversation()
        self.header_status.setText(self._idle_status())

    # ------------------------------------------------ UI 构建

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(TitleBar(self))

        content = QWidget()
        cl = QHBoxLayout(content)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.new_chat_clicked = self._new_conversation
        self.sidebar.conversation_selected = self._switch_conversation
        self.sidebar.settings_clicked = self._open_settings
        self.sidebar.delete_requested = self._delete_conversation
        cl.addWidget(self.sidebar)

        cl.addWidget(self._build_chat_panel(), 1)
        root.addWidget(content, 1)

    def _build_chat_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("chat_panel")
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.setSpacing(0)

        # 头部：对话标题 + 状态 + 导出
        header = QFrame()
        header.setObjectName("chat_header")
        header.setFixedHeight(50)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(24, 0, 16, 0)
        hl.setSpacing(8)

        self.header_title = QLabel("新对话")
        self.header_title.setObjectName("chat_header_title")
        hl.addWidget(self.header_title)
        hl.addSpacing(12)

        self.header_status = QLabel("就绪")
        self.header_status.setObjectName("chat_header_status")
        hl.addWidget(self.header_status)
        hl.addStretch(1)

        self.export_btn = self._ghost_btn("导出结果", self._export_results)
        self.export_card_btn = self._ghost_btn("导出翻译卡", self._export_plan_card)
        hl.addWidget(self.export_btn)
        hl.addWidget(self.export_card_btn)
        pl.addWidget(header)

        # 消息区
        self.chat_display = ChatDisplay()
        self.chat_display.suggestion_clicked.connect(self._on_suggestion)
        pl.addWidget(self.chat_display, 1)

        # 输入区
        dock = QWidget()
        dock.setObjectName("input_dock")
        dl = QVBoxLayout(dock)
        dl.setContentsMargins(24, 8, 24, 14)
        dl.setSpacing(6)

        card = QFrame()
        card.setObjectName("input_card")
        card.setProperty("focused", "false")
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 26))
        card.setGraphicsEffect(shadow)
        self.input_card = card
        self._input_shadow = shadow

        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 12, 12, 10)
        cl.setSpacing(8)

        self.message_input = QTextEdit()
        self.message_input.setObjectName("message_input")
        self.message_input.setPlaceholderText("描述你的研究兴趣，例如「我想研究扩散模型在图像生成中的最新进展」…")
        self.message_input.setAcceptRichText(False)
        self.message_input.setFixedHeight(44)
        self.message_input.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.message_input.installEventFilter(self)
        self.message_input.textChanged.connect(self._auto_resize_input)
        cl.addWidget(self.message_input)

        bottom = QHBoxLayout()
        bottom.setSpacing(8)
        hint = QLabel("Enter 发送 · Shift+Enter 换行 · 输入「跳过」可直接生成计划")
        hint.setObjectName("input_hint")
        bottom.addWidget(hint)
        bottom.addStretch(1)

        self.send_btn = QPushButton("↑")
        self.send_btn.setObjectName("send_btn")
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.send_btn.setToolTip("发送 (Enter)")
        self.send_btn.clicked.connect(self._send_message)
        bottom.addWidget(self.send_btn)
        cl.addLayout(bottom)

        dl.addWidget(card)
        pl.addWidget(dock)
        return panel

    def _ghost_btn(self, text: str, slot) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("ghost_btn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn.clicked.connect(slot)
        return btn

    def _auto_resize_input(self):
        doc = self.message_input.document()
        h = int(doc.size().height()) + 22
        self.message_input.setFixedHeight(max(44, min(h, 160)))

    # ------------------------------------------------ Worker

    def _ensure_worker(self):
        if self._worker is None:
            self._worker = AgentWorker(self._config)
            self._worker.agent_response.connect(self._on_agent_response)
            self._worker.plan_card_ready.connect(self._on_plan_card_ready)
            self._worker.search_results.connect(self._on_search_results)
            self._worker.status.connect(self._on_status)
            self._worker.error.connect(self._on_error)
            self._worker.finished.connect(self._on_finished)
            self._worker.start()

    # ------------------------------------------------ 对话管理

    def _new_conversation(self):
        conv_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._current_conv_id = conv_id
        self._conversations[conv_id] = {
            "title": "新对话",
            "messages": [],
            "timestamp": datetime.now().isoformat(),
            "plan_card": None,
            "search_results": [],
        }
        self.chat_display.clear()
        self.chat_display.show_welcome()
        self.header_title.setText("新对话")
        self.sidebar.update_conversations(self._conversations, self._current_conv_id)
        if self._worker:
            self._worker.submit_reset()
        self.message_input.setFocus()

    def _switch_conversation(self, conv_id: str):
        if not conv_id or conv_id not in self._conversations:
            return
        if conv_id == self._current_conv_id:
            return
        self._save_current_conversation()
        self._current_conv_id = conv_id
        conv = self._conversations[conv_id]
        self.header_title.setText(conv.get("title", "新对话"))

        self.chat_display.clear()
        messages = conv.get("messages", [])
        if not messages:
            self.chat_display.show_welcome()
        else:
            for msg in messages:
                self.chat_display.add_message(
                    msg["content"], is_user=(msg["role"] == "user")
                )
        self.sidebar.update_conversations(self._conversations, conv_id)
        # 切换对话后重置 Agent（历史对话不支持续聊，从头开始）
        if self._worker:
            self._worker.submit_reset()

    def _delete_conversation(self, conv_id: str):
        conv = self._conversations.get(conv_id)
        if not conv:
            return
        title = conv.get("title", "新对话")
        answer = QMessageBox.question(
            self,
            "删除对话",
            f"确定删除「{title}」吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self._conversations.pop(conv_id, None)
        try:
            os.remove(os.path.join(_HISTORY_DIR, f"{conv_id}.json"))
        except OSError:
            pass

        if conv_id == self._current_conv_id:
            self._current_conv_id = None
            self._new_conversation()
        else:
            self.sidebar.update_conversations(self._conversations, self._current_conv_id)

    def _load_conversations(self):
        os.makedirs(_HISTORY_DIR, exist_ok=True)
        for fname in os.listdir(_HISTORY_DIR):
            if fname.endswith(".json"):
                try:
                    with open(os.path.join(_HISTORY_DIR, fname), "r", encoding="utf-8") as f:
                        data = json.load(f)
                    conv_id = data.get("id", fname.replace(".json", ""))
                    self._conversations[conv_id] = data
                except Exception:
                    pass

    def _save_current_conversation(self):
        conv = self._conversations.get(self._current_conv_id)
        if not conv:
            return
        os.makedirs(_HISTORY_DIR, exist_ok=True)
        path = os.path.join(_HISTORY_DIR, f"{self._current_conv_id}.json")
        data = {**conv, "id": self._current_conv_id}
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ------------------------------------------------ 消息收发

    def eventFilter(self, obj, event):
        if obj is self.message_input:
            if event.type() == QEvent.Type.FocusIn:
                self._set_input_focus(True)
            elif event.type() == QEvent.Type.FocusOut:
                self._set_input_focus(False)
            elif event.type() == QEvent.Type.KeyPress:
                key = event.key()
                if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                        self.message_input.insertPlainText("\n")
                    else:
                        self._send_message()
                    return True
        return super().eventFilter(obj, event)

    def _set_input_focus(self, focused: bool):
        """输入框聚焦：卡片描边变陶土色 + 阴影带上品牌色光晕"""
        self.input_card.setProperty("focused", "true" if focused else "false")
        self.input_card.style().unpolish(self.input_card)
        self.input_card.style().polish(self.input_card)
        if focused:
            self._input_shadow.setBlurRadius(36)
            self._input_shadow.setColor(QColor(217, 119, 87, 42))
        else:
            self._input_shadow.setBlurRadius(28)
            self._input_shadow.setColor(QColor(0, 0, 0, 26))

    def _on_suggestion(self, text: str):
        if self._busy:
            return
        self.message_input.setPlainText(text)
        self._send_message()

    def _send_message(self):
        if self._busy:
            return
        text = self.message_input.toPlainText().strip()
        if not text:
            return

        self.chat_display.hide_welcome()
        self.chat_display.add_message(text, is_user=True)
        self.message_input.clear()
        self.message_input.setFixedHeight(44)

        conv = self._conversations.get(self._current_conv_id)
        if conv:
            conv["messages"].append({"role": "user", "content": text})
            conv["timestamp"] = datetime.now().isoformat()
            if conv["title"] == "新对话":
                conv["title"] = text[:24]
                self.header_title.setText(conv["title"])
                self.sidebar.update_conversations(self._conversations, self._current_conv_id)

        self._set_busy(True)
        self.chat_display.show_thinking()
        self._ensure_worker()
        self._worker.submit(text)

    def _set_busy(self, busy: bool):
        self._busy = busy
        self.send_btn.setEnabled(not busy)
        self.header_status.setText("Waiting for reply…" if busy else self._idle_status())

    def _llm_configured(self) -> bool:
        """LLM Key 是否可用：设置页优先，留空回落到 .env / 环境变量"""
        key = (self._config.get("openai_api_key") or "").strip()
        return bool(key) or bool(os.environ.get("OPENAI_API_KEY", "").strip())

    def _idle_status(self) -> str:
        if self._llm_configured():
            return "就绪"
        return "未配置 API Key · 点左下角「设置」"

    def _on_status(self, text: str):
        self.chat_display.show_thinking(text)
        self.header_status.setText(text)

    def _on_agent_response(self, text: str):
        self.chat_display.hide_thinking()
        self.chat_display.add_message(text, is_user=False)
        conv = self._conversations.get(self._current_conv_id)
        if conv:
            conv["messages"].append({"role": "agent", "content": text})

    def _on_plan_card_ready(self, card_dict: dict):
        self.chat_display.hide_thinking()
        self.chat_display.add_plan_card(card_dict)
        conv = self._conversations.get(self._current_conv_id)
        if conv:
            conv["plan_card"] = card_dict
            try:
                from presentation.render_results import render_plan_card
                conv["messages"].append(
                    {"role": "agent", "content": render_plan_card(card_dict)}
                )
            except Exception:
                conv["messages"].append(
                    {"role": "agent", "content": json.dumps(card_dict, ensure_ascii=False)}
                )

    def _on_search_results(self, results: list):
        self.chat_display.hide_thinking()
        self.chat_display.add_search_cards(results)
        conv = self._conversations.get(self._current_conv_id)
        if conv:
            conv["search_results"] = results
            try:
                from presentation.render_results import render_results
                conv["messages"].append(
                    {"role": "agent", "content": render_results(results)}
                )
            except Exception:
                conv["messages"].append(
                    {"role": "agent", "content": f"检索到 {len(results)} 篇论文"}
                )

    def _on_error(self, error: str):
        self.chat_display.hide_thinking()
        self.chat_display.add_message(f"[错误] {error}", is_user=False)

    def _on_finished(self):
        self.chat_display.hide_thinking()
        self._set_busy(False)
        self._save_current_conversation()
        self.message_input.setFocus()

    # ------------------------------------------------ 设置 / 导出

    def _open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            self._config = dialog.get_config()
            if self._worker:
                self._worker.update_config(self._config)
            self.header_status.setText(self._idle_status())

    def _export_results(self):
        conv = self._conversations.get(self._current_conv_id)
        if not conv or not conv.get("search_results"):
            QMessageBox.information(self, "提示", "当前对话没有检索结果。")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "导出检索结果", "", "Text Files (*.txt);;All Files (*)"
        )
        if not path:
            return

        results = conv["search_results"]
        with open(path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("检索结果\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"结果数量：{len(results)} 篇\n\n")
            for i, paper in enumerate(results, 1):
                f.write(f"[{i}] {paper.get('title', '无标题')}\n\n")
                authors = paper.get("authors", [])
                if authors:
                    f.write(f"作者：{', '.join(authors)}\n")
                year = paper.get("year", "")
                if year:
                    f.write(f"年份：{year}\n")
                venue = paper.get("venue", "")
                if venue:
                    f.write(f"发表：{venue}\n")
                doi = paper.get("doi", "")
                if doi:
                    f.write(f"DOI: {doi}\n")
                url = paper.get("url", "")
                if url:
                    f.write(f"链接：{url}\n")
                f.write(f"\n摘要：{paper.get('abstract', '无摘要')}\n")
                bibtex = paper.get("bibtex", "")
                if bibtex:
                    f.write(f"\nBibTeX:\n{bibtex}\n")
                f.write("\n" + "-" * 60 + "\n\n")

        QMessageBox.information(self, "导出成功", f"已保存到:\n{path}")

    def _export_plan_card(self):
        conv = self._conversations.get(self._current_conv_id)
        if not conv or not conv.get("plan_card"):
            QMessageBox.information(self, "提示", "当前对话没有需求翻译卡。")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "导出需求翻译卡", "", "Text Files (*.txt);;YAML Files (*.yaml);;All Files (*)"
        )
        if not path:
            return

        card = conv["plan_card"]
        with open(path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("需求翻译卡\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"研究兴趣：{card.get('research_interest', '')}\n")
            f.write(f"解读问题：{card.get('interpreted_question', '')}\n")
            f.write(f"研究类型：{card.get('research_intent_type', '')}\n\n")
            f.write("关键维度:\n")
            for dim in card.get("key_dimensions", []):
                f.write(f"  - {dim}\n")
            f.write("\n建议关键词:\n")
            kw = card.get("suggested_keywords", {})
            f.write(f"  主要：{', '.join(kw.get('primary', []))}\n")
            f.write(f"  变体：{', '.join(kw.get('variants', []))}\n")
            f.write(f"  相邻领域：{', '.join(kw.get('adjacent_fields', []))}\n\n")
            f.write("不确定性:\n")
            for unc in card.get("uncertainties", []):
                f.write(f"  - {unc}\n")
            f.write("\n检索计划:\n")
            sp = card.get("search_plan", {})
            f.write(f"  模式：{sp.get('mode', '')}\n")
            f.write("  建议查询:\n")
            for q in sp.get("suggested_queries", []):
                f.write(f"    - {q}\n")
            f.write("\n下一步行动:\n")
            for action in card.get("next_actions", []):
                f.write(f"  - {action}\n")

        QMessageBox.information(self, "导出成功", f"已保存到:\n{path}")

    def closeEvent(self, event):
        self._save_current_conversation()
        if self._worker:
            self._worker.stop()
            self._worker.wait(3000)
        event.accept()
