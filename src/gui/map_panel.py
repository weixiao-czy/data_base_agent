"""
内置文献地图面板

把生成的 HTML 思维导图直接嵌在应用窗口右侧，不再跳外部浏览器。
QtWebEngine 是可选依赖：缺失时降级为提示 + 「在浏览器打开」按钮，
不影响主流程。
"""

import os
import webbrowser

from PyQt6.QtCore import Qt, QCoreApplication, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Chromium 的沙箱在受限环境和部分 Windows 账户下起不来渲染进程，
# 表现为 QWebEngineView 空白且 loadFinished(success=False)。
# 本面板只渲染自己生成的本地 HTML，不加载外部页面，因此关掉沙箱是可接受的；
# 外部已经显式设置过 flags 时不覆盖用户的选择。
os.environ.setdefault(
    "QTWEBENGINE_CHROMIUM_FLAGS", "--no-sandbox --disable-gpu"
)

# PyQt6 6.11 导入 QtWebEngineWidgets 时不再自动设置该属性，
# 缺失会让 WebEngine 初始化时直接 qFatal 闪退。必须在 QApplication
# 创建前设置；本模块由 main_window 在 QApplication 之前导入。
QCoreApplication.setAttribute(
    Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True
)

try:  # PyQt6-WebEngine 需要单独安装
    from PyQt6.QtWebEngineCore import QWebEnginePage
    from PyQt6.QtWebEngineWidgets import QWebEngineView

    HAS_WEBENGINE = True
except Exception:  # noqa: BLE001 - 缺依赖、DLL 缺失都会抛不同的错
    QWebEnginePage = None
    QWebEngineView = None
    HAS_WEBENGINE = False

EXTERNAL_SCHEMES = ("http", "https", "mailto")


def _open_in_system_browser(url: QUrl):
    QDesktopServices.openUrl(url)


if HAS_WEBENGINE:

    class _MapPage(QWebEnginePage):
        """导图预览只读：外链一律交给系统浏览器，不在内嵌页面里跳走。

        导图里的文献链接是 target="_blank"，QtWebEngine 默认不创建新窗口，
        点击会毫无反应；同页跳转则会把内嵌的导图本身替换掉。两条路径都要拦。
        """

        def __init__(self, parent=None):
            super().__init__(parent)
            self.newWindowRequested.connect(self._on_new_window_requested)

        def acceptNavigationRequest(self, url, nav_type, is_main_frame):
            link_clicked = (
                nav_type
                == QWebEnginePage.NavigationType.NavigationTypeLinkClicked
            )
            if link_clicked and self._open_externally(url):
                return False
            return super().acceptNavigationRequest(url, nav_type, is_main_frame)

        def _on_new_window_requested(self, request):
            self._open_externally(request.requestedUrl())

        @staticmethod
        def _open_externally(url: QUrl) -> bool:
            if url.scheme().lower() not in EXTERNAL_SCHEMES:
                return False
            _open_in_system_browser(url)
            return True


class MapPanel(QFrame):
    """右侧内嵌导图面板（默认隐藏，生成导图后展开）"""

    closed = pyqtSignal()
    load_failed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("map_panel")
        self.setMinimumWidth(360)
        self._path = ""
        self._view = None
        self._page = None
        self._setup_ui()
        self.hide()

    # ------------------------------------------------------------ UI

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        header = QFrame()
        header.setObjectName("map_header")
        header.setFixedHeight(46)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 0, 10, 0)
        hl.setSpacing(8)

        dot = QLabel("◈")
        dot.setObjectName("map_dot")
        hl.addWidget(dot)

        self.title = QLabel("文献地图")
        self.title.setObjectName("map_title")
        hl.addWidget(self.title, 1)

        self.browser_btn = QPushButton("在浏览器打开")
        self.browser_btn.setObjectName("map_action")
        self.browser_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browser_btn.clicked.connect(self._open_external)
        hl.addWidget(self.browser_btn)

        self.close_btn = QPushButton("返回对话")
        self.close_btn.setObjectName("map_close")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setToolTip("回到对话页")
        self.close_btn.clicked.connect(self._on_close)
        hl.addWidget(self.close_btn)

        lay.addWidget(header)

        # 内嵌渲染失败时的提示条：宁可说清楚，也不要留一片空白
        self.hint = QLabel()
        self.hint.setObjectName("map_hint")
        self.hint.setWordWrap(True)
        self.hint.hide()
        lay.addWidget(self.hint)

        body = QWidget()
        body.setObjectName("map_body")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setSpacing(0)

        if HAS_WEBENGINE:
            self._view = QWebEngineView(body)
            self._view.setObjectName("map_view")
            self._view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            self._page = _MapPage(self._view)
            self._view.setPage(self._page)
            self._view.loadFinished.connect(self._on_load_finished)
            bl.addWidget(self._view)
        else:
            tip = QLabel(
                "当前环境缺少 QtWebEngine，无法内嵌预览。\n"
                "请点击右上角「在浏览器打开」，或安装：\n"
                "pip install PyQt6-WebEngine"
            )
            tip.setObjectName("map_fallback")
            tip.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tip.setWordWrap(True)
            bl.addWidget(tip)

        lay.addWidget(body, 1)

    # ------------------------------------------------------------ 对外

    def show_map(self, html_path: str, topic: str = ""):
        """载入并展开导图"""
        self._path = os.path.abspath(html_path)
        label = topic.strip() or os.path.basename(self._path)
        if len(label) > 18:
            label = label[:18] + "…"
        self.title.setText(f"文献地图 · {label}")
        self.title.setToolTip(self._path)
        if self._view is not None:
            self._view.setUrl(QUrl.fromLocalFile(self._path))
        self.show()

    def clear(self):
        if self._view is not None:
            self._view.setUrl(QUrl("about:blank"))

    # ------------------------------------------------------------ 内部

    def _open_external(self):
        if self._path and os.path.exists(self._path):
            webbrowser.open("file://" + self._path)

    def _on_load_finished(self, ok: bool):
        """内嵌渲染失败时不留白：提示原因并通知主窗口降级到外部浏览器"""
        if ok or not self._path:
            self.hint.hide()
            return
        self.hint.setText(
            "内嵌预览加载失败，已改用默认浏览器打开；"
            "若浏览器没有弹出，请点右上角「在浏览器打开」。"
        )
        self.hint.show()
        self.load_failed.emit(self._path)

    def _on_close(self):
        self.hide()
        self.clear()
        self.closed.emit()
