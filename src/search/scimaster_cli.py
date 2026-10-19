"""
SciMaster CLI 降级实现
"""

import os
import subprocess
import json
from typing import List, Dict, Any
from .provider import SearchProvider
from dotenv import load_dotenv

load_dotenv()


class SciMasterCLIProvider(SearchProvider):
    """通过 CLI 子进程调用 SciMaster 检索（降级方案）"""
    
    def __init__(self):
        """初始化 CLI 提供者"""
        self.cli_command = "sci"  # SciMaster CLI 命令
        self.search_limit = int(os.getenv("SEARCH_DEFAULT_LIMIT", "10"))
        self.timeout = int(os.getenv("SEARCH_TIMEOUT", "30"))
    
    def search(self, query: str, limit: int = None, **kwargs) -> List[Dict[str, Any]]:
        """
        通过 CLI 调用检索
        
        Args:
            query: 检索查询词
            limit: 返回结果数量
            
        Returns:
            论文列表
        """
        if limit is None:
            limit = self.search_limit
        
        try:
            # 尝试使用 SciMaster CLI
            # sci search --query "xxx" --limit 10 --format json
            result = subprocess.run(
                [self.cli_command, "search", "--query", query, "--limit", str(limit), "--format", "json"],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                # 解析 JSON 输出
                try:
                    papers = json.loads(result.stdout)
                    return self._normalize_papers(papers)
                except json.JSONDecodeError:
                    print(f"CLI 输出解析失败: {result.stdout}")
                    return []
            else:
                print(f"CLI 调用失败: {result.stderr}")
                return []
                
        except FileNotFoundError:
            print(f"未找到 CLI 命令: {self.cli_command}")
            return []
        except subprocess.TimeoutExpired:
            print(f"CLI 调用超时（{self.timeout}秒）")
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
    
    def _normalize_papers(self, papers: List[Dict]) -> List[Dict[str, Any]]:
        """标准化论文数据格式"""
        normalized = []
        
        for paper in papers:
            normalized_paper = {
                "title": paper.get("title", "无标题"),
                "abstract": paper.get("abstract", "无摘要"),
                "authors": paper.get("authors", []),
                "url": paper.get("url", ""),
                "doi": paper.get("doi", ""),
                "year": paper.get("year", 0),
                "venue": paper.get("venue", ""),
                "bibtex": paper.get("bibtex", "")
            }
            normalized.append(normalized_paper)
        
        return normalized
