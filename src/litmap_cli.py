"""
文献地图命令行入口（薄封装）

等价于 `python src/litmap/cli.py`，
单独放一个文件是为了让根目录下的调用方式与项目里 `gui_launcher.py` 的风格一致。

    python src/litmap_cli.py "retrieval augmented generation"
"""

import os
import sys

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from litmap.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
