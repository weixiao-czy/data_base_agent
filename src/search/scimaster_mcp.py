"""
SciMaster MCP 调用实现
"""

import os
import json
from typing import List, Dict, Any, Optional
from .provider import SearchProvider
from dotenv import load_dotenv

load_dotenv()


class SciMasterMCPProvider(SearchProvider):
    """通过 MCP 调用 SciMaster 检索"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化 SciMaster MCP 客户端
        
        Args:
            api_key: SciMaster API Key
            base_url: SciMaster API base URL
        """
        self.api_key = api_key or os.getenv("SCIMASTER_API_KEY")
        self.base_url = base_url or os.getenv("SCIMASTER_BASE_URL", "https://api.scimaster.cn")
        self.search_limit = int(os.getenv("SEARCH_DEFAULT_LIMIT", "10"))
        self.timeout = int(os.getenv("SEARCH_TIMEOUT", "30"))
        
        # TODO: 初始化 MCP 客户端
        # 实际项目中需要集成 MCP SDK
        self.mcp_client = None
    
    def search(self, query: str, limit: int = None, **kwargs) -> List[Dict[str, Any]]:
        """
        通过 MCP 调用 search_papers
        
        Args:
            query: 检索查询词
            limit: 返回结果数量
            
        Returns:
            论文列表，每个论文包含：
            - title: 标题
            - abstract: 摘要
            - authors: 作者列表
            - url: 链接
            - doi: DOI
            - bibtex: BibTeX 条目
            - year: 发表年份
            - venue: 发表 venue
        """
        if limit is None:
            limit = self.search_limit
        
        if not self.is_available():
            print("[SciMaster] API Key 未配置或为占位符，跳过该来源")
            return []
        
        try:
            # TODO: 实现真正的 MCP 调用（集成 MCP SDK / scimaster-cli）
            # 在真正实现之前，本来源不返回任何结果，避免用 mock 数据冒充真实检索。
            print("[SciMaster] MCP 调用尚未实现，跳过该来源（改用 Crossref/arXiv）")
            return []
            
        except Exception as e:
            print(f"SciMaster MCP 调用失败: {e}")
            return []
    
    def is_available(self) -> bool:
        """检查 MCP 服务是否可用（占位符 Key 视为不可用）"""
        if not self.api_key:
            return False
        placeholder = "your-scimaster-api-key-here"
        if self.api_key.strip().lower() == placeholder:
            return False
        return bool(self.api_key)
