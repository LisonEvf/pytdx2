"""缓存管理模块"""
import time
from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class CacheItem:
    """缓存项"""
    data: Any
    expire_time: float


class SimpleCache:
    """简单的内存缓存"""

    def __init__(self, ttl_seconds: int = 86400):  # 默认 24 小时
        self._cache: dict[str, CacheItem] = {}
        self._ttl = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        item = self._cache.get(key)
        if item is None:
            return None

        # 检查是否过期
        if time.time() > item.expire_time:
            del self._cache[key]
            return None

        return item.data

    def set(self, key: str, value: Any) -> None:
        """设置缓存数据"""
        self._cache[key] = CacheItem(
            data=value,
            expire_time=time.time() + self._ttl
        )

    def delete(self, key: str) -> None:
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()


# XDXR 数据缓存（除权除息）
xdxr_cache = SimpleCache(ttl_seconds=86400)

# Finance 数据缓存（股本信息）
finance_cache = SimpleCache(ttl_seconds=86400)
