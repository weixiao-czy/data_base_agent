"""
检索提供者抽象接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SearchProvider(ABC):
    """检索提供者抽象基类"""
    
    @abstractmethod
    def search(self, query: str, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """
        执行检索
        
        Args:
            query: 检索查询词
            limit: 返回结果数量
            **kwargs: 其他参数
            
        Returns:
            论文列表，每个论文包含元数据、摘要、URL、BibTeX
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查检索服务是否可用"""
        pass
