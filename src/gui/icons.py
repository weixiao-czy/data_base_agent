"""应用图标：源码运行读项目 assets/，打包后读 PyInstaller 解包目录"""

import os
import sys

from PyQt6.QtGui import QIcon


def resource_path(*parts: str) -> str:
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
    return os.path.join(base, *parts)


def app_icon() -> QIcon:
    icon = QIcon()
    for name in ("assets/icon.ico", "assets/icon.png"):
        path = resource_path(*name.split("/"))
        if os.path.exists(path):
            icon.addFile(path)
    return icon
