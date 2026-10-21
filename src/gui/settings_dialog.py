"""
设置对话框 — 环境配置与常规设置

外观与主窗口、ConfirmDialog 同一套语言：无边框圆角卡片 + 外投影 + 压暗遮罩，
自绘标题行（标题 + 关闭），标题区可拖动。
"""

import os
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QFrame, QFormLayout, QGraphicsDropShadowEffect,
    QTabWidget, QWidget,
)
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QColor

from .styles import COLORS, SETTINGS_QSS
from .confirm_dialog import Scrim

# 配置文件路径（用户目录下）
_CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".databaseagent")
_CONFIG_FILE = os.path.join(_CONFIG_DIR, "config.json")

# 卡片外侧留给阴影的空间
_SHADOW_MARGIN = 22
# 标题区高度：在这个范围内按住可以拖动窗口
_DRAG_AREA = 78


def load_config() -> dict:
    """加载保存的配置"""
    if os.path.exists(_CONFIG_FILE):
        try:
            with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config(config: dict):
    """保存配置到文件"""
    os.makedirs(_CONFIG_DIR, exist_ok=True)
    with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settings_dialog")
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)
        self.setStyleSheet(SETTINGS_QSS)
        self._config = load_config()
        self._drag_pos = None
        self._scrim = None
        self._setup_ui()
        self._load_values()

    # ---------------------------------------------------------- UI

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            _SHADOW_MARGIN, _SHADOW_MARGIN, _SHADOW_MARGIN, _SHADOW_MARGIN
        )
        outer.setSpacing(0)

        card = QFrame()
        card.setObjectName("settings_card")
        card.setMinimumSize(560, 402)
        outer.addWidget(card)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 12)
        shadow.setColor(QColor(28, 27, 24, 60))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---------------- 标题行
        head = QWidget()
        hl = QHBoxLayout(head)
        hl.setContentsMargins(22, 16, 14, 12)
        hl.setSpacing(8)

        title = QLabel("设置")
        title.setObjectName("settings_title")
        hl.addWidget(title)
        hl.addStretch(1)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("settings_close")
        close_btn.setFixedSize(26, 26)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        close_btn.setToolTip("关闭")
        close_btn.clicked.connect(self.reject)
        hl.addWidget(close_btn)

        layout.addWidget(head)

        # ---------------- Tab 页
        tabs = QTabWidget()
        layout.addWidget(tabs, 1)

        # --- LLM 配置 ---
        llm_tab = QWidget()
        llm_layout = QFormLayout(llm_tab)
        llm_layout.setContentsMargins(22, 18, 22, 16)
        llm_layout.setSpacing(12)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("你的 API Key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        llm_layout.addRow("API Key:", self.api_key_input)

        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("https://models.sjtu.edu.cn/api/v1")
        llm_layout.addRow("Base URL:", self.base_url_input)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("deepseek-reasoner")
        llm_layout.addRow("模型:", self.model_input)

        hint = QLabel("保存后立即生效，无需重启；留空的项会自动读取 .env 配置。")
        hint.setWordWrap(True)
        llm_layout.addRow("", hint)

        tabs.addTab(llm_tab, "LLM 配置")

        # --- SciMaster 配置 ---
        sci_tab = QWidget()
        sci_layout = QFormLayout(sci_tab)
        sci_layout.setContentsMargins(22, 18, 22, 16)
        sci_layout.setSpacing(12)

        self.sci_key_input = QLineEdit()
        self.sci_key_input.setPlaceholderText("SciMaster API Key（可选）")
        self.sci_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        sci_layout.addRow("API Key:", self.sci_key_input)

        self.sci_url_input = QLineEdit()
        self.sci_url_input.setPlaceholderText("https://scimaster.bohrium.com/api/v1")
        sci_layout.addRow("Base URL:", self.sci_url_input)

        tabs.addTab(sci_tab, "SciMaster")

        # --- 常规设置 ---
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        general_layout.setContentsMargins(22, 18, 22, 16)
        general_layout.setSpacing(12)

        self.max_rounds_spin = QSpinBox()
        self.max_rounds_spin.setMinimum(1)
        self.max_rounds_spin.setMaximum(20)
        self.max_rounds_spin.setValue(10)
        general_layout.addRow("最大澄清轮次:", self.max_rounds_spin)

        self.search_limit_spin = QSpinBox()
        self.search_limit_spin.setMinimum(1)
        self.search_limit_spin.setMaximum(50)
        self.search_limit_spin.setValue(10)
        general_layout.addRow("检索结果数量:", self.search_limit_spin)

        self.search_timeout_spin = QSpinBox()
        self.search_timeout_spin.setMinimum(5)
        self.search_timeout_spin.setMaximum(120)
        self.search_timeout_spin.setValue(30)
        general_layout.addRow("检索超时(秒):", self.search_timeout_spin)

        tabs.addTab(general_tab, "常规")

        # ---------------- 按钮行
        btn_row = QWidget()
        btn_layout = QHBoxLayout(btn_row)
        btn_layout.setContentsMargins(22, 12, 22, 18)
        btn_layout.setSpacing(8)
        btn_layout.addStretch(1)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("保存")
        self.save_btn.setObjectName("save_btn")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self._save)
        btn_layout.addWidget(self.save_btn)

        layout.addWidget(btn_row)

    # ---------------------------------------------------------- 拖动

    def mousePressEvent(self, event):
        if (
            event.button() == Qt.MouseButton.LeftButton
            and event.position().y() < _DRAG_AREA
        ):
            self._drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    # ---------------------------------------------------------- 显示

    def exec(self) -> int:
        parent = self.parentWidget()
        if parent is not None:
            self._scrim = Scrim(parent)
            self._scrim.show()
            self._scrim.raise_()
        try:
            self.adjustSize()
            self._center_on_parent()
            return super().exec()
        finally:
            if self._scrim is not None:
                self._scrim.hide()
                self._scrim.setParent(None)
                self._scrim.deleteLater()
                self._scrim = None

    def _center_on_parent(self):
        parent = self.parentWidget()
        if parent is None:
            return
        top_left = parent.mapToGlobal(QPoint(0, 0))
        self.move(
            top_left.x() + (parent.width() - self.width()) // 2,
            top_left.y() + (parent.height() - self.height()) // 2,
        )

    # ---------------------------------------------------------- 配置

    def _load_values(self):
        """从配置加载值到输入框"""
        c = self._config
        self.api_key_input.setText(c.get("openai_api_key", ""))
        self.base_url_input.setText(c.get("openai_base_url", "https://models.sjtu.edu.cn/api/v1"))
        self.model_input.setText(c.get("openai_model", "deepseek-reasoner"))
        self.sci_key_input.setText(c.get("scimaster_api_key", ""))
        self.sci_url_input.setText(c.get("scimaster_base_url", "https://scimaster.bohrium.com/api/v1"))
        self.max_rounds_spin.setValue(c.get("max_rounds", 10))
        self.search_limit_spin.setValue(c.get("search_default_limit", 10))
        self.search_timeout_spin.setValue(c.get("search_timeout", 30))

    def _save(self):
        """保存配置"""
        self._config = {
            "openai_api_key": self.api_key_input.text().strip(),
            "openai_base_url": self.base_url_input.text().strip(),
            "openai_model": self.model_input.text().strip(),
            "scimaster_api_key": self.sci_key_input.text().strip(),
            "scimaster_base_url": self.sci_url_input.text().strip(),
            "max_rounds": self.max_rounds_spin.value(),
            "search_default_limit": self.search_limit_spin.value(),
            "search_timeout": self.search_timeout_spin.value(),
        }
        save_config(self._config)
        self.accept()

    def get_config(self) -> dict:
        """获取当前配置"""
        return self._config
