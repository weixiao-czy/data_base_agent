# 文献地图（Literature Map）

在原有「需求翻译卡 + 单次检索」之上，补一层**按项目周期组织文献**的能力。

原有链路回答的是「这一次该用什么检索式」；
文献地图回答的是「做这个项目，我应该按什么顺序把这块领域的文献吃下来」。

---

## 它长什么样

一张三层级的思维导图：

```
研究主题
├── 种子文献          直接检索到的代表性论文，作为坐标原点
├── 综述与奠基        → 综述方向 A / B / C   （每个方向挂 2-3 篇真实文献）
├── 核心方法          → 方法 A / B / C
├── 任务与应用        → 应用 A / B / C
├── 数据集与评测      → 数据集 / 基准 / 指标
├── 挑战与开放问题    → 挑战 / 局限 / 开放问题
└── 前沿与最新进展    → 最新进展 / 前沿综述
```

六个维度对应「读文献的完整闭环」：先有全局认知（综述），再定技术路线（方法），
然后找可复用的实验基础（数据集评测），最后用领域痛点找选题切口（挑战）。

---

## 快速开始

```bash
# 生成（默认走规则发散，无需 API Key）
python src/litmap_cli.py "retrieval augmented generation"

# 换主题
python src/litmap_cli.py "graph neural network for drug discovery"

# 控制规模（每多一个检索方向 = 多一次外部请求）
python src/litmap_cli.py "..." \
    --seed-limit 20 --per-topic 3 --topics-per-aspect 3 --max-queries 18

# 指定输出目录、生成后不自动打开浏览器
python src/litmap_cli.py "..." -o output/maps --no-open
```

产物（写入 `output/maps/`，该目录已在 `.gitignore` 中）：

| 文件 | 用途 |
|---|---|
| `<slug>.html` | 自包含交互式思维导图，双击离线可用 |
| `<slug>.md` | 层级大纲 + 文献总表，可直接贴进笔记 |
| `<slug>.json` | 结构化数据，便于二次开发或接入 GUI |

导图支持：节点点击展开/折叠、滚轮缩放、拖拽平移、关键词搜索高亮、
点文献节点看摘要、一键全部展开 / 收起到维度。

---

## 两种发散策略

| 策略 | 触发条件 | 特点 |
|---|---|---|
| `llm` | 配置了 `OPENAI_API_KEY` | 模型结合种子文献生成领域化子主题，**层级质量明显更高** |
| `rule` | 无 Key 或 `--no-llm` | 靠统计术语 + 维度模板，离线可用，质量保守 |

规则策略的具体做法（`terms.py`）：

1. 从种子文献**标题**抽大写缩写（`RAG`、`LLM`）—— 领域内最高精度的术语信号
2. 从**标题**抽 bigram 术语（标题是作者精修过的名词短语，比摘要干净）
3. 从**摘要**抽 bigram 术语，但要求**文档频次** ≥ 3：只在单篇里反复出现的词
   多半是那篇文章的自造系统名，不能拿来代表领域
4. 概念池不够时，退回「主题核心词 + 维度修饰词」，**宁可发散度低也不塞垃圾术语**

这是刻意的取舍：无监督 n-gram 没有词性信息，硬凑只会产出
`Achieve Deeper`、`Welyi Orcid` 这类节点，比少几个分支更难用。

---

## 代码结构

```
src/litmap/
├── models.py     LitNode / LiteratureMap，节点统计与序列化
├── terms.py      概念词抽取（缩写 / 标题术语 / 摘要术语）
├── expander.py   维度发散（LLMExpander / RuleExpander 双策略）
├── builder.py    检索 + 全局去重 + 组装层级
├── render.py     HTML / Markdown / JSON 渲染
└── cli.py        命令行入口
src/litmap_cli.py 薄封装，保持与 gui_launcher.py 一致的调用风格
```

对外 API：

```python
from litmap import build_map, to_html
from search.real_search import RealSearchProvider

litmap = build_map("retrieval augmented generation", RealSearchProvider(),
                   seed_limit=20, per_topic=3)
open("map.html", "w", encoding="utf-8").write(to_html(litmap))
```

---

## 设计要点

**全局去重**：一篇文献在全图只出现一次，挂在最先命中的节点上。
否则同一个方向检索到的论文会在六个分支里重复六次，导图直接失效。
被去重的条目数记录在 `meta.duplicates_removed`。

**访问礼节**：请求之间默认间隔 0.4 秒，遵守 Crossref / arXiv 的使用约定。
`--max-queries` 控制总请求数，跑一次 18 个方向大约 30-60 秒。

**失败隔离**：任一子主题检索失败只记入 `meta.errors`，不影响整张图。
某个方向检索不到文献时节点仍然保留（显示 `×`），提示这里需要人工补检索。

**与原有代码的关系**：完全新增，不修改 `main.py`、`agent/`、`search/`、`gui/`。
只复用 `RealSearchProvider` 的 `SearchProvider` 接口和 `OpenAIClient`。
所以原有 CLI 与 GUI 行为不受任何影响。

---

## 已知边界

- **规则模式发散度有限**：真实效果取决于种子文献数量，`--seed-limit` 低于 10 时
  统计样本不足，多数分支会退回主题兜底。想要真正的领域化发散，请配置 LLM。
- **未接入 GUI**：目前是独立 CLI。要接进 `main_window.py` 需要改原有文件，
  做了最小侵入方案后可以再议。
- **不解析引用关系**：Crossref / arXiv 公开接口不提供引用网络，
  所以「上下游文献」靠检索式近似，不是真实的引文追踪。
- **中文主题**：检索仍走英文 API，中文主题会被直接当作查询词，
  效果不如英文；建议用英文主题。
