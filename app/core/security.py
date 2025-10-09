"""
安全相关功能
"""

import hashlib
import secrets
from typing import Optional
from passlib.context import CryptContext
from passlib.hash import bcrypt

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def generate_salt() -> str:
    """生成盐值"""
    return secrets.token_hex(32)


def hash_password_with_salt(password: str, salt: str) -> str:
    """使用盐值哈希密码"""
    return hashlib.sha256((password + salt).encode()).hexdigest()


def generate_random_string(length: int = 32) -> str:
    """生成随机字符串"""
    return secrets.token_urlsafe(length)


def generate_session_token() -> str:
    """生成会话令牌"""
    return secrets.token_urlsafe(64)


def generate_refresh_token() -> str:
    """生成刷新令牌"""
    return secrets.token_urlsafe(64)


def generate_api_key() -> str:
    """生成API密钥"""
    return secrets.token_urlsafe(32)


def verify_api_key(api_key: str, stored_hash: str) -> bool:
    """验证API密钥"""
    return secrets.compare_digest(api_key, stored_hash)


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """掩码敏感数据"""
    if len(data) <= visible_chars:
        return "*" * len(data)
    
    visible = data[:visible_chars]
    masked = "*" * (len(data) - visible_chars)
    return visible + masked


def is_strong_password(password: str) -> bool:
    """检查密码强度"""
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return has_upper and has_lower and has_digit and has_special


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """验证密码强度并返回错误信息"""
    errors = []
    
    if len(password) < 8:
        errors.append("密码长度至少8位")
    
    if not any(c.isupper() for c in password):
        errors.append("密码必须包含大写字母")
    
    if not any(c.islower() for c in password):
        errors.append("密码必须包含小写字母")
    
    if not any(c.isdigit() for c in password):
        errors.append("密码必须包含数字")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("密码必须包含特殊字符")
    
    return len(errors) == 0, errors
