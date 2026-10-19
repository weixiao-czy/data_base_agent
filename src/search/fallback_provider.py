"""
组合检索提供者：按优先级依次尝试多个来源，失败自动降级
"""

from typing import List, Dict, Any
from .provider import SearchProvider


class FallbackSearchProvider(SearchProvider):
    """按优先级尝试多个检索来源，第一个返回非空结果的即为最终来源"""

    def __init__(self, providers: List[SearchProvider]):
        self.providers = providers

    def is_available(self) -> bool:
        return any(p.is_available() for p in self.providers)

    def search(self, query: str, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        for provider in self.providers:
            if not provider.is_available():
                continue
            try:
                results = provider.search(query, limit, **kwargs)
                if results:
                    return results
            except Exception as e:
                print(f"[降级] {provider.__class__.__name__} 失败: {e}")
                continue
        return []

    def active_provider_name(self) -> str:
        """返回当前可用的提供者名称（用于展示）"""
        for p in self.providers:
            if p.is_available():
                return p.__class__.__name__
        return "None"
