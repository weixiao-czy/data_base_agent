# 内容依据与教学简化范围

核对日期：2026-10-22。产品仓库：<https://github.com/weixiao-czy/data_base_agent>。核对提交：`644e397db2e844b98370f2db8221dfc4d134f908`。本教程没有实际调用用户 API，也没有读取用户 `.env` 或个人配置中的密钥。

| 教学内容 | 产品实现依据（产品仓库路径） |
| --- | --- |
| LLM 配置、SciMaster、常规三个标签；API Key / Base URL / 模型；保存配置 | `src/gui/settings_dialog.py`，`SettingsDialog`；配置保存于用户目录 `.databaseagent/config.json` |
| 默认交大接口与模型 | `src/gui/settings_dialog.py` 的配置加载；`.env.example` 仅作变量名参考，不把“免费”注释当作对所有账号的承诺 |
| GUI 非空设置优先、空值回退环境变量、模型调用降级提示 | `src/gui/agent_worker.py`，初始化与重置逻辑；`src/llm/client.py` |
| .env 搜索路径、系统变量优先、模型客户端直连 | `src/llm/client.py`，显式 dotenv 加载、`override=False`、`httpx.Client(trust_env=False, timeout=60.0)` |
| 就绪不是测试连接 | `src/gui/main_window.py` 的 `_idle_status` 仅判断配置是否存在；设置页没有单独测试按钮 |
| 澄清选项、其他、跳过、计划确认菜单 | `src/gui/agent_worker.py` 的澄清逻辑与 `PLAN_ACTIONS`；`src/gui/main_window.py` 的选项回调 |
| 看完地图仍可普通检索，且菜单改变 | `src/gui/agent_worker.py` 的 `_view_literature_tree`、`MAP_ACTIONS`、`_emit_map_actions`；状态保持 `USER_CONFIRM`，显示四个后续操作 |
| 六个研究维度与种子分支 | `src/litmap/expander.py`；`src/litmap/builder.py`。六维为综述与奠基、核心方法、任务与应用、数据集与评测、挑战与开放问题、前沿与最新进展 |
| 节点展开/折叠、搜索、高亮、平移缩放、摘要详情 | `src/litmap/render.py`；标题搜索与节点点击处理，无外部 CDN 脚本依赖 |
| 内嵌地图、返回对话、浏览器回退 | `src/gui/main_window.py` 的地图切页逻辑；`src/gui/map_panel.py` 的 WebEngine 可选加载与浏览器打开 |
| 最近地图与导入 HTML | `src/gui/main_window.py` 的 `_show_recent_maps`、`_import_map`、`_open_recent_map` |
| 地图 HTML / MD / JSON 自动保存 | `src/gui/agent_worker.py` 的 `_view_literature_tree`；源码根或 EXE 同级 `output/maps` |
| 导出计划与结果 | `src/gui/main_window.py` 的顶部按钮和导出方法；已有内容后才可导出 |
| SciMaster 可选、公开检索回退 | `src/gui/agent_worker.py` 与 `src/search/`；SciMaster MCP 需要它的专用密钥和 npx 环境 |
| GUI 启动和依赖 | `gui_launcher.py`、`requirements.txt`；教程固定使用一条 Python 3.12 路线，未重新安装并测试全套产品依赖 |

制作时通过 GitHub 发布接口核对到 `Better_GUI_function` 等发布记录存在 `LiteratureSearchAgent.exe` 附件，较早发布也有 ZIP 程序包。教程使用发布页而非固定旧版下载链接。源码更新不代表已经发布新 EXE；最终发布教程前再次核对实际下载版本是否包含地图菜单。

## 画面与实际程序的关系

画面是为教学重绘的矢量界面。保留操作顺序与关键按钮名称，简化窗体装饰、布局密度、计划字段、文件对话框。地图镜头放大地图工作区，不复刻左侧历史栏；实际应用用地图页替换对话工作区，左侧历史栏仍在。

“以树形图查看文献结构”按钮省略了括号中的说明；真实完整标签含“发散检索 + 思维导图”。返回后的菜单单独按 `MAP_ACTIONS` 绘制，没有重复展示原五项菜单。示意图把研究主题放在左侧向右展开；“从主题看向分支”是阅读方向，不是要求主题位于屏幕几何中心。

文件名、论文、摘要、聊天回复都标明为示例，不声称实际检索到这些论文。服务商控制台是通用示意，不冒充某家当前页面，不提供或要求所有人使用同一服务商。跨平台账号注册、实名或额度购买由对应平台规则决定，不属于这个程序的统一界面。

Python 3.12 的传统 Windows 安装器可在官方 [3.12.10 发布页](https://www.python.org/downloads/release/python-31210/)的 Files 列表中找到；官方页面同时说明它已被后续版本替代。本教程使用 3.12 系列作示例，不声称 3.12.10 是当前最新补丁版本，也未把它写成产品唯一支持版本。

## 本次验证边界

交付前检查 TypeScript、场景连续性、字幕时间、中文文本行数预算、内容导出一致性、语法、依赖锁文件和压缩包内容。不运行 GUI、不测试密钥、不生成音频/样帧/视频。中文字体的实际字宽、动画播放、语音长度及最终混音留给后续预览验收。
