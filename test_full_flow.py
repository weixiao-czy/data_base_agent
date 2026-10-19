"""
完整对话流程测试脚本
"""

import sys
sys.path.insert(0, 'src')

from agent.state_machine import StateMachine, AgentState
from agent.clarifier import Clarifier
from agent.plan_card import PlanCardGenerator
from llm.client import OpenAIClient


def test_full_flow():
    """测试完整的对话流程"""
    print("="*60)
    print("完整对话流程测试")
    print("="*60)
    
    # 初始化组件
    try:
        llm_client = OpenAIClient()
        print(f"\n[OK] LLM 客户端初始化成功")
        print(f"  Model: {llm_client.model}")
        print(f"  Base URL: {llm_client.base_url or '默认'}")
    except Exception as e:
        print(f"\n[ERROR] LLM 初始化失败: {e}")
        return
    
    state_machine = StateMachine(max_rounds=3)  # 测试用3轮
    clarifier = Clarifier(llm_client=llm_client)
    plan_card_generator = PlanCardGenerator()
    
    # 模拟用户输入
    test_inputs = [
        "我想做大模型辅助文献检索",
        "1",  # 选择第一个选项
        "A",  # 回答追问
    ]
    
    print("\n" + "="*60)
    print("开始对话流程")
    print("="*60)
    
    # 步骤1: IDLE -> RESTATE
    print("\n[步骤1] 用户输入研究兴趣")
    user_input = test_inputs[0]
    print(f"用户: {user_input}")
    
    state_machine.user_input = user_input
    state_machine.add_to_history("user", user_input)
    state_machine.transition(AgentState.RESTATE)
    
    # 步骤2: RESTATE - 复述
    print("\n[步骤2] Agent 复述")
    try:
        restate_result = clarifier.restate(user_input)
        print(f"Agent: {restate_result['restatement']}")
        print("\n选项:")
        for i, option in enumerate(restate_result['options'], 1):
            print(f"  {i}. {option}")
        
        state_machine.add_to_history("agent", restate_result['restatement'], 
                                    {"options": restate_result['options']})
        state_machine.transition(AgentState.CONFIRM_INTERPRETATION)
    except Exception as e:
        print(f"[ERROR] 复述失败: {e}")
        return
    
    # 步骤3: CONFIRM - 确认选择
    print("\n[步骤3] 用户选择")
    user_choice = test_inputs[1]
    print(f"用户: {user_choice}")
    
    interpretation = clarifier.confirm_interpretation(user_choice, restate_result['options'])
    state_machine.interpretation = interpretation
    state_machine.add_to_history("user", user_choice)
    state_machine.add_to_history("agent", f"确认方向: {interpretation}")
    
    print(f"确认的研究方向: {interpretation}")
    
    # 步骤4: PROBE - 追问
    print("\n[步骤4] Agent 追问")
    try:
        context = {
            "interpretation": interpretation,
            "history": state_machine.clarification_history
        }
        probe_question = clarifier.probe_key_fork(context)
        print(f"Agent: {probe_question}")
        
        state_machine.add_to_history("agent", probe_question)
        state_machine.increment_round()
        state_machine.transition(AgentState.PROBE_KEY_FORK)
    except Exception as e:
        print(f"[ERROR] 追问失败: {e}")
        return
    
    # 步骤5: 用户回答追问
    print("\n[步骤5] 用户回答追问")
    user_answer = test_inputs[2]
    print(f"用户: {user_answer}")
    state_machine.add_to_history("user", user_answer)
    
    # 步骤6: GENERATE_PLAN_CARD - 生成需求翻译卡
    print("\n[步骤6] 生成需求翻译卡")
    try:
        plan_card = plan_card_generator.generate(
            state_machine.clarification_history,
            state_machine.user_input,
            state_machine.interpretation
        )
        
        print("\n" + "="*60)
        print("需求翻译卡")
        print("="*60)
        print(f"\n研究兴趣: {plan_card.research_interest}")
        print(f"解读问题: {plan_card.interpreted_question}")
        print(f"研究类型: {plan_card.research_intent_type}")
        
        print("\n关键维度:")
        for dim in plan_card.key_dimensions:
            print(f"  - {dim}")
        
        print("\n建议关键词:")
        print(f"  主要: {', '.join(plan_card.suggested_keywords['primary'])}")
        print(f"  变体: {', '.join(plan_card.suggested_keywords['variants'])}")
        print(f"  相邻领域: {', '.join(plan_card.suggested_keywords['adjacent_fields'])}")
        
        print("\n不确定性:")
        for unc in plan_card.uncertainties:
            print(f"  - {unc}")
        
        print("\n检索计划:")
        print(f"  模式: {plan_card.search_plan['mode']}")
        print("  建议查询:")
        for query in plan_card.search_plan['suggested_queries']:
            print(f"    - {query}")
        
        print("\n下一步行动:")
        for action in plan_card.next_actions:
            print(f"  - {action}")
        
        print("\n" + "="*60)
        print("[OK] 完整流程测试成功!")
        print("="*60)
        
    except Exception as e:
        print(f"[ERROR] 生成需求翻译卡失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_full_flow()
