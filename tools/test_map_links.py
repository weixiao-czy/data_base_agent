"""验证导图内链接交给系统浏览器（真实窗口，测试中替换打开动作，不真的拉起浏览器）。"""
import os
import sys
import traceback

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from PyQt6.QtCore import QPoint, Qt, QTimer, QUrl
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication
from gui import map_panel

assert map_panel.HAS_WEBENGINE, "缺少 PyQt6-WebEngine"

app = QApplication(sys.argv)

opened = []
map_panel._open_in_system_browser = lambda url: opened.append(url)

panel = map_panel.MapPanel()
panel.resize(900, 600)
panel.show()

html_path = os.path.abspath("output/map_links_sample.html")
os.makedirs(os.path.dirname(html_path), exist_ok=True)
with open(html_path, "w", encoding="utf-8") as f:
    f.write(
        "<html><head><meta charset='utf-8'></head>"
        "<body style='margin:0;font:20px sans-serif'>"
        "<a id='blank' href='https://example.com/blank' target='_blank' "
        "style='position:absolute;left:40px;top:40px;padding:16px'>"
        "target blank</a>"
        "<a id='same' href='https://example.com/same' "
        "style='position:absolute;left:40px;top:120px;padding:16px'>"
        "same tab</a>"
        "</body></html>"
    )

panel.show_map(html_path, "链接测试")
view = panel._view
page = panel._page
results = {"ok": False}


def guarded(fn):
    """PyQt 槽里未捕获的异常会直接终止进程，这里统一转成失败退出。"""
    def wrapper(*args):
        try:
            fn(*args)
        except BaseException:
            traceback.print_exc()
            results["ok"] = False
            app.exit(1)
    return wrapper


@guarded
def verify_blank():
    urls = [u.toString() for u in opened]
    print("系统浏览器收到的链接:", urls)
    assert "https://example.com/same" in urls, "同页链接未交给系统浏览器"
    assert "https://example.com/blank" in urls, \
        "target=_blank 链接未交给系统浏览器"
    assert page.url() == QUrl.fromLocalFile(html_path), \
        "点击链接后内嵌导图被导航走了"
    print("内嵌导图仍停留在:", page.url().toString())
    results["ok"] = True
    app.quit()


@guarded
def click_blank(rect):
    x = int(rect["x"] + rect["width"] / 2)
    y = int(rect["y"] + rect["height"] / 2)
    print("点击 target=_blank 链接坐标:", x, y)
    widget = view.focusProxy() or view
    QTest.mouseClick(
        widget,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
        QPoint(x, y),
    )
    QTimer.singleShot(800, verify_blank)


@guarded
def check_same_tab():
    # 等价于用户点击无 target 的链接：acceptNavigationRequest 应拒绝当前页导航
    url = QUrl("https://example.com/same")
    allowed = page.acceptNavigationRequest(
        url, map_panel.QWebEnginePage.NavigationType.NavigationTypeLinkClicked, True
    )
    print("同页外链是否允许内嵌跳转:", allowed)
    assert allowed is False, "外链不应在内嵌页面内跳转"
    assert opened and opened[-1].toString() == url.toString(), \
        "同页外链未交给系统浏览器"
    page.runJavaScript(
        "(() => { const r = document.getElementById('blank').getBoundingClientRect();"
        " return {x:r.x, y:r.y, width:r.width, height:r.height}; })()",
        click_blank,
    )


@guarded
def on_load(ok):
    print("loadFinished:", ok)
    if not ok:
        raise RuntimeError("QWebEngineView 加载测试页面失败")
    QTimer.singleShot(300, check_same_tab)


view.loadFinished.connect(on_load)
QTimer.singleShot(20000, app.quit)
app.exec()
assert results.get("ok"), "导图链接外跳测试失败"
print("全部通过")
