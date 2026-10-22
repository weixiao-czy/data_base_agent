"""GUI 树形图入口的离线集成测试：桩掉网络与 litmap，验证整条分支逻辑。"""
import os
import sys
import types

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

# ---- 桩掉 litmap，避免真实联网 ----
class _FakeNode:
    def __init__(self, label, papers):
        self.children = []
        self.label = label
        self.total_paper_count = papers

class _FakeMap:
    def __init__(self):
        a1 = _FakeNode("研究角度", 5)
        t = _FakeNode("语义匹配", 3)
        a1.children.append(t)
        self.root = _FakeNode("root", 8)
        self.root.children = [a1]
    def to_dict(self):
        return {"topic": "大模型语义检索", "stats": {"total_papers": 8, "total_topics": 1, "total_nodes": 3}}

fake_builder = types.ModuleType("litmap.builder")
fake_builder.LiteratureMapBuilder = lambda **kw: types.SimpleNamespace(build=lambda topic: _FakeMap())
fake_builder.summarize = lambda m: "主题：大模型语义检索\n文献：8 篇"
fake_render = types.ModuleType("litmap.render")
fake_render.to_html = lambda m: "<html/>"
fake_render.to_json = lambda m: "{}"
fake_render.to_markdown = lambda m: "# map"
fake_pkg = types.ModuleType("litmap")
fake_pkg.builder = fake_builder
fake_pkg.render = fake_render
sys.modules["litmap"] = fake_pkg
sys.modules["litmap.builder"] = fake_builder
sys.modules["litmap.render"] = fake_render

from gui.agent_worker import AgentWorker
from agent.state_machine import AgentState

w = AgentWorker({"use_mock_llm": True})
w.init_agent()
sm = w.agent["state_machine"]
sm.user_input = "大模型在文献检索中的语义理解能力"
sm.transition(AgentState.USER_CONFIRM)

emitted = {"resp": [], "status": [], "options": []}
w.agent_response = types.SimpleNamespace(emit=lambda t: emitted["resp"].append(t))
w.status = types.SimpleNamespace(emit=lambda t: emitted["status"].append(t))
w.options_ready = types.SimpleNamespace(
    emit=lambda opts, allow_skip: emitted["options"].append((opts, allow_skip))
)

print("=== 用例 1：输入 5 走树形图分支 ===")
w._handle_user_confirm("5")
all_resp = "\n".join(emitted["resp"])
assert "文献树形图已生成" in all_resp, all_resp
assert "8 篇" in all_resp, all_resp
assert "导图看完了" in all_resp, all_resp
assert "这个计划看起来如何？" not in all_resp, "导图后不应重复生成前的计划菜单"
assert emitted["options"][-1][1] is False
map_labels = [o["label"] for o in emitted["options"][-1][0]]
assert "重新生成树形图" in map_labels, map_labels
assert "确认，开始检索" in map_labels, map_labels
print("  通过：导图后给出专属摘要与菜单，不再重复计划确认文案")

print("=== 用例 2：菜单包含第 5 项 ===")
emitted["resp"].clear()
emitted["options"].clear()
w._handle_generate_plan()
plan_labels = [o["label"] for o in emitted["options"][-1][0]]
assert any("以树形图查看文献结构" in t for t in plan_labels), plan_labels
assert emitted["options"][-1][1] is False
print("  通过：需求卡菜单已列出选项 5")

print("=== 用例 3：产物文件已写出 ===")
from datetime import datetime
out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "maps")
files = sorted(os.listdir(out_dir))
assert files, "output/maps 应有产物"
print("  output/maps 下文件：", files[-3:])

print("=== 用例 4：状态机仍在 USER_CONFIRM ===")
assert sm.current_state == AgentState.USER_CONFIRM
print("  通过")

print("=== 用例 5：首轮点「跳过」直接生成计划 ===")
w2 = AgentWorker({"use_mock_llm": True})
w2.init_agent()
sm2 = w2.agent["state_machine"]
sm2.user_input = "大模型在文献检索中的语义理解能力"
sm2.transition(AgentState.CONFIRM_INTERPRETATION)
w2.agent["current_options"] = ["语义检索方向", "检索评估方向"]
resp2 = []
w2.agent_response = types.SimpleNamespace(emit=lambda t: resp2.append(t))
w2.status = types.SimpleNamespace(emit=lambda t: None)
w2.plan_card_ready = types.SimpleNamespace(emit=lambda d: None)
w2.options_ready = types.SimpleNamespace(emit=lambda o, s: None)
w2._handle_confirm("跳过")
assert sm2.current_state == AgentState.USER_CONFIRM, sm2.current_state
assert sm2.interpretation == "语义检索方向", sm2.interpretation
assert any("这个计划看起来如何" in t for t in resp2), resp2
print("  通过：跳过不会继续追问，直接进入计划确认")
print("\n全部通过")
