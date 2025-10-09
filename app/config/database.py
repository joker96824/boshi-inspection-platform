"""
数据库配置
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from typing import AsyncGenerator
from .settings import settings


class Base(DeclarativeBase):
    """数据库基础类"""
    pass


# 创建异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
    future=True,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_database_url() -> str:
    """获取数据库连接URL"""
    return settings.DATABASE_URL


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database():
    """初始化数据库"""
    async with engine.begin() as conn:
        # 对于MySQL，需要先创建数据库（如果不存在）
        try:
            await conn.execute(text("CREATE DATABASE IF NOT EXISTS boshirobot"))
            await conn.execute(text("USE boshirobot"))
        except Exception as e:
            logger.warning(f"数据库创建警告: {e}")
        
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)


async def close_database():
    """关闭数据库连接"""
    await engine.dispose()
