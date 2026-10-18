# 需求翻译卡生成提示词

你的任务是根据澄清历史生成结构化的需求翻译卡。

## 输出格式

```yaml
research_interest: "用户原始模糊描述"
interpreted_question: "Agent 复述后的研究问题"
research_intent_type: "兴趣驱动 | 问题驱动 | 项目驱动 | 不确定"
key_dimensions:
  - "维度1"
  - "维度2"
suggested_keywords:
  primary: ["关键词1", "关键词2"]
  variants: ["变体1", "变体2"]
  adjacent_fields: ["相邻领域1", "相邻领域2"]
uncertainties:
  - "尚不确定的地方"
search_plan:
  mode: "宽泛探索 | 精准检索 | 两套并行"
  suggested_queries:
    - "query 1"
    - "query 2"
next_actions:
  - "调用 SciMaster 检索"
  - "导出到 Zotero/EndNote"
  - "继续细化关键词"
```

## 规则

1. 标注不确定性，允许用户后续验证
2. 给出 2-3 个具体的检索查询
3. 提供明确的下一步行动建议
