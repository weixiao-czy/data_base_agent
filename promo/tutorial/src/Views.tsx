import React from 'react';
import { interpolate } from 'remotion';
import { Box, Text, Frame, AppBase, color } from './vector';
import { clamp } from './vector';
import { LessonScene } from './timeline';

type Props={scene:LessonScene;focus:string;f:number};
const dimensions=['综述与奠基','核心方法','任务与应用','数据集与评测','挑战与开放问题','前沿与最新进展'];
const query='我想研究大模型如何帮助文献检索，先做一篇方法综述。';
const payload=(s:LessonScene)=>s.payload as {url?:string;file?:string;commands?:string[];note?:string};

function Settings({scene,focus,f}:Props){
 if(focus==='save'&&f>=105)return <AppBase focus="none" f={f} status="就绪"><Text x={270} y={275} text="配置已保存" size={39} bold/><Text x={270} y={345} text="下一步：发送一个研究问题，验证接口能否调用。" size={28} width={870}/></AppBase>;
 const opened=focus!=='settings'||f>=90, sci=['sci','fallback','npx'].includes(focus);
 return <AppBase focus={focus} f={f} status="未配置 API Key">
  {!opened&&<Text x={300} y={300} text="先打开左下角设置" size={38}/>}
  {opened&&<><rect x={181} y={117} width={1048} height={531} fill="#172B27" opacity={.12}/>
    <rect x={290} y={138} width={850} height={465} rx={24} fill="white" stroke={color.line}/>
    <Text x={325} y={182} text="设置" size={31} bold/>
    {['LLM 配置','SciMaster','常规'].map((label,i)=><Box key={label} x={325+i*255} y={202} w={240} h={46} label={label} active={focus==='llm'&&i===0||sci&&i===1} fill={(sci?i===1:i===0)?'#EDF4E2':'white'} f={f} click size={22}/>)}
    <Text x={325} y={299} text="API Key:" size={25}/>
    <Box x={510} y={267} w={590} h={51} label={sci?'留空（主线不配置）':scene.id==='fill_key'&&f<90?'粘贴真实密钥':'●●●●●●●●●●●●'} active={focus==='key'||focus==='mask'||focus==='sci'} f={f} click size={25}/>
    <Text x={325} y={379} text="Base URL:" size={25}/>
    <Box x={510} y={347} w={590} h={51} label={sci?'https://scimaster.bohrium.com/api/v1':focus==='defaults'?'https://models.sjtu.edu.cn/api/v1':'〈服务商提供的完整 API 地址〉'} active={focus==='url'||focus==='defaults'} f={f} click size={23}/>
    {!sci&&<><Text x={325} y={459} text="模型:" size={25}/><Box x={510} y={427} w={590} h={51} label="〈该平台支持的模型 ID〉" active={focus==='model'} f={f} click size={24}/></>}
    <Text x={325} y={520} text={sci?'没有专用密钥也能使用 Crossref / arXiv':'保存后立即生效；留空项读取环境配置。'} width={630} size={20} fill={color.gray}/>
    <Box x={830} y={541} w={120} h={44} label="取消" size={22}/><Box x={980} y={541} w={120} h={44} label="保存" active={focus==='save'} f={f} click size={22}/>
    {focus==='npx'&&<Box x={335} y={427} w={755} h={56} label="SciMaster：专用 Key + Node.js / npx" size={24} active f={f}/>}
  </>}
 </AppBase>;
}
function Chat({scene,focus,f}:Props){
 const verify=scene.id==='verify', clarify=scene.id==='clarify';
 return <AppBase focus={focus} f={f} status={focus==='ready'?'就绪（仅代表配置存在）':'研究对话'}>
  {verify&&focus==='ready'?<><Box x={270} y={220} w={820} h={130} fill="#FFF0E7"/><Text x={305} y={272} text="就绪 ≠ 连接测试通过" size={38} bold/><Text x={305} y={318} text="下一步：实际发送研究问题，检查回复与错误提示。" size={24}/></>:
  <><Box x={380} y={155} w={780} h={114} fill="#E7EEDC"/><Text x={405} y={195} text={query} width={730} size={25}/>
   {(clarify||verify&&f>=90)&&<><Box x={225} y={305} w={760} h={93} fill="#F3F5EE"/><Text x={250} y={345} text="你更关注检索方法，还是应用体验？" size={26}/>
    <Box x={235} y={427} w={250} h={56} label="检索方法" active={focus==='choice'} click f={f}/><Box x={510} y={427} w={250} h={56} label="应用体验"/>
    <Box x={785} y={427} w={180} h={56} label="其他…" active={focus==='other'} click f={f}/></>}
   {focus==='warning'&&<><Box x={225} y={307} w={940} h={182} fill="#FFF0E7" active f={f}/><Text x={250} y={352} text="请留意：模拟模式 / LLM 调用失败" size={30} bold/><Text x={250} y={405} text="出现这些提示时，先回设置排查配置，\n再用新对话验证。示例气泡不代表真实连通。" width={880} size={25}/></>}
  </>}
  <Box x={220} y={546} w={830} h={71} label={focus==='other'?'补充自己的研究方向…':focus==='input'?query:'描述你的研究兴趣…'} size={22} active={focus==='input'} f={f} click/>
  <Box x={1070} y={546} w={120} h={71} label="发送 ↑" size={23} active={focus==='input'&&f>=100} f={f} click/>
 </AppBase>;
}
function Plan({scene,focus,f}:Props){
 const loading=['loading','waiting'].includes(focus);
 const afterMap=['return','search'].includes(scene.id);
 const actions=afterMap?['确认，开始检索','重新生成树形图','返回调整计划（请说明）','跳过检索']:['确认，开始检索','需要调整（请说明）','重新生成','跳过检索','以树形图查看文献结构'];
 return <AppBase focus={focus} f={f} status="需求翻译卡 / 计划确认">
  <Box x={220} y={145} w={440} h={458} fill="#FAFBF7"/>
  <Text x={250} y={192} text="需求翻译卡" size={31} bold/>
  <Box x={240} y={218} w={400} h={226} fill="#FAFBF7" active={focus==='question'} f={f}/>
  <Text x={250} y={247} text="研究问题" size={22} fill={color.gray}/><Text x={250} y={284} text="大模型如何辅助文献检索？" width={380} size={26}/>
  <Text x={250} y={365} text="关键词 / 查询建议" size={22} fill={color.gray}/><Text x={250} y={403} text="LLM · 查询扩展 · 检索增强" width={370} size={24}/>
  <Box x={240} y={462} w={400} h={108} active={focus==='uncertainty'} f={f}/><Text x={256} y={494} text="不确定性：" size={22} fill={color.gray}/><Text x={256} y={532} text="是否纳入多模态模型？" size={24}/>
  <Text x={710} y={182} text={afterMap?'导图看完了，接下来怎么继续？':'这个计划看起来如何？'} size={25}/>
  {actions.map((label,i)=><Box key={label} x={700} y={211+i*73} w={480} h={58} label={label} size={24} active={focus==='confirm'&&i===0||focus==='tree'&&i===4||focus==='uncertainty'&&i===1} click f={f}/>)}
  {loading&&<><rect x={181} y={117} width={1048} height={531} fill="#172B27" opacity={.15}/><Box x={310} y={265} w={790} h={190} fill={color.ink}/><Text x={345} y={321} text={scene.id==='tree_entry'?'正在构建文献树形图…':'正在检索…'} size={36} fill={color.green}/><Text x={345} y={375} text="等待状态更新，不要重复点击。" size={27} fill="white"/><Text x={345} y={421} text="过程已压缩示意，实际耗时取决于网络与检索规模。" size={22} fill="#B6CAB6"/></>}
 </AppBase>;
}
function Tree({scene,focus,f}:Props){
 if(focus==='return'&&f>=105)return <Plan scene={scene} focus="none" f={f}/>;
 const detail=focus==='detail'&&f>=90, searched=['search','detail'].includes(focus), collapsed=focus==='collapse'&&f>=90;
 const zoom=focus==='zoom'?interpolate(f,[75,105,135,165],[0,1,1,0],clamp):0;
 return <Frame title="文献检索需求翻译 Agent / 内嵌文献地图 · 教学示意">
  <Box x={945} y={65} w={260} h={43} label="返回对话" active={focus==='return'} f={f} click size={23}/>
  <Box x={20} y={65} w={345} h={43} label={searched?'⌕ 查询扩展':'搜索节点或文献标题…'} size={22} active={focus==='search'} f={f} click/>
  <Box x={380} y={65} w={150} h={43} label="全部展开" size={21}/><Box x={545} y={65} w={180} h={43} label="收起到维度" size={21} active={focus==='collapse'} click f={f}/><Box x={740} y={65} w={150} h={43} label="适应窗口" size={21} active={focus==='zoom'&&f>=150} click f={f-60}/>
  <g transform={detail?'translate(0,75) scale(.69)':`translate(${-45*zoom},${-30*zoom}) scale(${1+.08*zoom})`}>
   <Box x={24} y={308} w={200} h={79} label="研究主题" fill={color.ink} ink="white" size={28} active={focus==='root'} f={f}/>
   <Text x={31} y={431} text="大模型辅助文献检索" width={200} size={20} fill={color.gray}/>
   <path d="M224 345C255 345 255 145 290 145" fill="none" stroke="#7E9B64" strokeWidth={3}/><Box x={290} y={122} w={235} h={45} label="种子文献" size={23} fill="#EDF3E5"/>
   {dimensions.map((d,i)=>{const y=197+i*66, match=i===1,grow=focus==='root'?interpolate(f,[i*8,i*8+25],[0,1],clamp):1;return <g key={d} opacity={(searched&&!match?.25:1)*grow}>
    <path d={`M224 345C260 345 260 ${y+23} 290 ${y+23}`} fill="none" stroke={i%2?color.blue:'#78A486'} strokeWidth={2} pathLength={1} strokeDasharray={1} strokeDashoffset={1-grow}/>
    <Box x={290} y={y} w={235} h={46} label={d} size={22} fill={i%2?'#EDF2FF':'#EAF3E6'} active={focus==='survey'&&i===0} f={f} click/>
    {!collapsed&&!(focus==='survey'&&i===0&&f<90)&&<><path d={`M525 ${y+23}H570M795 ${y+23}H840`} stroke="#99AC93" strokeWidth={2}/><Box x={570} y={y} w={225} h={46} label={match?'查询扩展':'示例检索方向'} size={22} active={searched&&match} f={f}/><Box x={840} y={y} w={365} h={46} label={match?'示例：查询扩展研究':'示例：相关文献'} size={22} active={focus==='paper'&&i===0||focus==='detail'&&match} f={f} click/></>}
   </g>})}
  </g>
  {detail&&<><Box x={850} y={133} w={355} h={467} fill="#F8FAF3"/><Text x={875} y={178} text="文献详情 / 示例" size={24} fill={color.blue}/><Text x={875} y={231} text="查询扩展研究" size={30} bold width={300}/><Text x={875} y={294} text="研究维度：核心方法\n检索方向：查询扩展" size={23} width={310}/><Text x={875} y={391} text="示例摘要：比较不同查询策略对文献检索的影响，帮助判断这篇文献是否值得深入阅读。" width={300} size={24}/></>}
  {focus==='zoom'&&f<150&&<Text x={580} y={604} text="滚轮缩放 · 在空白处按住拖动" size={23} fill={color.blue}/>}
  {focus==='browser'&&<><Box x={220} y={230} w={820} h={240} fill="#FFF2E8"/><Text x={260} y={290} text="内嵌预览不可用？" size={36} bold/><Text x={260} y={349} text="可用浏览器打开已生成的 HTML。\n这与大模型密钥是否正确是两件事。" size={28} width={740}/></>}
  <Text x={25} y={627} text="教学示例文献 · 层级关系不等于引用关系" size={19} fill={color.gray}/>
 </Frame>;
}
function Result({focus,f}:Props){return <AppBase focus={focus} f={f} status="检索结果">
 <Box x={224} y={157} w={955} h={384} fill="#FAFBF7"/><Text x={254} y={205} text="示例：大模型辅助文献检索的方法研究" size={30} bold width={885}/>
 <Text x={254} y={256} text="年份 / 来源 / 作者等元数据：以真实返回内容为准" size={23} fill={color.gray}/>
 <Box x={245} y={292} w={915} h={142} active={focus==='abstract'} f={f}/><Text x={268} y={334} text="摘要：这是一段教学示例，展示如何判断文献\n是否涉及你的研究问题。不能把标题相似当作\n内容一定相关。" size={26} width={860}/>
 <Box x={250} y={463} w={400} h={53} label="论文标题 / 来源链接 ↗" active={focus==='link'} f={f} click size={24}/>
 <Text x={254} y={589} text="没有摘要或链接时，请到数据源进一步核对。" size={23} fill={color.gray}/>
 </AppBase>;}
function Files({scene,focus,f}:Props){
 const exporting=scene.view==='export',history=scene.view==='history';
 if(scene.id==='launch'&&focus==='exe'&&f>=105)return <AppBase focus="none" f={f} status="未配置 API Key"><Text x={270} y={280} text="程序已打开" size={39} bold/><Text x={270} y={350} text="接下来，准备密钥、接口地址和模型名称。" size={29} width={850}/><Box x={230} y={546} w={800} h={65} label="描述你的研究兴趣…" size={25}/><Box x={1055} y={546} w={135} h={65} label="发送"/></AppBase>;
 if(f<90&&((exporting&&focus!=='files')||history&&focus!=='offline'))return <AppBase focus={focus} f={f} status="从顶部工具栏选择操作"><Text x={265} y={310} text="先点高亮按钮，再选择文件或保存位置。" size={32} width={880}/></AppBase>;
 const header=exporting?'保存文件 · 教学示意':history?'选择已保存的地图 HTML · 教学示意':'文档 / 文献检索助手 · 教学示意';
 return <Frame title={header}>
  <rect x={0} y={53} width={210} height={596} fill="#EDF1E8"/>{['文档','文献检索助手','output','maps'].map((s,i)=><Text key={s} x={25+i*10} y={110+i*72} text={s} size={24} fill={i===1?color.ink:color.gray}/>)}
  <Text x={250} y={108} text={history?'文献检索助手 / output / maps':exporting?'选择你能找得到的保存位置':'把程序放在自己新建的文件夹里'} size={27} width={900}/>
  {(exporting||history?['研究计划.txt','检索结果.txt','研究主题.html','研究主题.md','研究主题.json']:['LiteratureSearchAgent.exe','output / maps','（可选）.env']).map((name,i)=><Box key={name} x={250} y={145+i*66} w={905} h={54} label={name} size={26} active={focus==='exe'&&i===0||focus==='files'&&i>=2||focus==='import'&&i===2||focus==='card'&&i===0||focus==='result'&&i===1} f={f} click={i===0||focus==='import'}/>)}
  {history&&focus==='recent'&&<><Box x={300} y={138} w={790} h={260} fill="#F5F8F0"/><Text x={332} y={190} text="聊天页 → 最近地图" size={32} bold/><Box x={330} y={221} w={710} h={60} label="选择以前生成的研究主题" active f={f} click/><Text x={332} y={344} text="或者：打开其他文件…" size={27}/></>}
  {focus==='offline'&&<Text x={250} y={568} text="已生成 HTML：离线浏览\n新检索 / 新地图：仍需联网" size={25} fill={color.blue}/>}
  {exporting&&<><Text x={250} y={552} text={focus==='files'?'地图文件自动保存到 output/maps':'文件名：'+(focus==='card'?'研究计划.txt':'检索结果.txt')} size={25}/><Box x={1015} y={572} w={140} h={48} label="保存" active={focus!=='files'} f={f} click/></>}
  {!exporting&&!history&&<Box x={260} y={440} w={880} h={87} label="看到主窗口后，再去设置 API 配置。" size={29} fill="#E7F3D1"/>}
 </Frame>;
}
function Credentials({scene,focus,f}:Props){
 if(scene.view==='provider') return <Frame title="服务商 API 控制台 · 通用示意，入口名称以实际平台为准">
  <Text x={45} y={115} text="同一家平台，准备三项信息" size={35} bold/>
  {['① 登录你有权限的 API 控制台','② API 密钥 / 密钥管理 → 创建密钥','③ 接口文档 → Base URL + 模型 ID'].map((t,i)=><Box key={t} x={70} y={160+i*120} w={1085} h={87} label={t} size={29} active={focus===[ 'console','create','docs'][i]} f={f} click/>)}
  <Text x={75} y={578} text="密钥只保存在自己的电脑；确认平台额度与调用权限。" size={25} fill={color.gray}/>
 </Frame>;
 return <Frame title="API 配置三件套">
  {['API Key','Base URL','模型 ID'].map((t,i)=><g key={t}><Box x={50+i*399} y={165} w={365} h={290} fill={i===1?'#ECF2FF':'#EEF5E3'} active={focus===['key','url','model'][i]} f={f}/><Text x={80+i*399} y={225} text={t} size={35} bold width={310}/><Text x={80+i*399} y={304} text={['你的调用钥匙\n不是登录密码','接口的地址\n不是聊天网址','平台的模型名称\n不是随便起名'][i]} size={28} width={300}/></g>)}
  <Text x={615} y={548} text="同一家服务商 · 同一个有权限的账号" size={32} anchor="middle"/>
 </Frame>;
}
function Release({scene,focus,f}:Props){return <Frame title="GitHub 项目发布页 · 教学示意">
 <Text x={40} y={109} text="weixiao-czy / data_base_agent" size={32} bold/><Text x={40} y={160} text={payload(scene).url||'github.com/weixiao-czy/data_base_agent/releases'} size={21} mono width={1160}/>
 <Box x={40} y={208} w={300} h={62} label="Releases / 发布版本" active={focus==='releases'} f={f} click/>
 <Text x={70} y={330} text="Assets / 下载文件" size={29} bold/><Box x={65} y={365} w={1090} h={75} label="LiteratureSearchAgent.exe" size={34} active={focus==='exe'} f={f} click/>
 <Text x={90} y={493} text="Source code (zip) 是源码，不是 Windows 程序。" size={25}/><Text x={90} y={553} text="发布包的功能可能晚于最新源码；请核对版本。" size={25} fill={color.gray}/>
</Frame>;}
function Env({focus,f}:Props){
 const lines=['OPENAI_API_KEY=〈你的真实模型密钥〉','OPENAI_BASE_URL=〈同平台的接口地址〉','OPENAI_MODEL=〈该平台可用的模型ID〉','SCIMASTER_API_KEY='];
 return <Frame title=".env · 可选配置方式 · 所有尖括号内容都必须替换">
  <Text x={40} y={107} text="位置：EXE 同级目录 / 源码项目根目录" size={29} bold/>
  <Box x={40} y={137} w={1145} h={66} label={focus==='extension'?'.env   ✓       .env.txt   ×':'文件名：.env      编码：UTF-8'} active={focus==='extension'||focus==='location'} f={f} size={29}/>
  {lines.map((line,i)=><Box key={line} x={50} y={236+i*66} w={1130} h={53} label={line} size={27} fill="#F6F8F2" active={focus==='key'&&i<3||focus==='blank'&&i===3} f={f}/>)}
  <Text x={55} y={556} text={focus==='priority'?'优先顺序：设置页非空值 → 系统环境变量 → .env':focus==='restart'?'编辑 .env 后：保存文件 → 完整退出 → 重新打开程序':'这是填写模板；不要照抄占位文字。'} size={27} width={1120} fill={focus==='restart'?color.blue:color.gray}/>
 </Frame>;
}
function Source({scene,focus,f}:Props){
 const p=payload(scene);
 if(scene.view==='source')return <Frame title="项目主页 → 下载源码 → 解压">
  <Text x={50} y={117} text="github.com/weixiao-czy/data_base_agent" size={28}/>
  <Box x={60} y={158} w={270} h={63} label="Code" active={focus==='zip'} f={f} click size={30}/><Box x={380} y={158} w={700} h={63} label="Download ZIP → 解压" active={focus==='zip'} f={f} size={30}/>
  {['data_base_agent-master /','    gui_launcher.py','    requirements.txt','    src /','    .env.example'].map((t,i)=><Text key={t} x={100} y={300+i*54} text={t} size={27} mono/>)}
  <Text x={750} y={390} text="进入内层项目目录，\n确认看到这两个文件。" width={420} size={28} fill={color.blue}/>
 </Frame>;
 return <Frame title="Windows PowerShell · 在项目根目录执行">
  <rect x={1} y={53} width={1228} height={596} fill="#152923"/>
  <Text x={40} y={107} text={scene.id==='python'?'先安装 Python 3.12（python.org）':'当前目录：包含 gui_launcher.py 的文件夹'} size={27} fill={color.green}/>
  {(p.commands||[]).map((cmd,i)=><g key={cmd}><Text x={48} y={192+i*145} text={`${i+1}. 复制并执行这一条`} size={22} fill="#AEC5AE"/><Box x={40} y={217+i*145} w={1145} h={83} fill="#243E32" active={focus===['venv','pip'][i]||focus==='run'||focus==='terminal'} f={f}/><Text x={62} y={266+i*145} text={cmd} size={26} width={1100} mono fill="white"/></g>)}
  <Text x={48} y={551} text={p.note||''} size={25} width={1120} fill="#BDD0B7"/>
  {focus==='install'&&<><Box x={130} y={190} w={930} h={235} fill="#F0F4E8"/><Text x={170} y={254} text="Python 3.12 · Windows 安装器" size={35} bold/><Text x={170} y={326} text="☑ Add python.exe to PATH" size={32}/><Text x={170} y={385} text="安装后重新打开终端。" size={25}/></>}
 </Frame>;
}
const fixes:Record<string,[string,string,string]>={
 '401':['401 / 403','先核对 Key 和平台权限','同时检查 Base URL，保存后重新试一次。'],
 model:['模型不存在 / 无权限','从同一平台复制模型 ID','名称与账号权限都要匹配。'],
 '429':['请求受限 / 额度不足','查看平台额度与限流提示','稍后再试，避免连续点击发送。'],
 network:['连接失败 / 超时','核对 Base URL 与网络','校园接口可能需要平台规定的网络条件。'],
 proxy:['网页能打开，程序仍超时','当前模型客户端使用直连','系统代理设置不一定作用于程序。'],
 empty:['未找到相关论文','检查网络，换更明确的主题','需要时试试对应的英文术语。'],
 refine:['结果方向不对','细化检索（开始新对话）','结果页不再保留之前的计划确认菜单。']
};
function Errors({focus,f}:Props){const [symptom,action,note]=fixes[focus]||fixes.empty;return <Frame title="问题排查 · 按错误提示定位">
 <Box x={65} y={115} w={1100} h={115} fill="#FFF0E5"/><Text x={100} y={184} text={symptom} size={40} bold/>
 <path d="M615 250V290" stroke={color.orange} strokeWidth={5}/><path d="M602 276L615 291L628 276" fill="none" stroke={color.orange} strokeWidth={5}/>
 <Box x={65} y={320} w={1100} h={100} label={action} size={36} active f={f}/><Text x={90} y={491} text={note} size={29} width={1060}/><Text x={90} y={570} text="配置问题先修配置，不需要盲目重装程序。" size={26} fill={color.gray}/>
 </Frame>;}
function Roadmap({scene,focus,f}:Props){return <Frame title="操作路线 · 完成一轮就学会">
 {['打开程序','配置 API','描述主题','查看地图','检索与保存'].map((t,i)=><g key={t}><Box x={45+i*239} y={160+(i%2)*65} w={215} h={170} fill={i%2?'#EDF3FF':'#EDF6DA'} active={focus==='done'||i===0&&focus==='prepare'||i===4&&focus==='finish'} f={f}/><Text x={75+i*239} y={208+(i%2)*65} text={`0${i+1}`} size={25} fill={color.gray}/><Text x={75+i*239} y={266+(i%2)*65} text={t} size={28} width={175}/></g>)}
 <Text x={75} y={480} text={scene.id==='summary'?'主线到这里完成。后面的补充章节按需观看。':'一次只做一步。不熟悉的地方，暂停后照着操作。'} size={31} width={1090}/>
 <Text x={75} y={566} text="配置正确 → 明确研究问题 → 检查计划 → 找到并保存线索" size={26} fill={color.gray}/>
 </Frame>;}
export const Views:React.FC<Props>=props=>{
 switch(props.scene.view){
  case 'settings':return <Settings {...props}/>;
  case 'chat':return <Chat {...props}/>;
  case 'plan':return <Plan {...props}/>;
  case 'tree':return <Tree {...props}/>;
  case 'results':return <Result {...props}/>;
  case 'files':case 'export':case 'history':return <Files {...props}/>;
  case 'credentials':case 'provider':return <Credentials {...props}/>;
  case 'release':return <Release {...props}/>;
  case 'env':return <Env {...props}/>;
  case 'source':case 'terminal':return <Source {...props}/>;
  case 'errors':return <Errors {...props}/>;
  default:return <Roadmap {...props}/>;
 }
};
