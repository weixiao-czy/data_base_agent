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

    spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
    ['gui_launcher.py'],
    pathex=[r'{project_dir}', r'{src_dir}'],
    binaries=[],
    datas=[
        ('src/prompts', 'prompts'),
    ],
    hiddenimports=[
        'gui',
        'gui.main_window',
        'gui.chat_widget',
        'gui.agent_worker',
        'gui.settings_dialog',
        'gui.styles',
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
    ] + collect_submodules('mcp'),
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
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", spec_file, "--clean", "--noconfirm"],
        cwd=project_dir,
    )

    exe_path = os.path.join(project_dir, "dist", "LiteratureSearchAgent.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n打包成功！单文件 exe: {exe_path} ({size_mb:.1f} MB)")
    else:
        print("\n打包失败，请检查错误信息。")


if __name__ == "__main__":
    build()
