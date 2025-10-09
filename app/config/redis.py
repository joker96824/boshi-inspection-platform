"""
Redis配置
"""

import redis.asyncio as redis
from typing import Optional
from .settings import settings


def get_redis_url() -> str:
    """获取Redis连接URL"""
    return settings.REDIS_URL


def get_redis_client() -> redis.Redis:
    """获取Redis客户端"""
    return redis.from_url(
        settings.REDIS_URL,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
    )


async def get_redis_connection() -> redis.Redis:
    """获取Redis连接"""
    client = get_redis_client()
    try:
        yield client
    finally:
        await client.close()
