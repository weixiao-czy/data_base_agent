"""
PyInstaller 打包脚本
生成独立 exe 文件
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
    [],
    exclude_binaries=True,
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

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LiteratureSearchAgent',
)
'''

    with open(spec_file, "w", encoding="utf-8") as f:
        f.write(spec_content)

    print("运行 PyInstaller 打包...")
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", spec_file, "--clean", "--noconfirm"],
        cwd=project_dir,
    )

    dist_dir = os.path.join(project_dir, "dist", "LiteratureSearchAgent")
    if os.path.exists(dist_dir):
        print(f"\n打包成功！exe 位于: {dist_dir}")
    else:
        print("\n打包失败，请检查错误信息。")


if __name__ == "__main__":
    build()
