"""
主窗口 — 侧边栏 + 聊天界面
"""

import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QTextEdit, QSplitter, QFrame, QFileDialog, QMessageBox,
)
from PyQt6.QtCore import Qt, QSize

from .styles import COLORS, GLOBAL_QSS, SIDEBAR_QSS, CHAT_QSS
from .chat_widget import ChatDisplay
from .agent_worker import AgentWorker
from .settings_dialog import SettingsDialog, load_config

# 对话历史存储路径
_HISTORY_DIR = os.path.join(os.path.expanduser("~"), ".databaseagent", "conversations")


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("文献检索需求翻译 Agent")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        self.setStyleSheet(GLOBAL_QSS + SIDEBAR_QSS + CHAT_QSS)

        self._config = load_config()
        self._conversations = {}  # id -> {title, messages, timestamp}
        self._current_conv_id = None
        self._worker = None

        self._setup_ui()
        self._load_conversations()
        self._new_conversation()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- 左侧边栏 ---
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # 侧边栏头部
        header = QWidget()
        header.setObjectName("sidebar_header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 16, 16, 12)

        title_label = QLabel("文献检索 Agent")
        title_label.setObjectName("sidebar_title")
        header_layout.addWidget(title_label)

        new_btn = QPushButton("+ 新对话")
        new_btn.setObjectName("new_chat_btn")
        new_btn.clicked.connect(self._new_conversation)
        header_layout.addWidget(new_btn)

        sidebar_layout.addWidget(header)

        # 对话列表
        self.conv_list = QListWidget()
        self.conv_list.setObjectName("conversation_list")
        self.conv_list.currentRowChanged.connect(self._switch_conversation)
        sidebar_layout.addWidget(self.conv_list)

        # 底部设置按钮
        settings_btn = QPushButton("⚙ 设置")
        settings_btn.setObjectName("settings_btn")
        settings_btn.clicked.connect(self._open_settings)
        sidebar_layout.addWidget(settings_btn)

        splitter.addWidget(sidebar)

        # --- 右侧聊天区域 ---
        chat_panel = QWidget()
        chat_layout = QVBoxLayout(chat_panel)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # 工具栏
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 8, 16, 8)

        self.export_btn = QPushButton("导出结果")
        self.export_btn.setObjectName("export_btn")
        self.export_btn.clicked.connect(self._export_results)
        toolbar_layout.addWidget(self.export_btn)

        self.export_card_btn = QPushButton("导出需求翻译卡")
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
        input_layout.setContentsMargins(16, 12, 16, 12)

        self.message_input = QTextEdit()
        self.message_input.setObjectName("message_input")
        self.message_input.setPlaceholderText("描述你的研究兴趣...")
        self.message_input.setMaximumHeight(100)
        self.message_input.setAcceptRichText(False)
        input_layout.addWidget(self.message_input, 1)

        send_btn = QPushButton("发送")
        send_btn.setObjectName("send_btn")
        send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(send_btn)

        chat_layout.addWidget(input_area)

        splitter.addWidget(chat_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

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
        self._refresh_conv_list()

        # 初始化 worker
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

        # 显示用户消息
        self.chat_display.add_message(text, is_user=True)
        self.message_input.clear()

        # 保存消息
        conv = self._conversations.get(self._current_conv_id)
        if conv:
            conv["messages"].append({"role": "user", "content": text})
            if conv["title"] == "新对话":
                conv["title"] = text[:30]
                self._refresh_conv_list()

        # 禁用输入
        self.message_input.setEnabled(False)

        # 启动 worker
        if self._worker is None:
            self._init_worker()
        self._worker.process(text)

    def _on_agent_response(self, text: str):
        """Agent 回复"""
        self.chat_display.add_message(text, is_user=False)
        conv = self._conversations.get(self._current_conv_id)
        if conv:
            conv["messages"].append({"role": "agent", "content": text})

    def _on_plan_card_ready(self, card_dict: dict):
        """需求翻译卡就绪"""
        conv = self._conversations.get(self._current_conv_id)
        if conv:
            conv["plan_card"] = card_dict

    def _on_search_results(self, results: list):
        """检索结果就绪"""
        conv = self._conversations.get(self._current_conv_id)
        if conv:
            conv["search_results"] = results

    def _on_error(self, error: str):
        """错误"""
        self.chat_display.add_message(f"[错误] {error}", is_user=False)

    def _on_finished(self):
        """一轮处理完成"""
        self.message_input.setEnabled(True)
        self.message_input.setFocus()

    def _open_settings(self):
        """打开设置"""
        dialog = SettingsDialog(self)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            self._config = dialog.get_config()
            # 重新初始化 worker
            self._init_worker()

    def _switch_conversation(self, row: int):
        """切换对话"""
        if row < 0:
            return
        item = self.conv_list.item(row)
        conv_id = item.data(Qt.ItemDataRole.UserRole)
        if conv_id and conv_id in self._conversations:
            self._current_conv_id = conv_id
            conv = self._conversations[conv_id]
            self.chat_display.clear()
            for msg in conv["messages"]:
                self.chat_display.add_message(
                    msg["content"], is_user=(msg["role"] == "user")
                )
            self._init_worker()

    def _refresh_conv_list(self):
        """刷新对话列表"""
        self.conv_list.clear()
        for conv_id, conv in sorted(
            self._conversations.items(), key=lambda x: x[1]["timestamp"], reverse=True
        ):
            item = QListWidgetItem(conv["title"])
            item.setData(Qt.ItemDataRole.UserRole, conv_id)
            self.conv_list.addItem(item)
            if conv_id == self._current_conv_id:
                self.conv_list.setCurrentItem(item)

    def _load_conversations(self):
        """从磁盘加载对话历史"""
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
        """保存当前对话到磁盘"""
        conv = self._conversations.get(self._current_conv_id)
        if not conv:
            return
        os.makedirs(_HISTORY_DIR, exist_ok=True)
        path = os.path.join(_HISTORY_DIR, f"{self._current_conv_id}.json")
        data = {**conv, "id": self._current_conv_id}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _export_results(self):
        """导出检索结果为 txt"""
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
            f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"结果数量: {len(results)} 篇\n\n")
            for i, paper in enumerate(results, 1):
                f.write(f"[{i}] {paper.get('title', '无标题')}\n\n")
                authors = paper.get("authors", [])
                if authors:
                    f.write(f"作者: {', '.join(authors)}\n")
                year = paper.get("year", "")
                if year:
                    f.write(f"年份: {year}\n")
                venue = paper.get("venue", "")
                if venue:
                    f.write(f"发表: {venue}\n")
                doi = paper.get("doi", "")
                if doi:
                    f.write(f"DOI: {doi}\n")
                url = paper.get("url", "")
                if url:
                    f.write(f"链接: {url}\n")
                f.write(f"\n摘要: {paper.get('abstract', '无摘要')}\n")
                bibtex = paper.get("bibtex", "")
                if bibtex:
                    f.write(f"\nBibTeX:\n{bibtex}\n")
                f.write("\n" + "-" * 60 + "\n\n")

        QMessageBox.information(self, "导出成功", f"已保存到:\n{path}")

    def _export_plan_card(self):
        """导出需求翻译卡为 txt"""
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
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"研究兴趣: {card.get('research_interest', '')}\n")
            f.write(f"解读问题: {card.get('interpreted_question', '')}\n")
            f.write(f"研究类型: {card.get('research_intent_type', '')}\n\n")
            f.write("关键维度:\n")
            for dim in card.get("key_dimensions", []):
                f.write(f"  - {dim}\n")
            f.write("\n建议关键词:\n")
            kw = card.get("suggested_keywords", {})
            f.write(f"  主要: {', '.join(kw.get('primary', []))}\n")
            f.write(f"  变体: {', '.join(kw.get('variants', []))}\n")
            f.write(f"  相邻领域: {', '.join(kw.get('adjacent_fields', []))}\n\n")
            f.write("不确定性:\n")
            for unc in card.get("uncertainties", []):
                f.write(f"  - {unc}\n")
            f.write("\n检索计划:\n")
            sp = card.get("search_plan", {})
            f.write(f"  模式: {sp.get('mode', '')}\n")
            f.write("  建议查询:\n")
            for q in sp.get("suggested_queries", []):
                f.write(f"    - {q}\n")
            f.write("\n下一步行动:\n")
            for action in card.get("next_actions", []):
                f.write(f"  - {action}\n")

        QMessageBox.information(self, "导出成功", f"已保存到:\n{path}")

    def closeEvent(self, event):
        """关闭窗口时保存对话"""
        self._save_current_conversation()
        if self._worker:
            self._worker.quit()
            self._worker.wait()
        event.accept()
