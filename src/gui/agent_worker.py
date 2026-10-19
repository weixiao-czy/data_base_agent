"""
Agent 后台工作线程
在 QThread 中运行澄清对话流程，通过信号与 GUI 通信
"""

import sys
import os
import json
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
from presentation.render_results import render_results, render_plan_card


class AgentWorker(QThread):
    """
    在后台线程中运行 Agent 对话逻辑。

    信号：
        agent_response(text)  — Agent 的文本回复
        plan_card_ready(dict) — 需求翻译卡生成完毕
        search_results(list)  — 检索结果
        round_info(str)       — 剩余轮次提示
        finished()            — 当前轮处理完毕
        error(str)            — 错误信息
    """

    agent_response = pyqtSignal(str)
    plan_card_ready = pyqtSignal(dict)
    search_results = pyqtSignal(list)
    round_info = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.agent = None
        self._pending_input = None
        self._input_event = None

    def set_user_input(self, text: str):
        """主线程调用：提供用户输入"""
        self._pending_input = text

    def init_agent(self):
        """初始化 Agent（在 run 中调用）"""
        max_rounds = self.config.get("max_rounds", 10)
        use_mock_llm = self.config.get("use_mock_llm", False)

        state_machine = StateMachine(max_rounds=max_rounds)

        if use_mock_llm:
            llm_client = MockLLMClient()
        else:
            try:
                llm_client = OpenAIClient(
                    api_key=self.config.get("openai_api_key"),
                    base_url=self.config.get("openai_base_url"),
                    model=self.config.get("openai_model"),
                )
            except Exception:
                llm_client = MockLLMClient()

        clarifier = Clarifier(llm_client=llm_client)
        plan_card_gen = PlanCardGenerator(llm_client=llm_client)

        # 检索提供者
        providers = []
        mcp = SciMasterMCPProvider(
            api_key=self.config.get("scimaster_api_key"),
            base_url=self.config.get("scimaster_base_url"),
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

    def run(self):
        """等待用户输入并处理（由主线程通过 set_user_input 触发）"""
        # 初始化在第一次 process 时做
        pass

    def process(self, user_text: str):
        """
        处理一条用户消息，根据当前状态执行对应逻辑。
        由主线程调用。
        """
        if self.agent is None:
            self.init_agent()

        sm = self.agent["state_machine"]
        clarifier = self.agent["clarifier"]
        plan_card_gen = self.agent["plan_card_gen"]
        search_provider = self.agent["search_provider"]

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

    def _handle_idle(self, text: str):
        sm = self.agent["state_machine"]
        clarifier = self.agent["clarifier"]

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

        self.agent_response.emit("\n正在生成需求翻译卡...")

        plan_card = plan_card_gen.generate(
            sm.clarification_history,
            sm.user_input,
            sm.interpretation,
        )
        sm.plan_card = plan_card

        card_dict = plan_card.to_dict()
        rendered = render_plan_card(card_dict)
        self.agent_response.emit(rendered)
        self.plan_card_ready.emit(card_dict)

        sm.transition(AgentState.USER_CONFIRM)
        self.agent_response.emit(
            "\n这个计划看起来如何？\n"
            "1. 确认，开始检索\n"
            "2. 需要调整（请说明）\n"
            "3. 重新生成\n"
            "4. 跳过检索"
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
            self.agent_response.emit("\n好的，检索已跳过。你可以开始新的对话。")
            sm.reset()
        else:
            sm.transition(AgentState.CALL_SEARCH)
            self._handle_search()

    def _handle_search(self):
        sm = self.agent["state_machine"]
        search_provider = self.agent["search_provider"]

        if not search_provider:
            self.agent_response.emit("\n检索服务不可用，请手动使用需求翻译卡中的查询。")
            sm.transition(AgentState.PRESENT_RESULTS)
            return

        self.agent_response.emit("\n正在检索...")

        queries = sm.plan_card.search_plan["suggested_queries"]
        if not queries:
            self.agent_response.emit("\n没有可用的检索查询。")
            sm.transition(AgentState.PRESENT_RESULTS)
            return

        primary_query = queries[0]
        self.agent_response.emit(f"使用查询: {primary_query}")

        results = search_provider.search(primary_query, limit=10)

        if results:
            self.agent["search_results"] = results
            sm.add_to_history("agent", f"检索到 {len(results)} 篇论文")
            self.search_results.emit(results)
        else:
            self.agent["search_results"] = []
            self.agent_response.emit("\n未找到相关论文。")

        sm.transition(AgentState.PRESENT_RESULTS)
        self._handle_present_results()

    def _handle_present_results(self):
        results = self.agent.get("search_results", [])
        if results:
            rendered = render_results(results)
            self.agent_response.emit(rendered)
        self.agent_response.emit(
            "\n接下来你想：\n"
            "1. 细化检索（开始新对话）\n"
            "2. 结束"
        )

    def _handle_present(self, text: str):
        if text in ("1", "细化"):
            self.agent["state_machine"].reset()
            self.agent_response.emit("\n请描述新的研究兴趣：")
        else:
            self.agent_response.emit("\n再见！")

    def reset(self):
        """重置 Agent 状态"""
        if self.agent and self.agent.get("state_machine"):
            self.agent["state_machine"].reset()
        self.agent = None
