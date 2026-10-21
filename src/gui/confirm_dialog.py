"""
确认弹窗 — 破坏性操作的二次确认 + 轻量信息提示

不用 QMessageBox：系统弹窗的字体、圆角、按钮都跟主界面不是一套语言。
这里用无边框圆角卡片 + 压暗遮罩自绘，令牌全部来自 styles.COLORS。

两种形态：
- ask()  → 危险操作确认（红色确认按钮，默认焦点在「取消」，回车不删东西）
- info() → 单纯告知（单按钮，陶土色，点哪都能关）
"""

from PyQt6.QtCore import QEvent, QPoint, Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .styles import CONFIRM_DIALOG_QSS

# 卡片外侧留给阴影的空间
_SHADOW_MARGIN = 22


class Scrim(QWidget):
    """弹窗背后的压暗层，让卡片从界面里浮起来"""

    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setGeometry(parent.rect())
        parent.installEventFilter(self)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(28, 27, 24, 84))

    def mousePressEvent(self, event):
        # 吞掉遮罩上的点击，既不下沉到主界面，也不关闭弹窗
        event.accept()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Resize:
            self.setGeometry(obj.rect())
        return False


class ConfirmDialog(QDialog):
    """居中卡片：标题 + 说明 + 按钮"""

    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str = "删除",
        cancel_text: str | None = "取消",
        danger: bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)
        self.setStyleSheet(CONFIRM_DIALOG_QSS)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            _SHADOW_MARGIN, _SHADOW_MARGIN, _SHADOW_MARGIN, _SHADOW_MARGIN
        )
        outer.setSpacing(0)

        card = QFrame()
        card.setObjectName("confirm_card")
        card.setFixedWidth(392)
        outer.addWidget(card)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(36)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(28, 27, 24, 56))
        card.setGraphicsEffect(shadow)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(22, 20, 22, 18)
        cl.setSpacing(0)

        # ---------------- 标题行：圆形图标 + 标题
        head = QHBoxLayout()
        head.setContentsMargins(0, 0, 0, 0)
        head.setSpacing(10)

        icon = QLabel("!" if danger else "i")
        icon.setObjectName("confirm_icon" if danger else "confirm_icon_info")
        icon.setFixedSize(22, 22)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        head.addWidget(icon, 0, Qt.AlignmentFlag.AlignTop)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("confirm_title")
        self.title_label.setWordWrap(True)
        head.addWidget(self.title_label, 1)

        cl.addLayout(head)
        cl.addSpacing(10)

        # ---------------- 说明文字
        self.message_label = QLabel(message)
        self.message_label.setObjectName("confirm_message")
        self.message_label.setWordWrap(True)
        self.message_label.setMinimumWidth(320)
        cl.addWidget(self.message_label)
        cl.addSpacing(20)

        # ---------------- 按钮行
        btns = QHBoxLayout()
        btns.setContentsMargins(0, 0, 0, 0)
        btns.setSpacing(8)
        btns.addStretch(1)

        self.cancel_btn = None
        if cancel_text:
            self.cancel_btn = QPushButton(cancel_text)
            self.cancel_btn.setObjectName("confirm_cancel")
            self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.cancel_btn.clicked.connect(self.reject)
            btns.addWidget(self.cancel_btn)

        self.confirm_btn = QPushButton(confirm_text)
        self.confirm_btn.setObjectName("confirm_ok" if danger else "confirm_primary")
        self.confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.confirm_btn.clicked.connect(self.accept)
        btns.addWidget(self.confirm_btn)

        cl.addLayout(btns)

        # 危险操作：回车走「取消」，别让一个误触的回车把东西删了
        # 纯告知：只有一个按钮，它就当默认
        if self.cancel_btn is not None:
            self.cancel_btn.setDefault(True)
            self.confirm_btn.setAutoDefault(False)
            self.cancel_btn.setFocus()
        else:
            self.confirm_btn.setDefault(True)
            self.confirm_btn.setFocus()

        self._scrim = None

    # ---------------------------------------------------------- 显示

    def _center_on_parent(self):
        parent = self.parentWidget()
        if parent is None:
            return
        top_left = parent.mapToGlobal(QPoint(0, 0))
        x = top_left.x() + (parent.width() - self.width()) // 2
        y = top_left.y() + (parent.height() - self.height()) // 2
        self.move(x, y)

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

    # ---------------------------------------------------------- 快捷调用

    @classmethod
    def ask(
        cls,
        parent,
        title: str,
        message: str,
        confirm_text: str = "删除",
        cancel_text: str = "取消",
        danger: bool = True,
    ) -> bool:
        """一行调用：返回 True 表示用户确认"""
        dlg = cls(title, message, confirm_text, cancel_text, danger, parent)
        return dlg.exec() == QDialog.DialogCode.Accepted

    @classmethod
    def info(cls, parent, title: str, message: str, ok_text: str = "知道了"):
        """一行调用：只告知，不返回选择结果"""
        dlg = cls(title, message, ok_text, None, danger=False, parent=parent)
        dlg.exec()
