"""
Agent 后台工作线程
队列驱动：所有 LLM / 网络调用都在子线程执行，GUI 永不阻塞
"""

import sys
import os
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

        msg = f"{restatement}\n\n你更接近哪个方向？\n"
        for i, opt in enumerate(options, 1):
            msg += f"{i}. {opt}\n"
        msg += "\n（输入数字选择，或补充说明）"
        self.agent_response.emit(msg)
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

        msg = f"（还剩 {remaining} 轮澄清机会）\n{question}\n\n（输入选项字母，或说「跳过」直接生成计划）"
        self.agent_response.emit(msg)
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
        self.agent_response.emit(
            "这个计划看起来如何？\n"
            "1. 确认，开始检索\n"
            "2. 需要调整（请说明）\n"
            "3. 重新生成\n"
            "4. 跳过检索\n"
            "5. 以树形图查看文献结构（发散检索 + 思维导图）"
        )

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
            max_queries=15,
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

        import webbrowser
        try:
            webbrowser.open("file://" + os.path.abspath(base + ".html"))
        except Exception:
            pass

        # 停留在 USER_CONFIRM，用户看完导图还能继续选「确认，开始检索」
        self.agent_response.emit(
            "文献树形图已生成，并已在浏览器中打开。\n\n"
            + summarize(litmap)
            + f"\n\n[已保存] 导图：{base}.html\n"
              f"[已保存] 大纲：{base}.md\n"
              f"[已保存] 数据：{base}.json\n\n"
              "这个计划看起来如何？\n"
              "1. 确认，开始检索\n"
              "2. 需要调整（请说明）\n"
              "3. 重新生成\n"
              "4. 跳过检索\n"
              "5. 再生成一份树形图"
        )

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
            sm.transition(AgentState.CALL_SEARCH)
            self._handle_search()

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
        self.agent_response.emit(
            "接下来你想：\n"
            "1. 细化检索（开始新对话）\n"
            "2. 结束"
        )

    def _handle_present(self, text: str):
        if text in ("1", "细化"):
            self.agent["state_machine"].reset()
            self.agent_response.emit("请描述新的研究兴趣：")
        else:
            self.agent_response.emit("再见！")
