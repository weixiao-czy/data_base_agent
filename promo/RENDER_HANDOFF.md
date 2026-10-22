# 渲染交接说明

## 给接手模型的任务

请按本目录已经实现的分镜渲染 **84 秒文献地图版** 宣传片。先读 `README.md` 和 `STORYBOARD.md`，执行检查与草稿审片，再输出最终 1080p 视频。保留既定的中文文案、时间线、配色和原创配乐；不需要重写宣传片、找外部素材、运行 Python 项目或调用学术 API。

当前交付状态：源码、音频生成脚本、时间线及分镜已准备；`npm run check` 已通过；**本版没有生成新音频、样帧或视频，视觉和听觉验收留待你执行**。本地 `out/` 里旧视频及 `src/audio/track.wav` 如存在，均可能属于 60 秒旧版，禁止直接复用。

## 环境与入口

- 在包含 `package.json` 的目录运行命令。仓库内为 `D:/program/databaseagent/promo`；若使用 ZIP，进入解压后的 `promo` 文件夹。
- Node.js 22+、npm；源码无运行时在线素材。首次安装依赖/Chromium 可能需要网络，后续画面不依赖网络。
- 中文字体：Windows 自带 Microsoft YaHei；macOS 使用 PingFang SC；Linux 安装 Noto Sans CJK SC（检查实际字体名称），否则不可交付缺字或替代字体异常的片子。
- Remotion 合成 ID：`Promo`；入口：`src/index.ts`。1920×1080、30 fps、2520 帧。没有另一个新合成 ID。
- 现有机器若 `npm ls --depth=0` 无错误，可以复用 node_modules；独立 ZIP 需 `npm ci`。依赖版本已锁定，别为了渲染先升级 Remotion。

## 命令顺序

```bash
npm ci
npm run check
npm run render:draft -- --concurrency=2
npm run preview
npm run render -- --concurrency=4
```

- `check` 不产生媒体。
- `render:draft` 自动检查并生成 84 秒 `src/audio/track.wav`，输出 `out/promo-litmap-draft.mp4`，960×540。
- `preview` 会重新生成配乐，然后导出每镜头阅读帧、切点前帧及新交互前后的帧到 `out/review-litmap/`。这些只是「已输出」的图，不代表已经审查，必须实际打开检查。
- `render` 自动检查并重新生成配乐，输出 `out/promo-litmap-84s.mp4`。命令使用 H.264 / 4:2:0 / CRF 18，AAC 320 kbps。
- 内存不足时降并发为 1 或 2，不要降低最终分辨率或擅自缩短时长。
- 如果只需要一张指定帧：先 `npm run gen-audio`，再 `npx remotion still Promo out/check.png --frame=1897`。1897 帧位于新摘要面板刚出现后；地图完整帧可用 1650，结尾完整帧可用 2440。
- 如需 Studio：`npm run start`。不要在本次「暂不渲染」阶段执行这些媒体生成命令；仅由后续渲染任务执行。

## 重点审查

1. 从第 42 秒开始展示内嵌地图；历史侧栏不消失。不要误做成打开外部浏览器，或一边聊天一边挤在狭窄侧栏里看图。
2. 第 48–58 秒六个研究维度可辨认，种子文献单独作为起点。层级顺序正确，线条不穿过文字；每个示例标题不被截断。
3. 第 58–68 秒折叠、展开、缩放平移、搜索高亮、文献详情、返回对话均发生；光标与目标匹配。重点检查宽度收缩后的选中文献与右侧摘要。
4. 第 68–76 秒地图产物格式必须清楚；HTML / Markdown / JSON 为自动保存文件，不是凭空添加的 GUI 导出按钮。
5. 第 76–84 秒品牌地址稳定可读。影片结束前音乐自然收束，不在第 60 秒突然结束或开始重复。
6. 听整条草稿音轨，确认鼓组、旋律与界面点击不刺耳；检查原始 WAV 与最终 AAC 的响度和峰值。目标样本峰值 -1.2 dBFS 不等于编码后的真峰值保证。

可用 FFmpeg/ffprobe 检查（若已安装）：

```bash
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate,nb_frames,sample_rate,channels -of json out/promo-litmap-84s.mp4
ffmpeg -v error -i out/promo-litmap-84s.mp4 -f null -
ffmpeg -hide_banner -i out/promo-litmap-84s.mp4 -af ebur128=peak=true -f null -
```

预期视频 2520 帧 / 30 fps / 1920×1080；音轨 48 kHz 双声道。AAC 封装可能使文件总时长略超 84 秒，不应以此当作画面丢帧。像素格式可能显示 `yuv420p` 或全范围标记 `yuvj420p`，都应验证实际播放器兼容性。

## 修改位置

- 只调整树场景布局：`src/commercial/TreeScenes.tsx`。
- 示例文本与交互帧：`src/commercial/tree-demo.json`。不要更换成未核实的真实论文数据。
- 时间线：`src/film.json`；时长修改后必须更新分镜。编曲段落跟随场景定位，音效跟随交互帧。
- 共用风格：`src/commercial/design.tsx`；保留原片视觉延续。
- 音乐：`scripts/audio-plan.mjs` 定义段落及提示音时间，`scripts/gen_audio.mjs` 合成 PCM。

如改过视觉源码，重新做相关帧审查，再渲染。遵循仓库 AGENTS.md：修改完成后提交新的 commit。

## 常见阻塞

- `connect EACCES 127.0.0.1`：Chromium 本机调试端口被沙箱拦截，应在获准的本地渲染环境执行；不是缺少学术 API Key。
- `Can't resolve ./audio/track.wav`：先运行 `npm run gen-audio`，或使用带 pre 钩子的 `npm run render`，别跳过音频准备。
- 第 60 秒后音乐空白：错误复用了旧轨，重新生成并检查 WAV 时长应为 84 秒。
- 字体/行宽异常：先修字体环境，不能用缩小整片文字掩盖缺字。

## 最终交付

交付 `out/promo-litmap-84s.mp4`，可选封面图和审片拼图。报告实际检查过的内容、任何剩余限制及修改后的 commit。不得声称此源码交付阶段已通过视觉验收。

## 交付记录（2026-10-22 已渲染并验收）

- 环境：Windows 11 / Node v24.20.0 / npm 11.19.0；复用现有 `node_modules`，未升级 Remotion 4.0.536；`node_modules/.remotion` 已有 chrome-headless-shell。
- 顺序：`npm run check` → `npm run gen-audio`（84.000 s / 48 kHz / 双声道，样本峰值 −1.2 dBFS，RMS −16.8 dBFS）→ `npm run render:draft` → `npm run preview`（44 张审片帧）→ 全分辨率复核帧 → `npm run render -- --concurrency=2`。
- 并发：渲染时可用物理内存仅约 2.2 GB，按本文件规则把最终渲染并发降为 2；**分辨率与时长未降**。
- 产物：`out/promo-litmap-84s.mp4`（21,456,588 字节）；修正前草稿 `out/promo-litmap-draft-pre-fix.mp4`；封面 `out/promo-litmap-84s-poster.jpg`；审片拼图 `out/review-contact-sheet.jpg`；审片帧 `out/review-litmap/`（44 张）；修复复核帧 `out/fix-*.png`；旧 60 秒素材已移入 `out/legacy-60s/`。
- 实测（ffprobe / ffmpeg）：H.264 High、1920×1080、`yuvj420p`、30/1 fps、2520 帧、时长 84.011 s；AAC LC 48 kHz 双声道 317 kbps；`-f null -` 全解码无错误，`nb_read_frames=2520`。
- 成片响度（AAC）：Integrated −14.8 LUFS，LRA 6.5 LU，True peak −1.1 dBFS。
- 配乐结构实测（WAV 分段平均电平）：32–42 s −14.9 dB（第一峰）→ 42–48 s −17.6 dB（bridge）→ 48–58 s −14.8 dB（第二峰）→ 58–60 s −18.5 dB → 60–76 s −16.7 dB → 76–80 s −23.3 dB → 80–84 s −23.8 dB，83.0 s 后自然淡出（无第 60 秒断裂或重复）。
- 审片：44 张审片帧 + 修复后全分辨率帧由 4 名审片与 Lead 实看（分工：镜头06/07、镜头08 折叠缩放、镜头08 搜索详情返回、镜头09/10 + 0–42 秒回归）。修复内容见 commit `ac18d22`，修复后相关帧二次复核 PASS。
- 已知限制（审片判定不阻塞）：详情面板展开后（63.2–66.5 s）画布左缘把根主题节点裁成深色块、文字不可见，左栏与地图页头保留同名主题；缩放终态（60.3–63.2 s）根节点左缘裁约 30 px、首字略缺。二者是「1.16 倍缩放 + pan −180」下同时保证选中文献与摘要完整可读的取景取舍。片尾最后约 1 秒淡出至 −60 dB 以下属设计淡出。
- 独立源码包已按新源码重新生成并通过 SHA-256 校验：`out/delivery/promo-litmap-84s-source.zip`（24 个文件）。
