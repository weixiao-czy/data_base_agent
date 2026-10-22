"""
桌面 GUI 启动入口
"""

import sys
import os

# 确保 src 在 path 中
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))


def main():
    from PyQt6.QtWidgets import QApplication
    from gui.icons import app_icon
    from gui.main_window import MainWindow

    # Windows 任务栏默认按 exe 分组并显示 Python 图标；
    # 显式设置 AppUserModelID 后才会用我们自己的窗口图标。
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "LiteratureSearchAgent"
            )
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("文献检索需求翻译 Agent")
    app.setApplicationVersion("1.0.0")
    app.setWindowIcon(app_icon())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
