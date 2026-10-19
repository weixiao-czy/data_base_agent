"""
聊天显示组件 — 气泡式对话界面
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel,
)
from PyQt6.QtCore import Qt, pyqtSignal
from .styles import COLORS


class MessageBubble(QFrame):
    """单条消息气泡"""

    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.setObjectName("user_bubble" if is_user else "agent_bubble")
        self.setMaximumWidth(700)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        label = QLabel(text)
        label.setObjectName("message_label")
        label.setWordWrap(True)
        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        label.setOpenExternalLinks(True)
        layout.addWidget(label)


class ChatDisplay(QWidget):
    """
    聊天显示区域
    显示用户和 Agent 的消息气泡
    """

    export_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chat_area")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setObjectName("chat_area")

        # 消息容器
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(20, 20, 20, 20)
        self.messages_layout.setSpacing(8)
        self.messages_layout.addStretch()

        self.scroll_area.setWidget(self.messages_container)
        layout.addWidget(self.scroll_area)

    def add_message(self, text: str, is_user: bool = False):
        """添加一条消息"""
        # 移除底部的 stretch
        if self.messages_layout.count() > 0:
            item = self.messages_layout.itemAt(self.messages_layout.count() - 1)
            if item and item.spacerItem():
                self.messages_layout.removeItem(item)

        bubble = MessageBubble(text, is_user=is_user)

        # 使用 alignment 参数控制左右对齐
        alignment = Qt.AlignmentFlag.AlignRight if is_user else Qt.AlignmentFlag.AlignLeft
        self.messages_layout.addWidget(bubble, alignment=alignment)

        # 重新添加 stretch
        self.messages_layout.addStretch()

        # 滚动到底部
        self._scroll_to_bottom()

    def add_plan_card(self, card_dict: dict):
        """以格式化方式显示需求翻译卡"""
        from presentation.render_results import render_plan_card
        rendered = render_plan_card(card_dict)
        self.add_message(rendered, is_user=False)

    def add_search_results(self, results: list):
        """以格式化方式显示检索结果"""
        from presentation.render_results import render_results
        rendered = render_results(results)
        self.add_message(rendered, is_user=False)

    def clear(self):
        """清空所有消息"""
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _scroll_to_bottom(self):
        """滚动到底部"""
        sb = self.scroll_area.verticalScrollBar()
        sb.setValue(sb.maximum())
