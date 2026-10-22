# 文献检索 Agent：零基础视频教程源码

这是可独立交给另一位模型或剪辑人员的 Remotion 教程工程。**2026-10-22 已生成带中文配音的 1080p 成片：`out/tutorial-voiced-1080p.mp4`（1920×1080 / 30 fps / 18,930 帧 / 631 秒），验收数据见 [RENDER_HANDOFF.md](RENDER_HANDOFF.md) 末尾的「交付记录」。** 原商业宣传片位于上一级目录，本工程与它分开。

| 项目 | 内容 |
| --- | --- |
| 总时长 | 10 分 31 秒，34 个场景、78 段逐句解说 |
| 主线 | 00:00–08:22，Windows EXE → API 配置 → 第一次检索 → 文献地图 → 导出与重开 |
| 可选附录 | 08:22 起为 `.env`；09:14 起为源码运行；10:23 起为结束页 |
| 画面 | 1920×1080，30 fps，共 18,930 帧；SVG 矢量界面与图形 |
| 视觉节奏 | 奶白底、薄荷绿重点、橙色操作提示、蓝色分支；步骤进入动画、光标与点击反馈、树分支生长、平滑缩放、进度条 |
| 声音 | 原创 104 BPM 合成器背景音乐的生成源码；完整中文配音稿；可选 Windows 离线配音流程 |
| 内容依据 | 产品代码 `644e397db2e844b98370f2db8221dfc4d134f908`，核对日期 2026-10-22 |

## 先读哪些文件

- [STORYBOARD.md](STORYBOARD.md)：完整分镜，精确到场景帧区间、每句时间、操作与完成标志。
- [NARRATION.md](NARRATION.md)：78 段完整中文解说。
- [RENDER_HANDOFF.md](RENDER_HANDOFF.md)：直接交给下一位渲染模型的操作说明。
- [QUICKSTART.md](QUICKSTART.md)：观众可照着操作的文字速查，包含可复制命令。
- [FACT_CHECK.md](FACT_CHECK.md)：产品事实与对应源码，说明版本范围。
- `subtitles.srt` / `CHAPTERS.txt`：同步字幕与章节标记。

## 文件之间怎样配合

`src/lesson.json` 是教程文案、步骤时长与顺序的唯一内容来源。`src/timeline.ts` 自动计算每个镜头和步骤的帧数，`src/Views.tsx` 画具体界面，`src/vector.tsx` 提供矢量文字、按钮和光标，`src/Tutorial.tsx` 组合画面、字幕与音轨。

修改文案或时长后，在本目录执行 `npm run docs`，同步更新分镜、配音稿、SRT、章节与语音时间表，再执行 `npm run check`。只修改外观时不必重新生成文字文件。新增交互焦点时需要在 `Views.tsx` 中实现对应画面。

所有文献标题、回复和密钥框都是教学示意。没有嵌入真实 API Key、账号信息、网页截图或检索数据。渲染教程本身不需要任何模型 API Key，不调用文献检索服务。

## 仅检查，不渲染

安装 Node.js 22 与 npm 后，在本目录执行：

```powershell
npm ci
npm run check
```

这两条命令安装渲染工程依赖并做静态检查，不会生成音视频。`npm ci` 需要访问软件包仓库。使用锁文件固定依赖，不要临时升级 Remotion。

`npm run start`、`npm run preview`、`npm run render`、`npm run render:voiced` 属于后续预览或渲染操作，**不在本次已执行工作内**。它们的准备阶段会生成音乐。完整流程见交接说明。

## 音乐与配音

背景音乐由 `scripts/gen-audio.mjs` 逐样本生成，包含和弦铺底、琶音、低音和轻鼓组，无需外部音乐文件。生成位置是 `public/music.wav`。音色和混音尚未试听，下一位操作者应试听后决定是否调整。

配音有两条路径：Windows 中文 SAPI 离线语音，或者按 `narration-cues.json` 提供逐句 PCM WAV。两条路径都可以用 `scripts/assemble_voice.py` 对齐时长；它会在语速过快时明确停止，不截断讲解。不要把系统语音等同于真人或高质量商业配音。

SAPI 的默认语速偏慢：`scripts/narrate.ps1` 的 `-Rate` 默认 5（实测 `Microsoft Huihui Desktop` 在 Rate=0 时 68/78 句超过 1.20 倍对齐上限）。换语音时先跑一次 `npm run voice`，看是否还有超限句。

画面与配音合成时自动降低背景音乐音量。无配音版仍有完整屏幕字幕，方便低成本先审查。

## 源码打包

```powershell
python scripts/package_source.py
```

生成 `out/delivery/databaseagent-tutorial-source.zip` 与对应 SHA-256 文件。压缩包包含源码、依赖锁文件、文档、全部生成脚本和 MIT 许可证，不包含 `node_modules`、音视频或 `.env`。可在另一台机器单独解压使用，不依赖上一级宣传片目录。

本次静态检查不等于画面或音频验收。交接说明列出了后续样帧、中文字体、语音时长和声音混合的检查要点。
