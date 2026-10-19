"""
主窗口 — 现代 IDE 风格（无边框 + 自定义顶栏 + 图标侧边栏）
"""

import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QTextEdit, QFrame, QFileDialog, QMessageBox,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QMouseEvent

from .styles import COLORS, GLOBAL_QSS, TITLEBAR_QSS, SIDEBAR_QSS, CHAT_QSS
from .chat_widget import ChatDisplay
from .agent_worker import AgentWorker
from .settings_dialog import SettingsDialog, load_config

# 对话历史存储路径
_HISTORY_DIR = os.path.join(os.path.expanduser("~"), ".databaseagent", "conversations")


class TitleBar(QFrame):
    """自定义顶栏（无边框窗口的标题栏）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titlebar")
        self.setFixedHeight(36)
        self._parent_window = parent
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 0, 0)
        layout.setSpacing(0)

        # 左侧：窗口控制按钮（模拟）
        self.min_btn = QPushButton("—")
        self.min_btn.setObjectName("titlebar_btn")
        self.min_btn.setFixedSize(36, 36)
        self.min_btn.clicked.connect(self._minimize)
        layout.addWidget(self.min_btn)

        self.max_btn = QPushButton("□")
        self.max_btn.setObjectName("titlebar_btn")
        self.max_btn.setFixedSize(36, 36)
        self.max_btn.clicked.connect(self._maximize)
        layout.addWidget(self.max_btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("titlebar_btn titlebar_close")
        self.close_btn.setFixedSize(36, 36)
        self.close_btn.clicked.connect(self._close)
        layout.addWidget(self.close_btn)

        layout.addSpacing(12)

        # 中间：标题
        self.title_label = QLabel("文献检索需求翻译 Agent")
        self.title_label.setObjectName("titlebar_title")
        layout.addWidget(self.title_label)

        layout.addStretch()

    def _minimize(self):
        if self._parent_window:
            self._parent_window.showMinimized()

    def _maximize(self):
        if self._parent_window:
            if self._parent_window.isMaximized():
                self._parent_window.showNormal()
            else:
                self._parent_window.showMaximized()

    def _close(self):
        if self._parent_window:
            self._parent_window.close()

    def mouseDoubleClickEvent(self, event):
        """双击顶栏最大化/还原"""
        self._maximize()

    def mousePressEvent(self, event):
        """拖拽移动窗口"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_pos'):
            if self._parent_window:
                delta = event.globalPosition().toPoint() - self._drag_pos
                self._parent_window.move(self._parent_window.pos() + delta)
                self._drag_pos = event.globalPosition().toPoint()


class Sidebar(QWidget):
    """现代 IDE 风格侧边栏"""

    new_chat_clicked = pyqtSignal()
    conversation_selected = pyqtSignal(str)  # conv_id
    settings_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(240)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部：模式按钮
        top = QFrame()
        top.setObjectName("sidebar_top")
        top_layout = QVBoxLayout(top)
        top_layout.setContentsMargins(8, 8, 8, 8)

        mode_btn = QPushButton("💻 编程")
        mode_btn.setObjectName("sidebar_mode_btn")
        top_layout.addWidget(mode_btn)

        layout.addWidget(top)

        # 导航区
        nav = QListWidget()
        nav.setObjectName("sidebar_nav")
        nav.setMaximumHeight(200)

        nav_items = [
            ("✨ 新的任务", "new"),
            ("📁 项目", "projects"),
            ("💬 讨论", "discussions"),
            ("🔍 搜索", "search"),
        ]
        for text, _ in nav_items:
            item = QListWidgetItem(text)
            nav.addItem(item)

        nav.currentRowChanged.connect(self._on_nav_changed)
        layout.addWidget(nav)

        # 工作区标题
        workspace_title = QLabel("工作区")
        workspace_title.setObjectName("sidebar_section_title")
        layout.addWidget(workspace_title)

        # 对话列表
        self.conv_list = QListWidget()
        self.conv_list.setObjectName("sidebar_conv_list")
        self.conv_list.currentRowChanged.connect(self._on_conv_selected)
        layout.addWidget(self.conv_list, 1)

        # 最近任务标题
        recent_title = QLabel("最近任务")
        recent_title.setObjectName("sidebar_section_title")
        layout.addWidget(recent_title)

        # 最近任务列表（占位）
        recent_list = QListWidget()
        recent_list.setObjectName("sidebar_conv_list")
        recent_list.setMaximumHeight(80)
        layout.addWidget(recent_list)

        # 底部：设置按钮
        bottom = QFrame()
        bottom.setObjectName("sidebar_bottom")
        bottom_layout = QVBoxLayout(bottom)
        bottom_layout.setContentsMargins(8, 8, 8, 8)

        settings_btn = QPushButton("️ 设置")
        settings_btn.setObjectName("sidebar_settings_btn")
        settings_btn.clicked.connect(self.settings_clicked.emit)
        bottom_layout.addWidget(settings_btn)

        layout.addWidget(bottom)

    def _on_nav_changed(self, row):
        if row == 0:  # 新的任务
            self.new_chat_clicked.emit()

    def _on_conv_selected(self, row):
        if row >= 0:
            item = self.conv_list.item(row)
            conv_id = item.data(Qt.ItemDataRole.UserRole)
            if conv_id:
                self.conversation_selected.emit(conv_id)

    def update_conversations(self, conversations: dict, current_id: str):
        """更新对话列表"""
        self.conv_list.clear()
        for conv_id, conv in sorted(
            conversations.items(), key=lambda x: x[1].get("timestamp", ""), reverse=True
        ):
            item = QListWidgetItem(conv.get("title", "新对话"))
            item.setData(Qt.ItemDataRole.UserRole, conv_id)
            self.conv_list.addItem(item)
            if conv_id == current_id:
                self.conv_list.setCurrentItem(item)


class MainWindow(QMainWindow):
    """主窗口 — 现代 IDE 风格"""

    def __init__(self):
        super().__init__()
        # 无边框窗口
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Window
        )
        self.setWindowTitle("文献检索需求翻译 Agent")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        self.setStyleSheet(GLOBAL_QSS + TITLEBAR_QSS + SIDEBAR_QSS + CHAT_QSS)

        self._config = load_config()
        self._conversations = {}
        self._current_conv_id = None
        self._worker = None

        self._setup_ui()
        self._load_conversations()
        self._new_conversation()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 自定义顶栏
        self.titlebar = TitleBar(self)
        main_layout.addWidget(self.titlebar)

        # 内容区
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 侧边栏
        self.sidebar = Sidebar()
        self.sidebar.new_chat_clicked.connect(self._new_conversation)
        self.sidebar.conversation_selected.connect(self._switch_conversation)
        self.sidebar.settings_clicked.connect(self._open_settings)
        content_layout.addWidget(self.sidebar)

        # 右侧聊天区
        chat_panel = QWidget()
        chat_layout = QVBoxLayout(chat_panel)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # 工具栏
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 6, 12, 6)

        self.export_btn = QPushButton("📥 导出结果")
        self.export_btn.setObjectName("export_btn")
        self.export_btn.clicked.connect(self._export_results)
        toolbar_layout.addWidget(self.export_btn)

        self.export_card_btn = QPushButton("📋 导出需求翻译卡")
        self.export_card_btn.setObjectName("export_btn")
        self.export_card_btn.clicked.connect(self._export_plan_card)
        toolbar_layout.addWidget(self.export_card_btn)

        toolbar_layout.addStretch()
        chat_layout.addWidget(toolbar)

        # 聊天显示
        self.chat_display = ChatDisplay()
        chat_layout.addWidget(self.chat_display)

        # 输入区域
        input_area = QFrame()
        input_area.setObjectName("input_area")
        input_layout = QHBoxLayout(input_area)
        input_layout.setContentsMargins(12, 10, 12, 10)

        self.message_input = QTextEdit()
        self.message_input.setObjectName("message_input")
        self.message_input.setPlaceholderText("描述你的研究兴趣...")
        self.message_input.setMaximumHeight(80)
        self.message_input.setAcceptRichText(False)
        input_layout.addWidget(self.message_input, 1)

        send_btn = QPushButton("发送")
        send_btn.setObjectName("send_btn")
        send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(send_btn)

        chat_layout.addWidget(input_area)

        content_layout.addWidget(chat_panel, 1)
        main_layout.addWidget(content, 1)

    def _new_conversation(self):
        """新建对话"""
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
        self.chat_display.add_message(
            "你好！我是文献检索需求翻译 Agent。\n\n"
            "请描述你的研究兴趣，我会帮你把模糊的想法翻译成精准的检索计划。\n"
            "最多 10 轮对话，你也可以随时说「跳过」直接生成计划。",
            is_user=False,
        )
        self.sidebar.update_conversations(self._conversations, self._current_conv_id)
        self._init_worker()

    def _init_worker(self):
        """初始化 Agent 工作线程"""
        if self._worker:
            self._worker.quit()
            self._worker.wait()

        self._worker = AgentWorker(self._config)
        self._worker.agent_response.connect(self._on_agent_response)
        self._worker.plan_card_ready.connect(self._on_plan_card_ready)
        self._worker.search_results.connect(self._on_search_results)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._on_finished)

    def _send_message(self):
        """发送消息"""
        text = self.message_input.toPlainText().strip()
        if not text:
            return

        self.chat_display.add_message(text, is_user=True)
        self.message_input.clear()

        conv = self._conversations.get(self._current_conv_id)
        if conv:
            conv["messages"].append({"role": "user", "content": text})
            if conv["title"] == "新对话":
                conv["title"] = text[:30]
                self.sidebar.update_conversations(self._conversations, self._current_conv_id)

        self.message_input.setEnabled(False)

        if self._worker is None:
            self._init_worker()
        self._worker.process(text)

    def _on_agent_response(self, text: str):
        self.chat_display.add_message(text, is_user=False)
        conv = self._conversations.get(self._current_conv_id)
        if conv:
            conv["messages"].append({"role": "agent", "content": text})

    def _on_plan_card_ready(self, card_dict: dict):
        conv = self._conversations.get(self._current_conv_id)
        if conv:
            conv["plan_card"] = card_dict

    def _on_search_results(self, results: list):
        conv = self._conversations.get(self._current_conv_id)
        if conv:
            conv["search_results"] = results

    def _on_error(self, error: str):
        self.chat_display.add_message(f"[错误] {error}", is_user=False)

    def _on_finished(self):
        self.message_input.setEnabled(True)
        self.message_input.setFocus()

    def _open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            self._config = dialog.get_config()
            self._init_worker()

    def _switch_conversation(self, conv_id: str):
        if conv_id and conv_id in self._conversations:
            self._current_conv_id = conv_id
            conv = self._conversations[conv_id]
            self.chat_display.clear()
            for msg in conv["messages"]:
                self.chat_display.add_message(
                    msg["content"], is_user=(msg["role"] == "user")
                )
            self._init_worker()

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
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

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
            self, "导出需求翻译卡", "", "Text Files (*.txt);;All Files (*)"
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
            self._worker.quit()
            self._worker.wait()
        event.accept()
