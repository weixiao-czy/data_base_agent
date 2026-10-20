"""验证居中列会撑满可用宽度（离屏运行）。

回归背景：换行 QLabel 的 sizeHint 很窄，旧布局里列不带 stretch，
导致整列缩到 ~380px、两侧全是弹簧留白。
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from PyQt6.QtWidgets import QApplication
from gui.chat_widget import ChatDisplay, _CONTENT_MAX_WIDTH

app = QApplication([])
display = ChatDisplay()
display.resize(1400, 800)
display.show()
display.add_message("这是一条比较长的回复。" * 40, is_user=False)
app.processEvents()

w = display.scroll_area.viewport().width()
row = display.messages_layout.itemAt(0).widget()
col_w = row.column.width()
print(f"视口宽度     : {w}")
print(f"内容列宽度   : {col_w}")
print(f"上限         : {_CONTENT_MAX_WIDTH}")

expect = min(_CONTENT_MAX_WIDTH, w)
assert col_w >= expect - 6, f"内容列应撑满到 {expect}px，实际 {col_w}px"
print(f"✓ 列宽 {col_w}px ≈ 期望 {expect}px，不再缩在中间")
print("全部通过")
