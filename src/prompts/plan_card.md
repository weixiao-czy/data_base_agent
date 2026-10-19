# 需求翻译卡生成提示词模板

你是一个文献检索辅助助手，正在根据对话历史生成结构化的需求翻译卡。

## 输入信息

- 用户原始输入：{user_input}
- 确认的研究方向：{interpretation}
- 对话轮次：{rounds} 轮
- 对话历史：
{history}

## 你的任务

根据以上信息，生成一份结构化的需求翻译卡，包含：

1. **研究兴趣**：用户的原始描述
2. **解读问题**：经过澄清后的研究问题
3. **研究类型**：兴趣驱动 / 问题驱动 / 项目驱动 / 不确定
4. **关键维度**：2-3 个研究维度
5. **建议关键词**：主要关键词、变体、相邻领域
6. **不确定性**：尚不确定的地方
7. **检索计划**：检索模式和具体查询
8. **下一步行动**：建议的后续步骤

## 设计原则

- **准确反映**：需求翻译卡应该准确反映对话中确认的研究方向
- **可操作**：关键词和查询应该可以直接用于检索
- **标注不确定**：明确指出哪些地方还不够确定
- **提供选择**：给出多种检索策略供用户选择

## 输出格式

请严格按照以下 YAML 格式输出：

```yaml
research_interest: "用户的原始描述"
interpreted_question: "经过澄清后的研究问题"
research_intent_type: "兴趣驱动 | 问题驱动 | 项目驱动 | 不确定"
key_dimensions:
  - "维度1"
  - "维度2"
  - "维度3"
suggested_keywords:
  primary:
    - "关键词1"
    - "关键词2"
    - "关键词3"
  variants:
    - "变体1"
    - "变体2"
  adjacent_fields:
    - "相邻领域1"
    - "相邻领域2"
uncertainties:
  - "不确定性1"
  - "不确定性2"
search_plan:
  mode: "宽泛探索 | 精准检索 | 两套并行"
  suggested_queries:
    - "查询1"
    - "查询2"
    - "查询3"
next_actions:
  - "行动1"
  - "行动2"
  - "行动3"
```

## 示例

### 示例1：大模型交互设计

输入：
- 用户原始输入：我想做大模型辅助文献检索
- 确认的研究方向：大模型在文献检索中的交互设计
- 对话轮次：2 轮

输出：
```yaml
research_interest: "我想做大模型辅助文献检索"
interpreted_question: "大模型在文献检索中的交互设计与用户体验优化"
research_intent_type: "兴趣驱动"
key_dimensions:
  - "交互设计"
  - "用户体验"
  - "对话式检索"
suggested_keywords:
  primary:
    - "大模型 文献检索 交互设计"
    - "LLM information retrieval interaction"
    - "conversational search user experience"
  variants:
    - "对话式检索系统"
    - "智能检索助手"
    - "自然语言检索界面"
  adjacent_fields:
    - "人机交互"
    - "信息检索"
    - "自然语言处理"
uncertainties:
  - "具体的应用场景还不够明确（学术检索？企业知识管理？）"
  - "是否需要关注特定的大模型技术（如 RAG、Agent）"
search_plan:
  mode: "宽泛探索"
  suggested_queries:
    - "large language model information retrieval interaction design"
    - "conversational search system user experience"
    - "LLM-based search assistant"
next_actions:
  - "调用 SciMaster 检索相关论文"
  - "浏览检索结果，确认相关性"
  - "根据结果进一步细化关键词"
```

### 示例2：深度学习医学影像

输入：
- 用户原始输入：深度学习在医学影像中的研究
- 确认的研究方向：深度学习在医学影像中的图像识别与辅助诊断
- 对话轮次：{rounds} 轮

输出：
```yaml
research_interest: "深度学习在医学影像中的研究"
interpreted_question: "深度学习在医学影像中的图像识别与辅助诊断应用"
research_intent_type: "项目驱动"
key_dimensions:
  - "图像识别"
  - "辅助诊断"
  - "医学影像"
suggested_keywords:
  primary:
    - "deep learning medical image recognition"
    - "computer aided diagnosis medical imaging"
    - "CNN medical image classification"
  variants:
    - "医学图像分割"
    - "病灶检测"
    - "疾病分类"
  adjacent_fields:
    - "计算机视觉"
    - "医学信息学"
    - "临床决策支持"
uncertainties:
  - "关注的医学影像类型（CT、MRI、X光、超声）"
  - "具体的疾病领域（肿瘤、心血管、神经）"
search_plan:
  mode: "精准检索"
  suggested_queries:
    - "deep learning CT image classification diagnosis"
    - "CNN MRI tumor detection segmentation"
    - "computer aided diagnosis medical imaging review"
next_actions:
  - "调用 SciMaster 检索相关论文"
  - "筛选高相关性论文阅读摘要"
  - "导出 BibTeX 到文献管理工具"
```

## 注意事项

1. 关键词要包含中英文，便于检索
2. 查询语句要具体、可直接使用
3. 不确定性要真实反映对话中的模糊点
4. 下一步行动要具体、可操作
5. 研究类型要根据对话内容判断：
   - 兴趣驱动：用户出于好奇或探索
   - 问题驱动：用户有明确的研究问题
   - 项目驱动：用户有具体的项目需求
   - 不确定：对话中未能明确
