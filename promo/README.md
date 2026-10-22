# 文献检索 Agent · 84 秒文献地图版

在原 60 秒宣传片基础上扩展为 **84 秒 / 1920×1080 / 30 fps / 2520 帧 / 120 BPM**。延续墨绿、暖白、荧光绿与珊瑚橙的商业动效风格，新增约 26 秒文献树与内嵌 GUI 展示，原结果段落压缩 2 秒。此次是**源码交付，尚未渲染、未生成新配乐或样帧**。

## 交付入口

- [STORYBOARD.md](STORYBOARD.md)：完整分镜脚本、屏幕文案、精确时间/帧、交互拍点、音乐和审片要点。
- [RENDER_HANDOFF.md](RENDER_HANDOFF.md)：交给后续模型的执行步骤、输出规格、验收清单及常见问题。
- `src/`：全部画面源码及演示数据；`scripts/`：原创配乐生成器、音画事件表、静态检查、审片工具。
- `package.json` + `package-lock.json`：可复现依赖；Remotion 各包固定为 4.0.536。
- `out/delivery/promo-litmap-84s-source.zip`：独立源码交付包（生成后放在这里，不纳入 Git）。包内包含 SHA-256 文件清单；不含旧成片、依赖、音频或项目密钥。

## 不渲染的检查

```bash
cd promo
npm ci
npm run check
```

`check` 只做 TypeScript、脚本语法、依赖锁定、场景注册、2520 帧连续性、节拍、演示数据和音画事件边界检查。不启动 Chromium，不生成图片、音频或视频。

## 后续模型渲染

```bash
npm run render:draft -- --concurrency=2  # 960×540 草稿，自动生成 84 秒音乐
npm run preview                        # 输出交互前后审片帧，需要人工查看
npm run render -- --concurrency=4       # 最终 1080p 成片
```

最终输出 `out/promo-litmap-84s.mp4`，H.264、4:2:0、AAC 320 kbps。两个 render 命令均有对应 pre 钩子，自动先检查再重新生成音乐。**不要复用旧的 60 秒 track.wav**。`npm run start` 打开 Studio，也会先生成音乐。`npm run still` 默认检查新地图段的第 1650 帧。

## 结构

```text
src/film.json                       84 秒时间线（视频/音频/检查共同读取）
src/Promo.tsx / Root.tsx / index.ts  合成入口，Promo 合成 ID
src/commercial/Commercial.tsx       原片场景、更新后的选项点选、结尾
src/commercial/design.tsx           共用配色、排版、动画与背景
src/commercial/TreeScenes.tsx       树形图入口、六维展开、搜索与摘要、返回对话
src/commercial/tree-demo.json       六个维度、示例文献、交互帧号
src/components/Logo.tsx             品牌标记
scripts/audio-plan.mjs              按场景推导音乐段落与交互音效时刻
scripts/gen_audio.mjs               原创配乐 A Clearer Question，扩展到 84 秒
scripts/check-project.mjs           无渲染检查
scripts/preview.mjs                 后续渲染用的关键帧导出
```

`src/scenes/` 等旧版参考文件若仍在本地，不参与当前合成，也不包含在独立交付包中。包内只含活动源文件及必要依赖文件。所有动画由帧号驱动，完全不依赖实时网络、API Key、Python GUI 或屏幕录制。

## 与产品代码对齐

2026-10-22 已通过 `git ls-remote` 核对 GitHub `master`，与本地 `0153f4a2f7f35990d500de6e745b397b3ce058f0` 相同。

- `src/gui/agent_worker.py` 的 `PLAN_ACTIONS`：翻译卡生成后点选「以树形图查看文献结构」。
- `src/gui/main_window.py` 的 `QStackedWidget`：保留左侧历史栏，聊天页与地图页切换，并非并排挤在聊天右侧。
- `src/gui/map_panel.py`：内嵌导图与「返回对话」，缺少 QtWebEngine / 加载失败时可退回浏览器。
- `src/litmap/expander.py`：综述与奠基、核心方法、任务与应用、数据集与评测、挑战与开放问题、前沿与最新进展。
- `src/litmap/render.py`：展开/折叠、滚轮缩放、拖拽平移、搜索高亮、文献详情；HTML / Markdown / JSON。
- `src/litmap/builder.py`：逐方向检索及全图去重。

旧的 `src/litmap/README.md` 仍有「未接入 GUI」描述；本片按当前实现与主 README 制作。此处为功能示意 UI，不是逐像素录屏。示例论文明确标注，没有虚构 DOI、引用量或检索速度。图上的线表示主题层级，不表示论文之间的引用关系。离线可浏览的是**已经生成的 HTML**；生成地图仍需检索网络。生成过程在影片中压缩，不宣称瞬时完成。

## 音乐与验证状态

原创合成配乐，无外部采样或付费素材。保留原有电钢琴、旋律、琶音、贝斯与鼓组；48–58 秒树形结构展开形成第二个能量峰值，58–68 秒给交互阅读留空间，76 秒撤鼓，80 秒解决和弦，末尾自然淡出。输出 48 kHz 双声道，目标样本峰值 -1.2 dBFS；新版实际响度与编码后真峰值由后续渲染者测量。

此次通过 `npm run check`。未做新版样帧审查、成片解码或试听，不把旧成片的验证结果当作新版结论。渲染时需特别检查地图长中文标签、缩放后的选中文献、摘要面板、点击坐标和 84 秒音轨尾部。
