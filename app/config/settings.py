"""
应用配置设置
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类"""
    
    # 优先使用环境变量，不读取.env文件（Docker环境中通过environment传递配置）
    model_config = SettingsConfigDict(extra="ignore")

    # 应用基础配置
    APP_NAME: str = Field("博实智能巡检平台", description="应用名称")
    APP_VERSION: str = Field("1.0.0", description="应用版本")
    DEBUG: bool = Field(True, description="调试模式")
    ENVIRONMENT: str = Field("development", description="环境: development/production")
    
    # 服务器配置
    HOST: str = Field("0.0.0.0", description="服务器主机")
    PORT: int = Field(8000, description="服务器端口")
    WORKERS: int = Field(1, description="工作进程数")
    LOG_LEVEL: str = Field("INFO", description="日志级别")
    
    # 数据库配置
    DATABASE_URL: str = Field(
        "mysql+aiomysql://root:root@localhost:3306/boshirobot",
        description="数据库连接URL"
    )
    DATABASE_POOL_SIZE: int = Field(10, description="数据库连接池大小")
    DATABASE_MAX_OVERFLOW: int = Field(20, description="数据库最大溢出连接数")
    
    # Redis配置
    REDIS_URL: str = Field("redis://localhost:6379/0", description="Redis连接URL")
    REDIS_DB: int = Field(0, description="Redis数据库编号")
    
    # JWT配置
    SECRET_KEY: str = Field("your-secret-key-change-in-production", description="JWT密钥")
    ALGORITHM: str = Field("HS256", description="JWT算法")
    ACCESS_TOKEN_EXPIRE_DAYS: int = Field(30, description="访问令牌过期时间(天)")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(90, description="刷新令牌过期时间(天)")
    
    # CORS配置
    CORS_ORIGINS: List[str] = Field(["http://localhost:3000", "http://localhost:8080"], description="CORS允许的源")
    CORS_METHODS: List[str] = Field(["GET", "POST", "PUT", "DELETE", "OPTIONS"], description="CORS允许的方法")
    CORS_HEADERS: List[str] = Field(["*"], description="CORS允许的头部")
    
    # ROS2配置
    ROS_DOMAIN_ID: int = Field(0, description="ROS2域ID")
    ROS_BRIDGE_PORT: int = Field(9090, description="ROS Bridge端口")
    ROS_BRIDGE_HOST: str = Field("localhost", description="ROS Bridge主机")
    
    
    # 日志配置
    LOG_FORMAT: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    LOG_FILE: str = Field("logs/app.log", description="日志文件路径")


# 创建全局配置实例
settings = Settings()