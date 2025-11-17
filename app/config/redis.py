"""
Redis配置（可选，连接失败不影响应用启动）
"""

import redis.asyncio as redis
from typing import Optional, AsyncGenerator
from .settings import settings
from .logging import get_logger

logger = get_logger(__name__)

# 全局 Redis 客户端实例（延迟初始化）
_redis_client: Optional[redis.Redis] = None
_redis_available: bool = False


def is_redis_enabled() -> bool:
    """检查Redis是否启用"""
    return settings.REDIS_ENABLED


def get_redis_url() -> str:
    """获取Redis连接URL"""
    return settings.REDIS_URL


def _create_redis_client() -> Optional[redis.Redis]:
    """创建Redis客户端（内部函数，带容错处理）"""
    if not settings.REDIS_ENABLED:
        return None
    
    try:
        client = redis.from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        return client
    except Exception as e:
        logger.warning(f"Redis客户端创建失败: {e}，应用将继续运行（Redis功能不可用）")
        return None


async def _check_redis_connection(client: redis.Redis) -> bool:
    """检查Redis连接是否可用"""
    try:
        await client.ping()
        return True
    except Exception as e:
        logger.warning(f"Redis连接检查失败: {e}")
        return False


def get_redis_client() -> Optional[redis.Redis]:
    """
    获取Redis客户端
    
    Returns:
        Optional[redis.Redis]: Redis客户端实例，如果Redis未启用或连接失败则返回None
    """
    global _redis_client, _redis_available
    
    if not settings.REDIS_ENABLED:
        return None
    
    # 如果已有客户端且可用，直接返回
    if _redis_client is not None and _redis_available:
        return _redis_client
    
    # 创建新客户端
    _redis_client = _create_redis_client()
    if _redis_client is None:
        _redis_available = False
        return None
    
    # 检查连接（异步检查，这里只创建客户端，不阻塞）
    # 实际使用时会在第一次操作时检查
    _redis_available = True
    return _redis_client


async def get_redis_connection() -> AsyncGenerator[Optional[redis.Redis], None]:
    """
    获取Redis连接（异步上下文管理器）
    
    Yields:
        Optional[redis.Redis]: Redis客户端实例，如果Redis未启用或连接失败则返回None
    """
    if not settings.REDIS_ENABLED:
        logger.debug("Redis未启用，跳过连接")
        yield None
        return
    
    client = get_redis_client()
    if client is None:
        logger.debug("Redis客户端不可用，跳过连接")
        yield None
        return
    
    # 检查连接是否可用
    try:
        is_available = await _check_redis_connection(client)
        if not is_available:
            logger.warning("Redis连接不可用，但应用将继续运行")
            yield None
            return
    except Exception as e:
        logger.warning(f"Redis连接检查异常: {e}，但应用将继续运行")
        yield None
        return
    
    try:
        yield client
    except Exception as e:
        logger.warning(f"Redis操作异常: {e}，但应用将继续运行")
        yield None
    finally:
        # 注意：不要在这里关闭客户端，因为可能是全局共享的
        # 只在应用关闭时统一关闭
        pass


async def close_redis_connection():
    """关闭Redis连接（应用关闭时调用）"""
    global _redis_client, _redis_available
    
    if _redis_client is not None:
        try:
            await _redis_client.close()
            logger.info("Redis连接已关闭")
        except Exception as e:
            logger.warning(f"关闭Redis连接时出错: {e}")
        finally:
            _redis_client = None
            _redis_available = False
