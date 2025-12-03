"""
日志配置
"""

import logging
import logging.config
import os
from datetime import datetime
from pathlib import Path
from .settings import settings

# 防止重复初始化的标志
_logging_configured = False


def setup_logging():
    """设置日志配置"""
    global _logging_configured
    
    # 如果已经配置过，直接返回
    if _logging_configured:
        return logging.getLogger("app")
    
    # 创建按日期分级的日志目录
    today = datetime.now().strftime("%Y-%m-%d")
    base_log_dir = Path("logs")
    daily_log_dir = base_log_dir / today
    daily_log_dir.mkdir(parents=True, exist_ok=True)
    
    # 构建日志文件路径
    business_log_file = daily_log_dir / "app.log"  # 业务审计日志（只记录用户操作）
    error_log_file = daily_log_dir / "error.log"  # 错误日志
    debug_log_file = daily_log_dir / "debug.log"  # 调试日志（包含所有技术日志）
    
    # 日志配置字典
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%H:%M:%S",
            },
            "file_simple": {
                "format": "%(asctime)s [%(levelname)s] %(name)s\n    %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "file_detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s (%(module)s:%(funcName)s:%(lineno)d)\n    %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "error_detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s\n    Location: %(pathname)s:%(lineno)d in %(funcName)s()\n    Message: %(message)s\n    ---",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}',
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "console",
                "stream": "ext://sys.stdout",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "error_detailed",
                "filename": str(error_log_file),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 3,
                "encoding": "utf8",
            },
            "debug_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "file_detailed",
                "filename": str(debug_log_file),
                "maxBytes": 5242880,  # 5MB
                "backupCount": 2,
                "encoding": "utf8",
            },
        },
        "loggers": {
            "": {  # root logger
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "error_file"] + (["debug_file"] if settings.DEBUG else []),
                "propagate": False,
            },
            "app": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "error_file"] + (["debug_file"] if settings.DEBUG else []),
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "debug_file"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "ERROR",
                "handlers": ["console", "error_file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["debug_file"],  # 访问日志不输出到控制台
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING",  # 减少SQLAlchemy日志
                "handlers": (["debug_file"] if settings.DEBUG else []),
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": (["debug_file"] if settings.DEBUG else []),
                "propagate": False,
            },
            "redis": {
                "level": "WARNING",
                "handlers": (["debug_file"] if settings.DEBUG else []),
                "propagate": False,
            },
        },
    }
    
    # 应用日志配置
    logging.config.dictConfig(logging_config)
    
    
    # 设置第三方库日志级别
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # 标记为已配置
    _logging_configured = True
    
    return logging.getLogger("app")


def get_logger(name: str = "app") -> logging.Logger:
    """获取日志记录器"""
    return logging.getLogger(name)


def get_business_logger() -> logging.Logger:
    """获取业务审计日志记录器"""
    return logging.getLogger("app.business")


def log_user_action(logger, user: str, action: str, result: str, details: str = "", ip: str = "", extra: dict = None):
    """记录用户业务操作
    
    Args:
        logger: 日志记录器
        user: 用户名
        action: 操作类型 (登录/登出/创建用户/修改用户/删除用户等)
        result: 操作结果 (成功/失败)
        details: 操作详情
        ip: 用户IP地址
        extra: 额外的上下文信息（字典格式）
    """
    business_logger = get_business_logger()
    
    # 构建详情信息
    detail_parts = []
    if details:
        detail_parts.append(details)
    if ip:
        detail_parts.append(f"IP: {ip}")
    
    full_details = ", ".join(detail_parts) if detail_parts else "-"
    
    # 直接写入业务日志文件，不依赖过滤器
    import time
    from datetime import datetime
    from pathlib import Path
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{timestamp} | {user or '系统'} | {action} | {result} | {full_details}\n"
    
    # 获取当前日期的日志文件路径
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = Path("logs") / today / "app.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入日志文件
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_line)
    
    # 如果有 extra 信息，同时使用 logger 记录（带结构化信息）
    if extra is not None:
        logger.info(f"用户: {user}, 操作: {action}, 结果: {result}, 详情: {full_details}", extra=extra)
    else:
        # 否则只使用 business_logger 记录
        business_logger.info(f"用户: {user}, 操作: {action}, 结果: {result}, 详情: {full_details}")
    
    # 直接写入业务日志文件，不依赖过滤器
    import time
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{timestamp} | {user or '系统'} | {action} | {result} | {full_details}\n"
    
    # 获取当前日期的日志文件路径
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = Path("logs") / today / "app.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 直接写入文件
    with open(log_file, "a", encoding="utf8") as f:
        f.write(log_line)


def cleanup_old_logs(days_to_keep: int = 7):
    """清理旧的日志文件"""
    from datetime import datetime, timedelta
    
    base_log_dir = Path("logs")
    if not base_log_dir.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    for date_dir in base_log_dir.iterdir():
        if date_dir.is_dir() and len(date_dir.name) == 10:  # YYYY-MM-DD格式
            try:
                dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                if dir_date < cutoff_date:
                    import shutil
                    shutil.rmtree(date_dir)
                    print(f"已清理过期日志目录: {date_dir.name}")
            except ValueError:
                continue  # 跳过不是日期格式的目录


def get_log_stats():
    """获取日志统计信息"""
    base_log_dir = Path("logs")
    if not base_log_dir.exists():
        return {"total_dirs": 0, "total_size": 0}
    
    total_dirs = 0
    total_size = 0
    
    for date_dir in base_log_dir.iterdir():
        if date_dir.is_dir():
            total_dirs += 1
            for log_file in date_dir.glob("*.log*"):
                if log_file.is_file():
                    total_size += log_file.stat().st_size
    
    return {
        "total_dirs": total_dirs,
        "total_size_mb": round(total_size / 1024 / 1024, 2),
        "log_dirs": [d.name for d in sorted(base_log_dir.iterdir()) if d.is_dir()]
    }
