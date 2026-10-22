# 给后续渲染模型的交接说明

你拿到的是一份完成文案和动画实现的教程工程。请沿用内容，只处理依赖、预览、必要的排版修正、配音和最终输出。不要把完整教程压缩成宣传片，不要删除 API 配置或错误排查步骤。

本次作者未执行媒体生成。第一次实际预览、试听与视频渲染由你完成。视频总长 10:31；Composition ID 是 `Tutorial`；画幅 1920×1080；帧率 30；总帧数 18,930。

## 一、准备工作

1. 解压源码，进入含 `package.json` 的 `databaseagent-tutorial` 文件夹。不要在外层产品项目或旧宣传片目录运行命令。
2. 准备 Node.js 22 与 npm。中文字体需要 Microsoft YaHei、PingFang SC、Noto Sans CJK SC 或 Noto Sans SC 中至少一种。Linux 渲染机请实际安装中文字体，不能只把名字写进 CSS。
3. 执行下面命令。首次 Remotion 预览/渲染可能需要下载它使用的浏览器；保留网络与足够磁盘空间。

```powershell
npm ci
npm run check
```

这是静态检查，没有渲染。请保留 `package-lock.json`，不要因为版本号看起来旧而升级依赖。无需启动文献检索 Agent，无需 API Key，无需访问用户配置文件。

## 二、先检查样帧和动画

确认开始媒体制作后，再执行：

```powershell
npm run preview
```

此命令先检查工程、生成原创音乐，再为每个步骤输出点击前、点击后和结束状态的 PNG，位于 `out/preview`。共 234 张样帧，便于发现前后状态错误。想先少量检查，可调整 `scripts/preview.mjs` 的场景筛选；不要改变正式时间线。

需要逐段拖动播放时执行 `npm run start`。它打开 Remotion Studio，并会准备音乐。Studio 是人工检查工具，不是最终交付视频。

重点检查：

- 汉字没有方框或缺字；左侧操作说明、底部字幕、长 URL、文件名和命令没有遮挡或越界。
- `fill_key` 显示隐藏密钥；`fill_model` 保存后回到主界面；不能补画“测试连接”按钮。
- `tree_entry` 从计划确认菜单进入地图；`return` 后出现“确认，开始检索 / 重新生成树形图 / 返回调整计划 / 跳过检索”四项菜单。
- `tree_controls` 的折叠、缩放、搜索、详情与左侧讲解对应；点击文献后再出现详情。
- `exports`、`reopen` 的顶部按钮和文件类型一致；地图重开使用 HTML。
- 每次点击前有阅读时间，正文不做快速闪切。面板是教学简化示意，不要宣称它是实际录屏。

## 三、选择配音方式

### 方案 A：先出带字幕和背景音乐的审片版

```powershell
npm run render:draft
```

输出 `out/tutorial-draft.mp4`，分辨率 960×540，没有口播。适合先核对节奏，字幕清晰度以最终 1080p 样帧为准。正式无口播版执行 `npm run render`，输出 `out/tutorial-1080p.mp4`。

### 方案 B：Windows 离线中文语音

需要 Windows PowerShell、可被 **System.Speech / SAPI** 发现的中文语音、Python 3，以及 `ffmpeg` 可执行程序。系统里能朗读中文不代表 System.Speech 一定能发现那套语音。

```powershell
npm run voices
```

必须看到 `zh-CN` 语音。缺少时安装对应 SAPI 语音或使用方案 C。不要让英文语音读中文，更不要静默忽略配音失败。

```powershell
ffmpeg -version
python --version
npm run render:voiced
```

自动步骤：静态检查 → 生成音乐 → 按 78 段生成中文语音 → 对齐每句时间 → 渲染。输出 `out/tutorial-voiced-1080p.mp4`。

如需指定语音，可先运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/narrate.ps1 -VoiceName "你的已安装中文 SAPI 语音名称"
python scripts/assemble_voice.py
npm run prepare-media
npx remotion render Tutorial out/tutorial-voiced-1080p.mp4 --props=props-voice.json --codec=h264 --crf=18 --pixel-format=yuv420p --audio-bitrate=192k
```

最后一条直接调用 Remotion，以免 `render:voiced` 的准备阶段再次用默认语音覆盖刚指定的音色。

### 方案 C：外部中文配音或真人录音

以 `narration-cues.json` 为准，每条录制一份 PCM WAV，放到 `public/voice-cues/001.wav` 到 `078.wav`。每条只读 `text` 字段，编号与时间不读。保留统一声线和音量，读清 API Key、Base URL、模型 ID、文件名；英文缩写可自然口语化。

```powershell
python scripts/assemble_voice.py
npm run prepare-media
npx remotion render Tutorial out/tutorial-voiced-1080p.mp4 --props=props-voice.json --codec=h264 --crf=18 --pixel-format=yuv420p --audio-bitrate=192k
```

**外部配音不要执行 `npm run voice` 或 `npm run render:voiced`，它们会重新生成 SAPI 语音并覆盖逐句 WAV。**

对齐脚本在每句前后预留时间，最多加速到 1.20 倍，不截断正文。超长句会报出编号并停止。遇到超长句，重录那一句或增加 `src/lesson.json` 对应 `seconds`，再执行 `npm run docs`、`npm run check` 并重新生成音乐、字幕和整条配音。更改时间线后文档里的总时长描述也要同步更新。

`ffmpeg` 不在 PATH 时，可把环境变量 `FFMPEG` 设为它的完整路径。对齐脚本不需要额外 Python 第三方依赖。

## 四、声音和最终验收

先试听 `public/music.wav` 和 `public/narration.wav`，再听合成版。原音乐为 104 BPM 的轻节奏铺底，配音版音乐音量为无配音音轨基准的 0.22；实际仍需根据声音检查是否盖住解说。音量控制位于 `src/Tutorial.tsx`。这不是自动响度认证。

逐段确认：没有无声缺句、抢话、句尾截断、爆音；字幕与内容对应；转场不打断命令阅读。默认未添加点击音，避免遮住语音。检查前后各十秒与所有章节切换点，并完整审看最终成片。

在未修改时长的情况下，最终视频应为 1920×1080、30 fps、约 631 秒、H.264/AAC。可用 `ffprobe` 检查媒体信息，再用播放器确认画面声音正常。不要把“编译通过”写成“成片已验证”。

交付 MP4、SRT、章节文件，并保留最终修改后的源码和分镜。若仍在原 Git 项目中工作，遵守 `AGENTS.md`：每轮修改完成后创建新的 commit。
