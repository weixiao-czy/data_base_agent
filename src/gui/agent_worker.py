"""
Agent 后台工作线程
队列驱动：所有 LLM / 网络调用都在子线程执行，GUI 永不阻塞
"""

import sys
import os
import re
import queue
from PyQt6.QtCore import QThread, pyqtSignal

# 确保 src 在 path 中
_src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from agent.state_machine import StateMachine, AgentState
from agent.clarifier import Clarifier
from agent.plan_card import PlanCardGenerator
from search.fallback_provider import FallbackSearchProvider
from search.real_search import RealSearchProvider
from search.scimaster_mcp import SciMasterMCPProvider
from search.scimaster_cli import SciMasterCLIProvider
from llm.client import OpenAIClient, MockLLMClient


# ---------------------------------------------------------------- 选项拆分
# 命令行版让用户敲 "1" / "A"，GUI 版要把同样的选项渲染成按钮。
# 这里只做「识别 + 拆分」，不改下发给 Agent 的取值语义：返回的 key 仍是
# "1" / "A"，点按钮回传后与手敲完全等价，状态机无需感知输入方式。

_OPT_LINE_RE = re.compile(r"^\s*([A-Za-z]|\d{1,2})\s*[.、．)）]\s*(\S.*)$")
_MARKER_RE = re.compile(r"^\s*[\[【]\s*(说明|问题|选项|要求|注意)\s*[\]】]\s*[：:]?\s*")
_HINT_KEYS = ("输入", "可选", "也可以", "直接")


def _is_hint_line(line: str) -> bool:
    """括号包裹的提示句（如「（输入数字选择，或补充说明）」）不进正文"""
    s = line.strip()
    if not (s.startswith("（") or s.startswith("(")):
        return False
    return any(k in s for k in _HINT_KEYS)


def split_options(text: str):
    """
    把带编号/字母的选项行从正文里拆出来

    Args:
        text: 形如 "你更接近哪个方向？\\n1. 理论研究\\n2. 应用实践" 或
              "[说明]\\n……\\n[选项]\\nA. 交互设计\\nB. 用户体验" 的文本

    Returns:
        (body, options)
            body:    去掉选项行与提示行后的正文
            options: [{"key": "1", "label": "理论研究"}, ...]
    """
    body_lines = []
    options = []

    for raw in text.splitlines():
        line = _MARKER_RE.sub("", raw).strip()
        if not line or _is_hint_line(line):
            continue
        m = _OPT_LINE_RE.match(line)
        if m:
            options.append({"key": m.group(1), "label": m.group(2).strip()})
        else:
            body_lines.append(line)

    body = re.sub(r"\n{3,}", "\n\n", "\n".join(body_lines)).strip()
    return body, options


class AgentWorker(QThread):
    """
    在后台线程中运行 Agent 对话逻辑。

    信号：
        agent_response(text)  — Agent 的文本回复
        plan_card_ready(dict) — 需求翻译卡生成完毕
        search_results(list)  — 检索结果
        status(str)           — 进行中的状态提示（如"正在检索…"）
        round_info(str)       — 剩余轮次提示
        finished()            — 当前轮处理完毕
        error(str)            — 错误信息
    """

    agent_response = pyqtSignal(str)
    plan_card_ready = pyqtSignal(dict)
    search_results = pyqtSignal(list)
    status = pyqtSignal(str)
    round_info = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    # 可点击选项：[{"key": "1", "label": "确认，开始检索", "needs_input": False}, ...]
    # key 与命令行里手敲的内容一致，needs_input=True 表示该项需要用户补充说明
    options_ready = pyqtSignal(list)
    # 文献地图生成完毕：(html 路径, 主题)。由主窗口决定内嵌展示还是外部打开
    map_ready = pyqtSignal(str, str)

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = dict(config or {})
        self.agent = None
        self._queue = queue.Queue()
        self._running = True
        self._llm_init_error = ""
        self._warned_keys = set()

    def _warn_once(self, key: str, text: str):
        """同一类警告只播报一次，避免每轮追问都刷屏"""
        if key in self._warned_keys:
            return
        self._warned_keys.add(key)
        self.agent_response.emit(text)

    def _on_llm_error(self, msg: str):
        """Clarifier 降级回调：把 LLM 调用失败的原因显示到对话里"""
        self._warn_once("llm-call", f"⚠ {msg}")

    # ------------------------------------------------ 主线程调用（线程安全）

    def submit(self, text: str):
        """提交一条用户消息（入队，由工作线程处理）"""
        self._queue.put(("input", text))

    def submit_reset(self):
        """重置 Agent 状态（新对话 / 切换对话时调用）"""
        self._queue.put(("reset", None))

    def update_config(self, config: dict):
        """更新配置并重置 Agent"""
        self.config = dict(config or {})
        self.submit_reset()

    def stop(self):
        """停止工作线程"""
        self._running = False
        self._queue.put(("stop", None))

    # ------------------------------------------------ 工作线程主循环

    def run(self):
        while self._running:
            try:
                kind, payload = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue
            if kind == "stop":
                break
            if kind == "reset":
                self.agent = None
                continue
            if kind == "input":
                self._process(payload)

    def _cfg(self, key: str):
        """读配置项：空字符串归一为 None。

        设置对话框保存时，没填的字段会以 "" 存进 config.json。
        OpenAIClient 用 `is None` 区分「没传」和「显式传空」——
        "" 会挡住 .env 里的真实密钥，表现为「.env 配好了却仍走模拟模式」。
        """
        v = self.config.get(key)
        if isinstance(v, str):
            v = v.strip()
        return v or None

    def init_agent(self):
        """初始化 Agent（在工作线程中调用）"""
        max_rounds = self.config.get("max_rounds", 10)
        use_mock_llm = self.config.get("use_mock_llm", False)

        state_machine = StateMachine(max_rounds=max_rounds)

        self._llm_init_error = ""
        if use_mock_llm:
            llm_client = MockLLMClient()
        else:
            try:
                llm_client = OpenAIClient(
                    api_key=self._cfg("openai_api_key"),
                    base_url=self._cfg("openai_base_url"),
                    model=self._cfg("openai_model"),
                )
            except Exception as e:
                # 不能再静默降级：打包成 exe 后是窗口程序，没有控制台，
                # 用户看到的只是模板式回复，完全不知道模型没连上。
                # 把原因记下来，稍后显示到对话里。
                llm_client = MockLLMClient()
                self._llm_init_error = str(e)

        clarifier = Clarifier(llm_client=llm_client, on_error=self._on_llm_error)
        plan_card_gen = PlanCardGenerator(llm_client=llm_client)

        providers = []
        mcp = SciMasterMCPProvider(
            api_key=self._cfg("scimaster_api_key"),
            base_url=self._cfg("scimaster_base_url"),
        )
        if mcp.is_available():
            providers.append(mcp)
        real = RealSearchProvider()
        if real.is_available():
            providers.append(real)
        cli = SciMasterCLIProvider()
        if cli.is_available():
            providers.append(cli)

        search_provider = FallbackSearchProvider(providers) if providers else None

        self.agent = {
            "state_machine": state_machine,
            "clarifier": clarifier,
            "plan_card_gen": plan_card_gen,
            "search_provider": search_provider,
            "current_options": [],
            "search_results": [],
        }

    def _process(self, user_text: str):
        """处理一条用户消息（工作线程内执行）"""
        if self.agent is None:
            self.status.emit("正在初始化…")
            self.init_agent()
            if self._llm_init_error:
                self.agent_response.emit(
                    "⚠ 未能启用大模型，当前为「模拟模式」，回复是固定模板。\n\n"
                    f"原因：{self._llm_init_error}\n\n"
                    "解决方法：点击左下角「设置」→ LLM 配置，填入 API Key 后保存，"
                    "立即生效、无需重启。留空的项会自动读取 .env（源码运行时）。"
                )

        sm = self.agent["state_machine"]

        try:
            state = sm.current_state

            if state == AgentState.IDLE:
                self._handle_idle(user_text)
            elif state == AgentState.RESTATE:
                self._handle_restate()
            elif state == AgentState.CONFIRM_INTERPRETATION:
                self._handle_confirm(user_text)
            elif state == AgentState.PROBE_KEY_FORK:
                self._handle_probe(user_text)
            elif state == AgentState.GENERATE_PLAN_CARD:
                self._handle_generate_plan()
            elif state == AgentState.USER_CONFIRM:
                self._handle_user_confirm(user_text)
            elif state == AgentState.CALL_SEARCH:
                self._handle_search()
            elif state == AgentState.PRESENT_RESULTS:
                self._handle_present(user_text)
            else:
                self.agent_response.emit("未知状态，请重新开始。")

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit()

    # ------------------------------------------------ 各状态处理

    def _handle_idle(self, text: str):
        sm = self.agent["state_machine"]

        if text.lower() in ("跳过", "skip"):
            sm.interpretation = text
            sm.transition(AgentState.GENERATE_PLAN_CARD)
            self._handle_generate_plan()
            return

        sm.user_input = text
        sm.add_to_history("user", text)
        sm.transition(AgentState.RESTATE)
        self._handle_restate()

    def _handle_restate(self):
        sm = self.agent["state_machine"]
        clarifier = self.agent["clarifier"]

        self.status.emit("正在理解你的需求…")
        result = clarifier.restate(sm.user_input)
        restatement = result["restatement"]
        options = result["options"]
        self.agent["current_options"] = options

        sm.add_to_history("agent", restatement, {"options": options})

        # 复述文案有的来源已经自带问句（Mock 模板、大模型都可能带），别再补一遍
        body = restatement.strip()
        if not body.endswith(("？", "?")):
            body = f"{body}\n\n你更接近哪个方向？"
        self.agent_response.emit(body)
        self.options_ready.emit(
            [{"key": str(i), "label": opt} for i, opt in enumerate(options, 1)]
        )
        sm.transition(AgentState.CONFIRM_INTERPRETATION)

    def _handle_confirm(self, text: str):
        sm = self.agent["state_machine"]
        clarifier = self.agent["clarifier"]
        options = self.agent["current_options"]

        self.status.emit("正在分析…")
        if text.lower() in ("跳过", "skip"):
            interpretation = options[0] if options else sm.user_input
        else:
            interpretation = clarifier.confirm_interpretation(text, options)

        sm.interpretation = interpretation
        sm.add_to_history("user", text)
        sm.add_to_history("agent", f"确认方向: {interpretation}")

        if sm.can_clarify():
            sm.transition(AgentState.PROBE_KEY_FORK)
            self._do_probe()
        else:
            sm.transition(AgentState.GENERATE_PLAN_CARD)
            self._handle_generate_plan()

    def _do_probe(self):
        sm = self.agent["state_machine"]
        clarifier = self.agent["clarifier"]

        self.status.emit("正在生成澄清问题…")
        context = {
            "interpretation": sm.interpretation,
            "history": sm.clarification_history,
            "current_round": sm.current_round,
            "max_rounds": sm.max_rounds,
        }
        question = clarifier.probe_key_fork(context)
        remaining = sm.get_remaining_rounds()

        sm.add_to_history("agent", question)
        sm.increment_round()

        # 追问文本里带着 A/B/C 选项（LLM 模式还带 [说明]/[问题]/[选项] 标记），
        # 拆成「正文 + 选项按钮」两段，正文照旧显示，选项交给界面渲染
        body, options = split_options(question)
        head = f"（还剩 {remaining} 轮澄清机会）"
        self.agent_response.emit(f"{head}\n\n{body}" if body else head)
        if options:
            self.options_ready.emit(options)
        self.round_info.emit(f"剩余澄清轮次：{remaining}")
        sm.transition(AgentState.PROBE_KEY_FORK)

    def _handle_probe(self, text: str):
        sm = self.agent["state_machine"]
        sm.add_to_history("user", text)

        if text.lower() in ("跳过", "skip"):
            sm.transition(AgentState.GENERATE_PLAN_CARD)
            self._handle_generate_plan()
            return

        if sm.can_clarify():
            self._do_probe()
        else:
            sm.transition(AgentState.GENERATE_PLAN_CARD)
            self._handle_generate_plan()

    def _handle_generate_plan(self):
        sm = self.agent["state_machine"]
        plan_card_gen = self.agent["plan_card_gen"]

        self.status.emit("正在生成需求翻译卡…")

        plan_card = plan_card_gen.generate(
            sm.clarification_history,
            sm.user_input,
            sm.interpretation,
        )
        sm.plan_card = plan_card

        card_dict = plan_card.to_dict()
        self.plan_card_ready.emit(card_dict)

        sm.transition(AgentState.USER_CONFIRM)
        self._emit_plan_actions()

    # 计划确认阶段的操作项。needs_input=True 的项点下去不直接下发，
    # 而是把焦点交回输入框，让用户先把「要调整什么」说完。
    PLAN_ACTIONS = [
        {"key": "1", "label": "确认，开始检索"},
        {"key": "2", "label": "需要调整（请说明）", "needs_input": True},
        {"key": "3", "label": "重新生成"},
        {"key": "4", "label": "跳过检索"},
        {"key": "5", "label": "以树形图查看文献结构（发散检索 + 思维导图）"},
    ]

    def _emit_plan_actions(self):
        """计划确认菜单：正文与选项分开下发，选项由界面渲染成按钮"""
        self.agent_response.emit("这个计划看起来如何？")
        self.options_ready.emit([dict(o) for o in self.PLAN_ACTIONS])

    def _view_literature_tree(self):
        """以树形图查看文献结构（与命令行版同一逻辑，接在澄清结论之后）"""
        sm = self.agent["state_machine"]

        # 检索主题优先级与 CLI 版一致：原始输入 > 解读结论 > 翻译卡关键词。
        # 多轮澄清后 interpretation 常收敛成「理论研究」这类词，直接用会跑偏。
        candidates = [sm.user_input, sm.interpretation]
        plan = sm.plan_card
        if plan:
            try:
                candidates.append(" ".join(plan.suggested_keywords.get("primary", [])[:3]))
            except Exception:
                pass

        vague = {"理论研究", "实践应用", "不确定", "系统实现", "理论分析", "实验验证"}
        topic = ""
        for c in candidates:
            c = (c or "").strip()
            if c and c not in vague:
                topic = c
                break
        if not topic:
            self.agent_response.emit("没有得到有效的研究主题，请先描述研究兴趣。")
            return

        try:
            from litmap.builder import LiteratureMapBuilder, summarize
            from litmap.render import to_html, to_json, to_markdown
        except ImportError as e:
            self.agent_response.emit(f"⚠ 文献地图模块不可用：{e}")
            return

        llm = self.agent["clarifier"].llm_client
        if isinstance(llm, MockLLMClient):
            llm = None  # 模拟模式不传给 builder，让扩展器回落到规则模板

        self.status.emit(f"正在构建文献树形图：{topic}（约 1 分钟）…")
        builder = LiteratureMapBuilder(
            provider=self.agent["search_provider"],
            llm_client=llm,
            seed_limit=12,
            per_topic=3,
            topics_per_aspect=3,
            max_queries=20,
            progress=lambda msg: self.status.emit(msg),
        )
        try:
            litmap = builder.build(topic)
        except Exception as e:
            self.agent_response.emit(f"⚠ 构建文献地图失败：{e}")
            return

        # 产物目录：源码运行放项目根 output/maps；打包后放 exe 同级 output/maps
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
        out_dir = os.path.join(base_dir, "output", "maps")
        os.makedirs(out_dir, exist_ok=True)

        from datetime import datetime
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = "".join(c if (c.isalnum() or c in "-_") else "_" for c in topic)[:40]
        base = os.path.join(out_dir, f"{slug}_{stamp}")

        try:
            with open(base + ".html", "w", encoding="utf-8") as f:
                f.write(to_html(litmap))
            with open(base + ".md", "w", encoding="utf-8") as f:
                f.write(to_markdown(litmap))
            with open(base + ".json", "w", encoding="utf-8") as f:
                f.write(to_json(litmap))
        except OSError as e:
            self.agent_response.emit(f"⚠ 树形图已生成但写文件失败：{e}")
            return

        # 导图交给主窗口内嵌展示；面板不可用时主窗口会退回外部浏览器
        self.map_ready.emit(base + ".html", topic)

        # 停留在 USER_CONFIRM，用户看完导图还能继续选「确认，开始检索」
        self.agent_response.emit(
            "文献树形图已生成，已在窗口内打开（点右上角「返回对话」可切回）。\n\n"
            + summarize(litmap)
            + f"\n\n[已保存] 导图：{base}.html\n"
              f"[已保存] 大纲：{base}.md\n"
              f"[已保存] 数据：{base}.json"
        )
        self._emit_plan_actions()

    def _handle_user_confirm(self, text: str):
        sm = self.agent["state_machine"]

        if text in ("1", "确认"):
            sm.transition(AgentState.CALL_SEARCH)
            self._handle_search()
        elif text in ("2", "调整"):
            sm.add_to_history("user", f"调整: {text}")
            sm.transition(AgentState.GENERATE_PLAN_CARD)
            self._handle_generate_plan()
        elif text in ("3", "重新生成"):
            sm.transition(AgentState.GENERATE_PLAN_CARD)
            self._handle_generate_plan()
        elif text in ("4", "跳过"):
            self.agent_response.emit("好的，检索已跳过。你可以开始新的对话。")
            sm.reset()
        elif text in ("5", "树形图", "导图", "map"):
            self._view_literature_tree()
        else:
            # 走「其他（自己输入）」时，用户打的字就是调整说明：
            # 记进历史后重新生成翻译卡，而不是当成误操作直接去检索。
            sm.add_to_history("user", f"调整: {text}")
            sm.transition(AgentState.GENERATE_PLAN_CARD)
            self._handle_generate_plan()

    def _handle_search(self):
        sm = self.agent["state_machine"]
        search_provider = self.agent["search_provider"]

        if not search_provider:
            self.agent_response.emit("检索服务不可用，请手动使用需求翻译卡中的查询。")
            sm.transition(AgentState.PRESENT_RESULTS)
            return

        queries = sm.plan_card.search_plan["suggested_queries"]
        if not queries:
            self.agent_response.emit("没有可用的检索查询。")
            sm.transition(AgentState.PRESENT_RESULTS)
            return

        primary_query = queries[0]
        self.status.emit(f"正在检索：{primary_query[:40]}…")

        limit = int(self.config.get("search_default_limit", 10))
        results = search_provider.search(primary_query, limit=limit)

        if results:
            self.agent["search_results"] = results
            sm.add_to_history("agent", f"检索到 {len(results)} 篇论文")
            self.search_results.emit(results)
        else:
            self.agent["search_results"] = []
            self.agent_response.emit("未找到相关论文。")

        sm.transition(AgentState.PRESENT_RESULTS)
        self._handle_present_results()

    def _handle_present_results(self):
        self.agent_response.emit("接下来你想：")
        self.options_ready.emit([
            {"key": "1", "label": "细化检索（开始新对话）"},
            {"key": "2", "label": "结束"},
        ])

    def _handle_present(self, text: str):
        if text in ("1", "细化"):
            self.agent["state_machine"].reset()
            self.agent_response.emit("请描述新的研究兴趣：")
        else:
            self.agent_response.emit("再见！")
