"""
数据库配置（支持 MySQL 和 PostgreSQL 自动切换）
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from typing import AsyncGenerator, Literal
from urllib.parse import urlparse
from .settings import settings
from .logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """数据库基础类"""
    pass


def get_database_type() -> Literal["mysql", "postgresql", "unknown"]:
    """
    根据 DATABASE_URL 自动识别数据库类型
    
    Returns:
        Literal["mysql", "postgresql", "unknown"]: 数据库类型
    """
    db_url = settings.DATABASE_URL.lower()
    if "mysql" in db_url or "aiomysql" in db_url or "pymysql" in db_url:
        return "mysql"
    elif "postgresql" in db_url or "postgres" in db_url or "asyncpg" in db_url:
        return "postgresql"
    else:
        return "unknown"


def get_database_name_from_url() -> str:
    """
    从 DATABASE_URL 中提取数据库名称
    
    Returns:
        str: 数据库名称
    """
    try:
        # 解析 URL，格式：mysql+aiomysql://user:pass@host:port/dbname
        # 或：postgresql+asyncpg://user:pass@host:port/dbname
        parsed = urlparse(settings.DATABASE_URL.replace("+", "://", 1))
        # 移除路径开头的 /
        db_name = parsed.path.lstrip("/")
        return db_name
    except Exception as e:
        logger.warning(f"无法从 DATABASE_URL 提取数据库名称: {e}")
        return "boshirobot"


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


def get_database_type_info() -> dict:
    """
    获取数据库类型信息（用于日志和调试）
    
    Returns:
        dict: 包含数据库类型和名称的字典
    """
    db_type = get_database_type()
    db_name = get_database_name_from_url()
    return {
        "type": db_type,
        "name": db_name,
        "url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "***"
    }


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
    """
    初始化数据库（自动适配 MySQL 和 PostgreSQL）
    
    根据 DATABASE_URL 自动识别数据库类型并执行相应的初始化逻辑：
    - MySQL: 尝试创建数据库（如果不存在），然后创建表结构
    - PostgreSQL: 直接创建表结构（连接时已指定数据库）
    
    注意：
    - 对于 MySQL，如果数据库不存在，需要先手动创建数据库
    - 或者确保 DATABASE_URL 中的数据库已存在
    - 表结构会根据 SQLAlchemy 模型自动创建
    """
    db_type = get_database_type()
    db_info = get_database_type_info()
    
    logger.info(f"检测到数据库类型: {db_type}, 数据库名称: {db_info['name']}")
    
    if db_type == "mysql":
        # MySQL 初始化逻辑
        # 注意：CREATE DATABASE 不能在事务中执行，且需要连接到 MySQL 服务器（不指定数据库）
        # 这里我们假设数据库已经存在，或者通过外部脚本创建
        # 如果数据库不存在，连接会失败，这是预期的行为
        
        # 尝试创建表结构
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("MySQL 表结构初始化完成")
        except Exception as e:
            error_msg = str(e).lower()
            if "unknown database" in error_msg or "doesn't exist" in error_msg:
                logger.error(
                    f"MySQL 数据库 '{db_info['name']}' 不存在。"
                    f"请先手动创建数据库：CREATE DATABASE `{db_info['name']}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                )
            else:
                logger.error(f"MySQL 表结构初始化失败: {e}")
            raise
    
    elif db_type == "postgresql":
        # PostgreSQL 初始化逻辑
        # PostgreSQL 连接时已经指定了数据库，直接创建表即可
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("PostgreSQL 表结构初始化完成")
        except Exception as e:
            error_msg = str(e).lower()
            if "database" in error_msg and "does not exist" in error_msg:
                logger.error(
                    f"PostgreSQL 数据库 '{db_info['name']}' 不存在。"
                    f"请先手动创建数据库：CREATE DATABASE {db_info['name']};"
                )
            else:
                logger.error(f"PostgreSQL 表结构初始化失败: {e}")
            raise
    
    else:
        # 未知数据库类型，尝试通用初始化
        logger.warning(f"未知数据库类型: {db_type}，尝试通用初始化")
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("表结构初始化完成（通用模式）")
        except Exception as e:
            logger.error(f"表结构初始化失败: {e}")
            raise


async def close_database():
    """关闭数据库连接"""
    await engine.dispose()
