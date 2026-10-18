"""
主程序入口：文献检索需求翻译 Agent
"""

import sys
from agent.state_machine import StateMachine, AgentState
from agent.clarifier import Clarifier
from agent.plan_card import PlanCardGenerator
from search.scimaster_mcp import SciMasterMCPProvider
from search.scimaster_cli import SciMasterCLIProvider
from presentation.render_results import render_results, render_plan_card


class LiteratureSearchAgent:
    """文献检索需求翻译 Agent"""
    
    def __init__(self, max_rounds: int = 3):
        self.state_machine = StateMachine(max_rounds=max_rounds)
        self.clarifier = Clarifier()
        self.plan_card_generator = PlanCardGenerator()
        
        # 初始化检索提供者（MCP 优先，CLI 降级）
        self.search_provider = self._init_search_provider()
    
    def _init_search_provider(self):
        """初始化检索提供者"""
        mcp_provider = SciMasterMCPProvider()
        if mcp_provider.is_available():
            print("使用 MCP 模式")
            return mcp_provider
        
        cli_provider = SciMasterCLIProvider()
        if cli_provider.is_available():
            print("使用 CLI 降级模式")
            return cli_provider
        
        print("警告: 检索服务不可用，将只生成检索计划")
        return None
    
    def run(self):
        """运行 Agent 主循环"""
        print("="*50)
        print("文献检索需求翻译 Agent")
        print("="*50)
        print("\n我会帮你把模糊的研究兴趣翻译成可检索的关键词。")
        print("最多需要 3 轮对话，你也可以随时说「跳过」直接生成检索计划。")
        print("\n请描述你的研究兴趣（输入 'quit' 退出）：")
        
        while True:
            try:
                # 根据当前状态处理
                if self.state_machine.current_state == AgentState.IDLE:
                    self._handle_idle()
                elif self.state_machine.current_state == AgentState.RESTATE:
                    self._handle_restate()
                elif self.state_machine.current_state == AgentState.CONFIRM_INTERPRETATION:
                    self._handle_confirm()
                elif self.state_machine.current_state == AgentState.PROBE_KEY_FORK:
                    self._handle_probe()
                elif self.state_machine.current_state == AgentState.GENERATE_PLAN_CARD:
                    self._handle_generate_plan()
                elif self.state_machine.current_state == AgentState.USER_CONFIRM:
                    self._handle_user_confirm()
                elif self.state_machine.current_state == AgentState.CALL_SEARCH:
                    self._handle_search()
                elif self.state_machine.current_state == AgentState.PRESENT_RESULTS:
                    self._handle_present()
                elif self.state_machine.current_state == AgentState.FALLBACK:
                    self._handle_fallback()
                
            except KeyboardInterrupt:
                print("\n\n程序中断")
                break
            except Exception as e:
                print(f"\n错误: {e}")
                import traceback
                traceback.print_exc()
    
    def _handle_idle(self):
        """处理初始状态"""
        user_input = input("\n> ").strip()
        
        if user_input.lower() == 'quit':
            print("再见！")
            sys.exit(0)
        
        if not user_input:
            return
        
        if user_input.lower() in ['跳过', 'skip']:
            # 直接生成宽泛计划
            self.state_machine.interpretation = user_input
            self.state_machine.transition(AgentState.GENERATE_PLAN_CARD)
            return
        
        # 保存用户输入
        self.state_machine.user_input = user_input
        self.state_machine.add_to_history("user", user_input)
        
        # 转换到复述状态
        self.state_machine.transition(AgentState.RESTATE)
    
    def _handle_restate(self):
        """处理复述状态"""
        result = self.clarifier.restate(self.state_machine.user_input)
        
        print(f"\n{result['restatement']}")
        print("\n你更接近哪个方向？")
        for i, option in enumerate(result['options'], 1):
            print(f"{i}. {option}")
        print("（输入数字选择，或输入其他内容补充说明）")
        
        # 保存选项供下一步使用
        self.state_machine.add_to_history("agent", result['restatement'], 
                                         {"options": result['options']})
        
        # 临时保存选项
        self._current_options = result['options']
        
        self.state_machine.transition(AgentState.CONFIRM_INTERPRETATION)
    
    def _handle_confirm(self):
        """处理确认状态"""
        user_choice = input("\n> ").strip()
        
        if user_choice.lower() == 'quit':
            print("再见！")
            sys.exit(0)
        
        if user_choice.lower() in ['跳过', 'skip']:
            # 使用第一个选项
            interpretation = self._current_options[0] if self._current_options else self.state_machine.user_input
        else:
            interpretation = self.clarifier.confirm_interpretation(
                user_choice, self._current_options
            )
        
        self.state_machine.interpretation = interpretation
        self.state_machine.add_to_history("user", user_choice)
        self.state_machine.add_to_history("agent", f"确认方向: {interpretation}")
        
        # 检查是否需要继续追问
        if self.state_machine.can_clarify():
            self.state_machine.transition(AgentState.PROBE_KEY_FORK)
        else:
            self.state_machine.transition(AgentState.GENERATE_PLAN_CARD)
    
    def _handle_probe(self):
        """处理分叉追问状态"""
        context = {
            "interpretation": self.state_machine.interpretation,
            "history": self.state_machine.clarification_history
        }
        
        question = self.clarifier.probe_key_fork(context)
        
        remaining = self.state_machine.get_remaining_rounds()
        print(f"\n（还剩 {remaining} 轮澄清机会）")
        print(question)
        print("（输入选项字母，或说「跳过」直接生成计划）")
        
        self.state_machine.add_to_history("agent", question)
        self.state_machine.increment_round()
        
        user_answer = input("\n> ").strip()
        
        if user_answer.lower() == 'quit':
            print("再见！")
            sys.exit(0)
        
        if user_answer.lower() in ['跳过', 'skip']:
            # 直接生成计划
            self.state_machine.transition(AgentState.GENERATE_PLAN_CARD)
            return
        
        self.state_machine.add_to_history("user", user_answer)
        
        # 检查是否还能继续追问
        if self.state_machine.can_clarify():
            # 继续追问或生成计划
            self.state_machine.transition(AgentState.GENERATE_PLAN_CARD)
        else:
            self.state_machine.transition(AgentState.GENERATE_PLAN_CARD)
    
    def _handle_generate_plan(self):
        """处理生成需求翻译卡状态"""
        print("\n正在生成需求翻译卡...")
        
        plan_card = self.plan_card_generator.generate(
            self.state_machine.clarification_history,
            self.state_machine.user_input,
            self.state_machine.interpretation
        )
        
        self.state_machine.plan_card = plan_card
        
        # 展示需求翻译卡
        print(render_plan_card(plan_card.to_dict()))
        
        print("\n这个计划看起来如何？")
        print("1. 确认，开始检索")
        print("2. 需要调整")
        print("3. 重新生成")
        
        self.state_machine.transition(AgentState.USER_CONFIRM)
    
    def _handle_user_confirm(self):
        """处理用户确认状态"""
        choice = input("\n> ").strip()
        
        if choice in ['1', '确认']:
            self.state_machine.transition(AgentState.CALL_SEARCH)
        elif choice in ['2', '调整']:
            print("请告诉我需要调整什么：")
            adjustment = input("\n> ").strip()
            self.state_machine.add_to_history("user", f"调整: {adjustment}")
            # 重新生成
            self.state_machine.transition(AgentState.GENERATE_PLAN_CARD)
        elif choice in ['3', '重新生成']:
            self.state_machine.transition(AgentState.GENERATE_PLAN_CARD)
        else:
            print("无效选择，默认开始检索")
            self.state_machine.transition(AgentState.CALL_SEARCH)
    
    def _handle_search(self):
        """处理检索状态"""
        if not self.search_provider:
            print("\n检索服务不可用，请手动使用以下查询：")
            for query in self.state_machine.plan_card.search_plan['suggested_queries']:
                print(f"  - {query}")
            self.state_machine.transition(AgentState.PRESENT_RESULTS)
            return
        
        print("\n正在检索...")
        
        # 使用第一个建议查询
        queries = self.state_machine.plan_card.search_plan['suggested_queries']
        if queries:
            results = self.search_provider.search(queries[0], limit=10)
            
            if results:
                print(f"\n找到 {len(results)} 篇相关论文")
                self.state_machine.add_to_history("agent", f"检索到 {len(results)} 篇论文")
                # 保存结果供展示
                self._search_results = results
            else:
                print("\n未找到相关论文，建议放宽关键词")
                self._search_results = []
        
        self.state_machine.transition(AgentState.PRESENT_RESULTS)
    
    def _handle_present(self):
        """处理结果展示状态"""
        if hasattr(self, '_search_results') and self._search_results:
            print(render_results(self._search_results))
        else:
            print("\n可以使用需求翻译卡中的查询手动检索")
        
        print("\n接下来你想：")
        print("1. 导出结果")
        print("2. 细化检索")
        print("3. 结束")
        
        choice = input("\n> ").strip()
        
        if choice == '3' or choice.lower() == '结束':
            print("再见！")
            sys.exit(0)
        elif choice == '1':
            print("导出功能待实现")
        elif choice == '2':
            # 重新开始
            self.state_machine.reset()
            print("\n请描述新的研究兴趣：")
        else:
            print("再见！")
            sys.exit(0)
    
    def _handle_fallback(self):
        """处理降级状态"""
        print("\n生成宽泛检索计划...")
        self.state_machine.transition(AgentState.GENERATE_PLAN_CARD)


def main():
    """主函数"""
    agent = LiteratureSearchAgent()
    agent.run()


if __name__ == "__main__":
    main()
