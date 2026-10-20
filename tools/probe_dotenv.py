"""验证 llm.client 的 .env 定位逻辑在「打包 + 任意启动位置」下是否可靠。

不真的打包，只把 sys.frozen 置为 True —— python-dotenv 正是用这个标志
决定从 __file__ 还是从 os.getcwd() 起算。
"""
import os
import sys

mode = sys.argv[1] if len(sys.argv) > 1 else "normal"
if len(sys.argv) > 2:
    os.chdir(sys.argv[2])  # 模拟不同的启动位置
if mode == "frozen":
    sys.frozen = True

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from llm.client import ENV_FILE
from dotenv import find_dotenv

key = os.getenv("OPENAI_API_KEY", "")
base = os.getenv("OPENAI_BASE_URL", "")
print(f"  模式          : {mode}")
print(f"  当前工作目录  : {os.getcwd()}")
print(f"  dotenv 原生查找: {find_dotenv() or '（未找到）'}")
print(f"  修复后加载位置: {ENV_FILE or '（未找到）'}")
print(f"  Key 长度      : {len(key)}  -> {'可用' if len(key) > 20 else '为空/占位'}")
print(f"  Base URL      : {base or '（未设置）'}")
