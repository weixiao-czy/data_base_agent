"""
主程序入口：文献检索需求翻译 Agent
"""

import sys
import os
from agent.state_machine import StateMachine, AgentState
from agent.clarifier import Clarifier
from agent.plan_card import PlanCardGenerator
from search.fallback_provider import FallbackSearchProvider
from search.real_search import RealSearchProvider
from search.scimaster_mcp import SciMasterMCPProvider
from search.scimaster_cli import SciMasterCLIProvider
from presentation.render_results import render_results, render_plan_card
from llm.client import OpenAIClient, MockLLMClient


class LiteratureSearchAgent:
    """文献检索需求翻译 Agent"""
    
    def __init__(self, max_rounds: int = 10, use_mock_llm: bool = False):
        """
        初始化 Agent
        
        Args:
            max_rounds: 最大澄清轮次
            use_mock_llm: 是否使用模拟 LLM（用于测试）
        """
        self.state_machine = StateMachine(max_rounds=max_rounds)
        
        # 初始化 LLM 客户端
        if use_mock_llm:
            llm_client = MockLLMClient()
            print("使用模拟 LLM 模式")
        else:
            try:
                llm_client = OpenAIClient()
                print(f"使用 LLM 模式（模型：{llm_client.model}）")
            except Exception as e:
                # 配置错误要让人看得见：静默降级会让用户以为自己在用真实模型，
                # 实际拿到的是模拟回复，排查成本极高。
                print()
                print("!" * 62)
                print("LLM 初始化失败，已降级为「模拟 LLM 模式」。")
                print("注意：此模式下不会真正调用大模型，回复内容为固定模板。")
                print()
                for line in str(e).splitlines():
                    print(f"  {line}")
                print("!" * 62)
                print()
                llm_client = MockLLMClient()
        
        self.clarifier = Clarifier(llm_client=llm_client)
        self.plan_card_generator = PlanCardGenerator(llm_client=llm_client)
        
        # 初始化检索提供者（MCP 优先，CLI 降级）
        self.search_provider = self._init_search_provider()
    
    def _init_search_provider(self):
        """初始化检索提供者（自动降级链）

        优先级：
        1. SciMaster MCP（真实 API Key + npx 可用时启用）
        2. Crossref + arXiv（免费、无需 Key，兜底来源）
        3. SciMaster CLI（最后降级）

        任一来源失败自动切换到下一个，用户无感知。
        """
        providers = []

        mcp = SciMasterMCPProvider()
        if mcp.is_available():
            providers.append(mcp)

        real = RealSearchProvider()
        if real.is_available():
            providers.append(real)

        cli = SciMasterCLIProvider()
        if cli.is_available():
            providers.append(cli)

        if not providers:
            print("警告: 检索服务不可用，将只生成检索计划")
            return None

        # 展示当前可用的来源
        names = [p.__class__.__name__ for p in providers]
        print(f"检索来源（按优先级）: {' -> '.join(names)}")

        return FallbackSearchProvider(providers)
    
    def run(self):
        """运行 Agent 主循环"""
        print("="*50)
        print("文献检索需求翻译 Agent")
        print("="*50)
        print(f"\n我会帮你把模糊的研究兴趣翻译成可检索的关键词。")
        print(f"最多需要 {self.state_machine.max_rounds} 轮对话，你也可以随时说「跳过」直接生成检索计划。")
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
        try:
            user_input = input("\n> ").strip()
        except EOFError:
            print("\n再见！")
            sys.exit(0)
        
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
        try:
            user_choice = input("\n> ").strip()
        except EOFError:
            print("\n再见！")
            sys.exit(0)
        
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
            "history": self.state_machine.clarification_history,
            "current_round": self.state_machine.current_round,
            "max_rounds": self.state_machine.max_rounds
        }
        
        question = self.clarifier.probe_key_fork(context)
        
        remaining = self.state_machine.get_remaining_rounds()
        print(f"\n（还剩 {remaining} 轮澄清机会）")
        print(question)
        print("（输入选项字母，或说「跳过」直接生成计划）")
        
        self.state_machine.add_to_history("agent", question)
        self.state_machine.increment_round()
        
        user_answer = None
        try:
            user_answer = input("\n> ").strip()
        except EOFError:
            print("\n再见！")
            sys.exit(0)
        
        if user_answer.lower() == 'quit':
            print("再见！")
            sys.exit(0)
        
        if user_answer.lower() in ['跳过', 'skip']:
            # 直接生成计划
            self.state_machine.transition(AgentState.GENERATE_PLAN_CARD)
            return
        
        self.state_machine.add_to_history("user", user_answer)
        self.state_machine.add_to_history("agent", f"已记录: {user_answer}")
        
        # 已经把用户回答写进解读结论，供下一轮追问参考
        if user_answer:
            self.state_machine.interpretation = (
                f"{self.state_machine.interpretation}；{user_answer}"
            )
        
        # 检查是否还能继续追问
        if self.state_machine.can_clarify():
            # 回到追问状态继续澄清（最多 max_rounds 轮）
            self.state_machine.transition(AgentState.PROBE_KEY_FORK)
        else:
            # 轮次用尽，收敛到需求翻译卡
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
        
        # 自动保存为 txt 文件
        output_path = self._export_plan_card_to_txt(plan_card)
        if output_path:
            print(f"\n[已保存] 需求翻译卡已导出到: {output_path}")
        
        print("\n这个计划看起来如何？")
        print("1. 确认，开始检索")
        print("2. 需要调整")
        print("3. 重新生成")
        print("4. 重新导出 txt")
        print("5. 以树形图查看文献结构（发散检索 + 思维导图）")
        
        self.state_machine.transition(AgentState.USER_CONFIRM)
    
    def _handle_user_confirm(self):
        """处理用户确认状态"""
        try:
            choice = input("\n> ").strip()
        except EOFError:
            print("\n再见！")
            sys.exit(0)
        
        if choice in ['1', '确认']:
            self.state_machine.transition(AgentState.CALL_SEARCH)
        elif choice in ['2', '调整']:
            print("请告诉我需要调整什么：")
            try:
                adjustment = input("\n> ").strip()
            except EOFError:
                print("\n再见！")
                sys.exit(0)
            self.state_machine.add_to_history("user", f"调整: {adjustment}")
            # 重新生成
            self.state_machine.transition(AgentState.GENERATE_PLAN_CARD)
        elif choice in ['3', '重新生成']:
            self.state_machine.transition(AgentState.GENERATE_PLAN_CARD)
        elif choice in ['4', '导出']:
            output_path = self._export_plan_card_to_txt(self.state_machine.plan_card)
            if output_path:
                print(f"\n[已保存] 需求翻译卡已导出到: {output_path}")
            # 继续等待用户选择
        elif choice in ['5', '树形图', '导图', 'map']:
            self._view_literature_tree()
        else:
            print("无效选择，默认开始检索")
            self.state_machine.transition(AgentState.CALL_SEARCH)
    
    def _view_literature_tree(self):
        """以树形图查看文献结构
        
        复用前面多轮澄清得到的结论作为检索主题，而不是让用户重新输入，
        这样「对话澄清 → 层级导图」是一条连贯的链路。
        """
        print("\n" + "=" * 50)
        print("以树形图查看文献结构")
        print("=" * 50)
        
        # 检索主题的优先级：
        #   1. 用户最初描述的研究兴趣（信息量最大，含具体领域词）
        #   2. 澄清后的解读结论
        #   3. 需求翻译卡中的主关键词
        # 不能反过来用「解读结论」优先：多轮澄清后它常被收敛成
        # 「理论研究」「实践应用」这类无区分度的词，拿去检索会跑偏。
        sm = self.state_machine
        candidates = [sm.user_input, sm.interpretation]
        plan = sm.plan_card
        if plan:
            candidates.append(" ".join(plan.suggested_keywords.get('primary', [])[:3]))

        vague = {'理论研究', '实践应用', '不确定', '系统实现', '理论分析', '实验验证'}
        topic = ""
        for c in candidates:
            c = (c or "").strip()
            if c and c not in vague:
                topic = c
                break
        if not topic:
            topic = (sm.user_input or sm.interpretation or "").strip()
        if not topic:
            print("没有得到有效的研究主题，请回到上一步重新描述。")
            return

        # 需求翻译卡里的建议检索式对发散检索仍然有参考价值，一并展示
        queries = plan.search_plan.get('suggested_queries', []) if plan else []
        
        print(f"检索主题：{topic}")
        if queries:
            print("需求翻译卡中的建议检索式：")
            for q in queries[:3]:
                print(f"  · {q}")
        
        print("\n将在此主题下按「综述 / 方法 / 应用 / 数据集 / 挑战 / 前沿」"
              "六个维度发散检索，并生成层级导图。")
        
        try:
            scale = input("\n检索规模（1=快速约30秒 / 2=标准约1分钟 / 回车=标准）：").strip()
        except (EOFError, KeyboardInterrupt):
            scale = ""
        if scale == "1":
            cfg = dict(seed_limit=8, per_topic=2, topics_per_aspect=2, max_queries=8)
        else:
            cfg = dict(seed_limit=15, per_topic=3, topics_per_aspect=3, max_queries=18)
        
        try:
            from litmap.builder import LiteratureMapBuilder, summarize
            from litmap.render import to_html, to_json, to_markdown
        except ImportError as e:
            print(f"[错误] 文献地图模块不可用：{e}")
            return
        
        llm = None if isinstance(self.clarifier.llm_client, MockLLMClient) else self.clarifier.llm_client
        
        builder = LiteratureMapBuilder(
            provider=self.search_provider,
            llm_client=llm,
            **cfg,
        )
        try:
            litmap = builder.build(topic)
        except Exception as e:
            print(f"[错误] 构建文献地图失败：{e}")
            return
        
        # 输出三份产物
        import os
        from datetime import datetime
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output", "maps"
        )
        os.makedirs(output_dir, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = "".join(c if (c.isalnum() or c in "-_") else "_" for c in topic)[:40]
        base = os.path.join(output_dir, f"{slug}_{stamp}")
        
        with open(base + ".html", "w", encoding="utf-8") as f:
            f.write(to_html(litmap))
        with open(base + ".md", "w", encoding="utf-8") as f:
            f.write(to_markdown(litmap))
        with open(base + ".json", "w", encoding="utf-8") as f:
            f.write(to_json(litmap))
        
        print()
        print(summarize(litmap))
        print()
        print(f"[已保存] 树形图（浏览器打开）：{base}.html")
        print(f"[已保存] 层级大纲：{base}.md")
        print(f"[已保存] 结构化数据：{base}.json")
        
        try:
            import webbrowser
            webbrowser.open("file://" + os.path.abspath(base + ".html"))
            print("\n已在浏览器中打开导图。")
        except Exception:
            pass
        
        print("\n按回车回到计划确认页面…")
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass
        # 停留在 USER_CONFIRM，方便用户继续选择「确认开始检索」
    
    def _handle_search(self):
        """处理检索状态"""
        if not self.search_provider:
            print("\n检索服务不可用，请手动使用以下查询：")
            for query in self.state_machine.plan_card.search_plan['suggested_queries']:
                print(f"  - {query}")
            self.state_machine.transition(AgentState.PRESENT_RESULTS)
            return
        
        print("\n正在检索...")
        
        # 使用需求翻译卡中的查询
        queries = self.state_machine.plan_card.search_plan['suggested_queries']
        
        if queries:
            # 使用第一个查询进行检索
            primary_query = queries[0]
            print(f"使用查询: {primary_query}")
            
            results = self.search_provider.search(primary_query, limit=10)
            
            if results:
                print(f"\n找到 {len(results)} 篇相关论文")
                self.state_machine.add_to_history("agent", f"检索到 {len(results)} 篇论文")
                # 保存结果供展示
                self._search_results = results
            else:
                print("\n未找到相关论文")
                print("建议：")
                print("  1. 放宽关键词")
                print("  2. 尝试其他查询:")
                for q in queries[1:]:
                    print(f"     - {q}")
                self._search_results = []
        else:
            print("\n没有可用的检索查询")
            self._search_results = []
        
        self.state_machine.transition(AgentState.PRESENT_RESULTS)
    
    def _handle_present(self):
        """处理结果展示状态"""
        if hasattr(self, '_search_results') and self._search_results:
            print(render_results(self._search_results))
            
            # 自动保存检索结果为 txt 文件
            output_path = self._export_search_results_to_txt(self._search_results)
            if output_path:
                print(f"\n[已保存] 检索结果已导出到: {output_path}")
        else:
            print("\n可以使用需求翻译卡中的查询手动检索")
        
        print("\n接下来你想：")
        print("1. 导出结果到 txt")
        print("2. 细化检索")
        print("3. 结束")
        
        try:
            choice = input("\n> ").strip()
        except EOFError:
            # 输入流结束（管道/重定向场景）时必须退出，
            # 否则状态机停留在 PRESENT_RESULTS，会不断重新打印全部结果
            print("\n再见！")
            sys.exit(0)
        
        if choice == '3' or choice.lower() == '结束':
            print("再见！")
            sys.exit(0)
        elif choice == '1':
            if hasattr(self, '_search_results') and self._search_results:
                output_path = self._export_search_results_to_txt(self._search_results)
                if output_path:
                    print(f"\n[已保存] 检索结果已导出到: {output_path}")
            else:
                print("\n没有可导出的检索结果")
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
    
    def _export_plan_card_to_txt(self, plan_card) -> str:
        """
        将需求翻译卡导出为 txt 文件
        
        Args:
            plan_card: PlanCard 实例
            
        Returns:
            输出文件路径，失败返回空字符串
        """
        import os
        from datetime import datetime
        
        try:
            # 创建 output 目录
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output")
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"plan_card_{timestamp}.txt"
            output_path = os.path.join(output_dir, filename)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("需求翻译卡\n")
                f.write("="*60 + "\n\n")
                
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write(f"研究兴趣: {plan_card.research_interest}\n")
                f.write(f"解读问题: {plan_card.interpreted_question}\n")
                f.write(f"研究类型: {plan_card.research_intent_type}\n\n")
                
                f.write("关键维度:\n")
                for dim in plan_card.key_dimensions:
                    f.write(f"  - {dim}\n")
                f.write("\n")
                
                f.write("建议关键词:\n")
                f.write(f"  主要: {', '.join(plan_card.suggested_keywords['primary'])}\n")
                f.write(f"  变体: {', '.join(plan_card.suggested_keywords['variants'])}\n")
                f.write(f"  相邻领域: {', '.join(plan_card.suggested_keywords['adjacent_fields'])}\n\n")
                
                f.write("不确定性:\n")
                for unc in plan_card.uncertainties:
                    f.write(f"  - {unc}\n")
                f.write("\n")
                
                f.write("检索计划:\n")
                f.write(f"  模式: {plan_card.search_plan['mode']}\n")
                f.write("  建议查询:\n")
                for query in plan_card.search_plan['suggested_queries']:
                    f.write(f"    - {query}\n")
                f.write("\n")
                
                f.write("下一步行动:\n")
                for action in plan_card.next_actions:
                    f.write(f"  - {action}\n")
                f.write("\n")
                
                f.write("="*60 + "\n")
            
            return output_path
            
        except Exception as e:
            print(f"\n[错误] 导出失败: {e}")
            return ""
    
    def _export_search_results_to_txt(self, results: list) -> str:
        """
        将检索结果导出为 txt 文件
        
        Args:
            results: 论文列表
            
        Returns:
            输出文件路径，失败返回空字符串
        """
        import os
        from datetime import datetime
        
        try:
            # 创建 output 目录
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output")
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"search_results_{timestamp}.txt"
            output_path = os.path.join(output_dir, filename)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("检索结果\n")
                f.write("="*60 + "\n\n")
                
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"检索结果数量: {len(results)} 篇\n\n")
                
                # 如果有需求翻译卡，也写入查询信息
                if self.state_machine.plan_card:
                    f.write("检索查询:\n")
                    for query in self.state_machine.plan_card.search_plan['suggested_queries']:
                        f.write(f"  - {query}\n")
                    f.write("\n")
                
                f.write("-"*60 + "\n\n")
                
                for i, paper in enumerate(results, 1):
                    f.write(f"[{i}] {paper.get('title', '无标题')}\n\n")
                    
                    authors = paper.get('authors', [])
                    if authors:
                        f.write(f"作者: {', '.join(authors)}\n")
                    
                    year = paper.get('year', '')
                    if year:
                        f.write(f"年份: {year}\n")
                    
                    venue = paper.get('venue', '')
                    if venue:
                        f.write(f"发表: {venue}\n")
                    
                    doi = paper.get('doi', '')
                    if doi:
                        f.write(f"DOI: {doi}\n")
                    
                    url = paper.get('url', '')
                    if url:
                        f.write(f"链接: {url}\n")
                    
                    f.write(f"\n摘要: {paper.get('abstract', '无摘要')}\n")
                    
                    bibtex = paper.get('bibtex', '')
                    if bibtex:
                        f.write(f"\nBibTeX:\n{bibtex}\n")
                    
                    f.write("\n" + "-"*60 + "\n\n")
                
                f.write("="*60 + "\n")
            
            return output_path
            
        except Exception as e:
            print(f"\n[错误] 导出失败: {e}")
            return ""


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="文献检索需求翻译 Agent")
    parser.add_argument("--mock-llm", action="store_true", help="使用模拟 LLM（用于测试）")
    parser.add_argument("--max-rounds", type=int, default=10, help="最大澄清轮次（默认：10）")
    
    args = parser.parse_args()
    
    agent = LiteratureSearchAgent(
        max_rounds=args.max_rounds,
        use_mock_llm=args.mock_llm
    )
    agent.run()


if __name__ == "__main__":
    main()
