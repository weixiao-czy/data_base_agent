"""验证文献导图能在 QtWebEngine 内嵌渲染（真实窗口，截图供人工检查）。"""
import glob
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from gui.map_panel import MapPanel, HAS_WEBENGINE

print("HAS_WEBENGINE:", HAS_WEBENGINE)
assert HAS_WEBENGINE, "缺少 PyQt6-WebEngine，导图会退回浏览器"

# QWebEngine 需要非空 argv 才能初始化 Chromium 命令行；
# 真实入口 gui_launcher 传的就是 sys.argv。
app = QApplication(sys.argv)
panel = MapPanel()
panel.resize(1100, 800)
panel.show()

html = sys.argv[1] if len(sys.argv) > 1 else ""
if not html:
    hits = glob.glob("dist/output/maps/*.html") or glob.glob("output/maps/*.html")
    html = hits[-1] if hits else ""
if not html or not os.path.exists(html):
    # 没有现成导图时用最小 HTML 验证内嵌链路本身
    html = os.path.abspath("output/map_embed_sample.html")
    os.makedirs(os.path.dirname(html), exist_ok=True)
    with open(html, "w", encoding="utf-8") as f:
        f.write("<html><body><h1>文献地图内嵌测试</h1>"
                "<p>QtWebEngine 正常渲染本地 HTML。</p></body></html>")
panel.show_map(os.path.abspath(html), "内嵌导图测试")

result = {"ok": None}


def done(ok):
    result["ok"] = ok
    print("loadFinished:", ok)
    QTimer.singleShot(1200, snap)


def snap():
    out = os.path.abspath("output/map_embed_preview.png")
    panel.grab().save(out)
    print("saved:", out)
    app.quit()


panel._view.loadFinished.connect(done)
QTimer.singleShot(20000, app.quit)
app.exec()
assert result["ok"] is True, "QWebEngineView 加载本地导图失败"
print("全部通过")
