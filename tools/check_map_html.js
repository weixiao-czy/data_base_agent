// 用 jsdom 实跑 literature map 的内联脚本，捕获运行时错误并检查渲染结果
const fs = require('fs');
const { JSDOM } = require('jsdom');

const file = process.argv[2];
const html = fs.readFileSync(file, 'utf8');

const errors = [];
const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  beforeParse(win) {
    win.addEventListener('error', e => errors.push('window.error: ' + e.message));
    // jsdom 不做布局，getBoundingClientRect 全 0，给个合理视口
    win.HTMLElement.prototype.getBoundingClientRect = function () {
      return { width: 1400, height: 900, top: 0, left: 0, right: 1400, bottom: 900, x: 0, y: 0 };
    };
  },
});

const doc = dom.window.document;
const svg = doc.getElementById('svg');
const nodes = doc.querySelectorAll('#nodes .node');
const edges = doc.querySelectorAll('#edges .edge');
const texts = [...doc.querySelectorAll('#nodes .node text')].map(t => t.textContent);

console.log('节点数:', nodes.length);
console.log('连线数:', edges.length);
console.log('画布尺寸:', svg.getAttribute('data-w'), 'x', svg.getAttribute('data-h'));
console.log('统计栏:', doc.getElementById('stats').textContent);
console.log('前 8 个节点标签:');
texts.filter(Boolean).slice(0, 8).forEach(t => console.log('  ·', t));

// 检查节点是否有坐标 / 是否全部堆在原点
const rects = [...nodes].map(n => {
  const m = /translate\(([-\d.]+),([-\d.]+)\)/.exec(n.getAttribute('transform') || '');
  return m ? [+m[1], +m[2]] : null;
});
const bad = rects.filter(r => !r || (!r[0] && !r[1]));
console.log('坐标异常节点:', bad.length);

// 溢出检查：文字估算宽度是否超出节点框
let overflow = 0;
nodes.forEach(n => {
  const rect = n.querySelector('rect');
  const w = +rect.getAttribute('width');
  const t = n.querySelector('text');
  if (!t) return;
  const fs = +(t.getAttribute('font-size') || 12);
  let est = 0;
  for (const ch of t.textContent) {
    est += /[\u4e00-\u9fa5]/.test(ch) ? fs : fs * 0.56;
  }
  const x = +(t.getAttribute('x') || 0);
  if (est + x > w - 4) overflow++;
});
console.log('文字溢出节点:', overflow);

// 侧栏初始状态
console.log('侧栏标题:', doc.getElementById('side-title').textContent);

// 交互：点开一个检索方向节点，应展开出文献叶子节点
const before = doc.querySelectorAll('#nodes .node').length;
// 检索方向节点固定在第 3 列（x 由 render.py 的列宽推算，约 632）
const target = [...nodes].find(n => {
  const m = /translate\(([-\d.]+),/.exec(n.getAttribute('transform') || '');
  return m && Math.abs(+m[1] - 632) < 2;
});
if (target) {
  target.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  const after = doc.querySelectorAll('#nodes .node').length;
  console.log(`交互展开: ${before} → ${after} 个节点`, after > before ? '✅' : '❌ 未展开');
  console.log('侧栏标题:', doc.getElementById('side-title').textContent);
} else {
  console.log('交互展开: 跳过（没有可点击的检索方向节点）');
}

if (errors.length) {
  console.log('\n❌ 运行时错误:');
  errors.forEach(e => console.log('  ', e));
  process.exit(1);
}
if (!nodes.length) {
  console.log('\n❌ 未渲染出任何节点');
  process.exit(1);
}
console.log('\n✅ 渲染检查通过');
