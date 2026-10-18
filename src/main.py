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
        print("\n请描述你的研究兴趣（输入 'quit' 退出）：")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() == 'quit':
                    print("再见！")
                    break
                
                if not user_input:
                    continue
                
                # TODO: 实现完整的对话流程
                # 1. 复述
                # 2. 分叉追问（最多 3 轮）
                # 3. 生成需求翻译卡
                # 4. 调用检索
                # 5. 展示结果
                
                print(f"\n收到: {user_input}")
                print("（完整流程待实现）")
                
            except KeyboardInterrupt:
                print("\n\n程序中断")
                break
            except Exception as e:
                print(f"\n错误: {e}")


def main():
    """主函数"""
    agent = LiteratureSearchAgent()
    agent.run()


if __name__ == "__main__":
    main()
