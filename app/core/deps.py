"""
依赖注入
"""

from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.database import get_async_session
from ..core.exceptions import ValidationError


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async for session in get_async_session():
        try:
            yield session
        finally:
            await session.close()


def validate_pagination_params(page: Optional[int], size: Optional[int]) -> None:
    """
    验证分页参数：page和size必须同时提供或同时不提供
    
    Args:
        page: 页码
        size: 每页数量
    
    Raises:
        ValidationError: 如果page和size不同时提供或同时不提供
    """
    if (page is None) != (size is None):
        raise ValidationError("page和size必须同时提供或同时不提供")
