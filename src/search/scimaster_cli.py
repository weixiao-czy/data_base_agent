"""
SciMaster CLI 降级实现
"""

import subprocess
from typing import List, Dict, Any
from .provider import SearchProvider


class SciMasterCLIProvider(SearchProvider):
    """通过 CLI 子进程调用 SciMaster 检索（降级方案）"""
    
    def __init__(self):
        self.cli_command = "bohr"  # SciMaster CLI 命令
    
    def search(self, query: str, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """
        通过 CLI 调用检索
        
        Args:
            query: 检索查询词
            limit: 返回结果数量
            
        Returns:
            论文列表
        """
        # TODO: 实现 CLI 调用
        # bohr agents scimaster search-paper submit --mode high
        try:
            result = subprocess.run(
                [self.cli_command, "agents", "scimaster", "search-paper", "submit", "--mode", "high"],
                capture_output=True,
                text=True,
                timeout=30
            )
            # TODO: 解析输出
            return []
        except Exception as e:
            print(f"CLI 调用失败: {e}")
            return []
    
    def is_available(self) -> bool:
        """检查 CLI 是否可用"""
        try:
            result = subprocess.run(
                [self.cli_command, "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
