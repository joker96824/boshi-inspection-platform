"""
时间处理工具
"""

from datetime import datetime, timedelta
from typing import Optional
import pytz


def get_current_time() -> datetime:
    """获取当前时间"""
    return datetime.utcnow()


def format_datetime(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[str]:
    """格式化时间"""
    if dt is None:
        return None
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """解析时间字符串"""
    return datetime.strptime(date_str, format_str)


def add_days(dt: datetime, days: int) -> datetime:
    """添加天数"""
    return dt + timedelta(days=days)


def add_hours(dt: datetime, hours: int) -> datetime:
    """添加小时"""
    return dt + timedelta(hours=hours)


def add_minutes(dt: datetime, minutes: int) -> datetime:
    """添加分钟"""
    return dt + timedelta(minutes=minutes)


def is_expired(expires_at: datetime) -> bool:
    """检查是否过期"""
    return expires_at < datetime.utcnow()


def get_expiry_seconds(expires_at: datetime) -> int:
    """获取距离过期的秒数"""
    delta = expires_at - datetime.utcnow()
    return max(0, int(delta.total_seconds()))


def get_beijing_time() -> datetime:
    """获取北京时间"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(beijing_tz)


def utc_to_beijing(utc_dt: datetime) -> datetime:
    """UTC时间转北京时间"""
    utc_tz = pytz.UTC
    beijing_tz = pytz.timezone('Asia/Shanghai')
    
    if utc_dt.tzinfo is None:
        utc_dt = utc_tz.localize(utc_dt)
    
    return utc_dt.astimezone(beijing_tz)
