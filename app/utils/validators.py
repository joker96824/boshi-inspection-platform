"""
数据验证工具
"""

import re
from typing import Optional


def validate_username(username: str) -> bool:
    """验证用户名格式"""
    if not username:
        return False
    
    # 用户名规则：3-50字符，支持字母、数字、下划线、中文
    pattern = r'^[a-zA-Z0-9_\u4e00-\u9fa5]{3,50}$'
    return bool(re.match(pattern, username))


def validate_mobile(mobile: str) -> bool:
    """验证手机号格式"""
    if not mobile or mobile == '':
        return False  # 手机号为空时返回False，让调用方决定是否允许空值
    
    # 11位数字格式
    pattern = r'^\d{11}$'
    return bool(re.match(pattern, mobile))


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    if not email or email == '':
        return True  # 邮箱是可选的
    
    # 邮箱格式为 *@*.com
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.com$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple[bool, str]:
    """验证密码强度"""
    if len(password) < 6:
        return False, "密码长度至少6位"
    
    if len(password) > 50:
        return False, "密码长度不能超过50位"
    
    # 可以添加更多密码强度规则
    # has_upper = any(c.isupper() for c in password)
    # has_lower = any(c.islower() for c in password)
    # has_digit = any(c.isdigit() for c in password)
    # has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
    
    return True, "密码格式正确"


def sanitize_string(text: Optional[str]) -> Optional[str]:
    """清理字符串"""
    if not text:
        return None
    
    # 去除首尾空格
    text = text.strip()
    
    # 如果为空字符串，返回 None
    if not text:
        return None
    
    return text


def validate_role(role: str) -> bool:
    """验证角色是否有效"""
    valid_roles = ["super_admin", "admin", "operator", "viewer", "user"]
    return role in valid_roles
