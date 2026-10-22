"""验证澄清选项组的「跳过」按钮：浅红样式、独立回调、与普通选项区分。"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from PyQt6.QtWidgets import QApplication, QPushButton
from gui.chat_widget import ChatDisplay, OptionButtons
from gui.styles import GLOBAL_QSS, CHAT_QSS, MESSAGE_QSS

app = QApplication([])
app.setStyleSheet(GLOBAL_QSS + CHAT_QSS + MESSAGE_QSS)

display = ChatDisplay()
display.resize(900, 620)
display.show()
display.add_message("你更接近哪个方向？", is_user=False)
display.add_options([
    {"key": "1", "label": "理论研究"},
    {"key": "2", "label": "应用实践"},
    {"key": "3", "label": "系统实现"},
], show_skip=True)
app.processEvents()

block = display._options
assert isinstance(block, OptionButtons)
skip = block.findChild(QPushButton, "option_btn_skip")
assert skip is not None, "澄清选项组应包含独立的跳过按钮"
assert skip.text() == OptionButtons.SKIP_LABEL, skip.text()
print(f"✓ 跳过按钮已渲染：{skip.text()}")

picked = []
block.option_clicked.connect(lambda k, l: picked.append((k, l)))
skip.click()
assert picked == [(OptionButtons.SKIP_KEY, OptionButtons.SKIP_LABEL)], picked
assert block._locked, "点跳过应锁住整组选项"
print(f"✓ 点击回调：{picked[0]}")

# 即使模型没有给出选项，也能只渲染「跳过 + 其他」让用户脱身
display.add_options([], show_skip=True)
app.processEvents()
assert display._options is not None
assert display._options.findChild(QPushButton, "option_btn_skip") is not None
print("✓ 无选项时仍渲染跳过入口")

out = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "output", "gui_options_preview.png",
)
os.makedirs(os.path.dirname(out), exist_ok=True)
display.grab().save(out)
print(f"✓ 预览截图：{out}")
print("全部通过")
