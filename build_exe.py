"""
PyInstaller 打包脚本
生成单文件 exe（无 _internal 目录）
"""

import os
import subprocess
import sys


def build():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_dir, "src")
    spec_file = os.path.join(project_dir, "databaseagent.spec")
    icon_path = os.path.join(project_dir, "assets", "icon.ico")

    if not os.path.exists(icon_path):
        print(f"缺少应用图标：{icon_path}")
        sys.exit(1)

    spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_submodules

# collect_submodules 是按「当前构建进程的 sys.path」去 import 包的，
# pathex 只影响 Analysis 阶段，管不到这里。不把 src 加进来，
# collect_submodules('litmap') 会静默返回 []，打出的 exe 就缺整个 litmap。
sys.path.insert(0, r'{src_dir}')

block_cipher = None

a = Analysis(
    ['gui_launcher.py'],
    pathex=[r'{project_dir}', r'{src_dir}'],
    binaries=[],
    datas=[
        ('src/prompts', 'prompts'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'gui',
        'gui.main_window',
        'gui.chat_widget',
        'gui.agent_worker',
        'gui.settings_dialog',
        'gui.styles',
        'gui.icons',
        'gui.map_panel',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebEngineCore',
        'agent',
        'agent.state_machine',
        'agent.clarifier',
        'agent.plan_card',
        'search',
        'search.provider',
        'search.real_search',
        'search.scimaster_mcp',
        'search.scimaster_cli',
        'search.fallback_provider',
        'llm',
        'llm.client',
        'llm.prompt_manager',
        'presentation',
        'presentation.render_results',
        'mcp',
        'mcp.client',
        'mcp.client.stdio',
    ] + collect_submodules('mcp') + collect_submodules('litmap') + collect_submodules('markdown_it'),
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LiteratureSearchAgent',
    icon=r'{icon_path}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''

    with open(spec_file, "w", encoding="utf-8") as f:
        f.write(spec_content)

    print("运行 PyInstaller 打包（单文件模式）...")
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", spec_file, "--clean", "--noconfirm"],
        cwd=project_dir,
    )

    # 必须检查返回码：旧输出删不掉时 PyInstaller 会中途失败，
    # 但旧产物依然存在，只看「文件在不在」会误报成功。
    if result.returncode != 0:
        print(f"\n打包失败（PyInstaller 返回码 {result.returncode}）。")
        print("常见原因：旧 dist 内容删不掉（文件被占用或权限不足）。")
        print("请关闭正在运行的 exe，或手动删除 dist 下的旧产物后重试。")
        sys.exit(result.returncode)

    exe_path = os.path.join(project_dir, "dist", "LiteratureSearchAgent.exe")
    if os.path.exists(exe_path):
        # .env 不打进包内、也不复制到 exe 旁边（密钥随安装包外发有泄漏风险）。
        # 用户在 GUI 左下角「设置」里填入 Key，保存到 ~/.databaseagent/config.json。
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n打包成功！单文件 exe: {exe_path} ({size_mb:.1f} MB)")
        print("提示：API Key 在 exe 内「设置」页配置，无需在 exe 旁放 .env。")
    else:
        print("\n打包失败，请检查错误信息。")


if __name__ == "__main__":
    build()
