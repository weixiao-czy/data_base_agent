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
    ] + collect_submodules('mcp') + collect_submodules('litmap'),
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
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", spec_file, "--clean", "--noconfirm"],
        cwd=project_dir,
    )

    # 必须检查返回码：旧输出目录删不掉时 PyInstaller 会中途失败，
    # 但 dist 目录依然存在，只看「目录在不在」会误报成功。
    if result.returncode != 0:
        print(f"\n打包失败（PyInstaller 返回码 {result.returncode}）。")
        print("常见原因：旧 dist 目录删不掉（文件被占用或权限不足）。")
        print("请关闭正在运行的 exe，或手动删除 dist/LiteratureSearchAgent 后重试。")
        sys.exit(result.returncode)

    dist_dir = os.path.join(project_dir, "dist", "LiteratureSearchAgent")
    if os.path.exists(dist_dir):
        # .env 不打进包内（避免把密钥固化到二进制里，分享时容易泄漏），
        # 改为复制到 exe 同级目录。程序启动时会优先读那里。
        env_src = os.path.join(project_dir, ".env")
        if os.path.exists(env_src):
            import shutil
            shutil.copy2(env_src, os.path.join(dist_dir, ".env"))
            print("\n已把 .env 复制到 exe 同级目录。")
            print("注意：该文件包含 API 密钥，分享 dist 目录前请先删除它。")
        else:
            print("\n未找到 .env —— exe 将无法调用大模型，只能以模拟模式运行。")
            print("请复制 .env.example 为 .env 并填入密钥。")
        print(f"\n打包成功！exe 位于: {dist_dir}")
    else:
        print("\n打包失败，请检查错误信息。")


if __name__ == "__main__":
    build()
