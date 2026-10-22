// Text-only export: storyboard, exact narration, subtitles, chapter markers.
import fs from 'node:fs';
import path from 'node:path';
import {root,lesson,scenes,cues,totalFrames,duration,time} from './lesson.mjs';
const write=(name,text)=>fs.writeFileSync(path.join(root,name),text);
let board=`# 零基础视频教程分镜脚本\n\n${time(duration)} / ${lesson.width}×${lesson.height} / ${lesson.fps} fps / ${totalFrames} 帧。\n\nWindows EXE 为主线；补充 A 是 .env，补充 B 是源码启动。普通用户不需要同时完成三种配置路径。所有图形为 SVG 矢量界面，示例响应与文献不是实际检索输出。\n\n核对产品代码：\`${lesson.sourceCommit}\`（${lesson.checkedDate}）。尚未生成新音频、样帧或视频。\n\n`;
board+='## 统一导演规则\n\n左侧每次只给一个操作；右侧对应界面高亮，光标约 0.4 秒出现、2 秒到位、3 秒给出点击反馈或进入下一状态。字幕与逐句解说同步；每句保留 6–11 秒。步骤间轻微上移淡入，背景线条缓慢移动，避免过快转场干扰阅读。长命令、密钥字段和文件名固定停留，允许暂停。设置表单、文件选择、聊天气泡、计划卡、树图、结果卡、错误排查分别使用不同矢量构图。\n\n旁白为完整教学内容，不应删成广告口号。音乐是安静铺底，配音时进一步压低。原 84 秒宣传片不参与本教程。\n\n';
let voice='# 逐句配音稿\n\n时间与字幕由同一份 lesson.json 导出。以句为单位生成语音，不要整篇随意配速。\n\n';
let chapters='',last='';
for(const s of scenes){
 if(s.chapter!==last){chapters+=`${time(s.from/lesson.fps)} ${s.chapter}\n`;last=s.chapter;}
 board+=`## ${time(s.from/lesson.fps)}–${time((s.from+s.frames)/lesson.fps)}｜${s.title}\n\n- 章节：${s.chapter}\n- 画面模板：\`${s.view}\`；场景 ID：\`${s.id}\`\n- 完成标志：${s.goal}\n- 全局帧：${s.from}–${s.from+s.frames}（右端不含）\n\n| 时间 | 画面高亮与操作 | 逐句解说 / 屏幕字幕 |\n| --- | --- | --- |\n`;
 for(const c of cues.filter(c=>c.scene===s.id)){
  const range=`${time(c.from/lesson.fps)}–${time((c.from+c.frames)/lesson.fps)}`;
  board+=`| ${range} | ${c.action}（焦点：\`${c.focus}\`） | ${c.voice} |\n`;
  voice+=`## ${String(c.id).padStart(3,'0')} · ${range} · ${s.title}\n\n${c.voice}\n\n`;
 }
 if(s.payload.commands)board+='\n屏幕完整命令（逐条执行，不能把两条粘成一行）：\n\n```powershell\n'+s.payload.commands.join('\n')+'\n```\n';
 if(s.payload.url)board+='\n屏幕链接：'+s.payload.url+'\n';
 board+='\n';
}
board+='## 关键内容约束\n\n- GUI 保存后生效；修改 .env 后完整重启。非空 GUI 配置优先于环境变量，系统环境变量可优先于 .env。\n- 默认交大地址只适合有对应权限的账号，不称为人人免费的通用接口。\n- 不展示真实 Key；不画不存在的测试连接按钮；就绪不等于 API 成功。\n- 先在翻译卡确认页查看地图，返回后再确认普通检索；结果阶段提供细化检索/结束。\n- 已生成 HTML 可离线浏览，检索/生成新图需要联网；文献树不是引文网络。\n- 发布包可能晚于源码。教程按核对的源码行为示意，渲染时应检查发布版本是否含这些按钮。\n- 字体和光标位置还需后续样帧审查，本次不以静态检查代替视觉验收。\n';
const stamp=sec=>{const ms=Math.round(sec*1000);return `${String(Math.floor(ms/3600000)).padStart(2,'0')}:${String(Math.floor(ms/60000)%60).padStart(2,'0')}:${String(Math.floor(ms/1000)%60).padStart(2,'0')},${String(ms%1000).padStart(3,'0')}`;};
const srt=cues.map(c=>`${c.id}\n${stamp(c.from/lesson.fps)} --> ${stamp((c.from+c.frames)/lesson.fps)}\n${c.voice}\n`).join('\n');
write('STORYBOARD.md',board);write('NARRATION.md',voice.trimEnd()+'\n');write('subtitles.srt',srt);write('CHAPTERS.txt',chapters);write('narration-cues.json',JSON.stringify(cues.map(c=>({id:c.id,start:c.from/lesson.fps,seconds:c.frames/lesson.fps,text:c.voice,scene:c.scene})),null,2)+'\n');
console.log(`Text files generated: ${scenes.length} scenes, ${cues.length} voice cues, ${time(duration)}. No media rendered.`);
