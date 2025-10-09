"""
依赖注入
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.database import get_async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async for session in get_async_session():
        try:
            yield session
        finally:
            await session.close()
