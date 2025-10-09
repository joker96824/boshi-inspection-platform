"""
自定义异常类 - 简化版本
"""

from typing import Any, Dict, Optional
from .error_codes import ErrorCode, ErrorMessage, get_http_status_code


class CustomException(Exception):
    """自定义异常基类"""
    
    def __init__(
        self,
        code: int,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message or ErrorMessage.get_message(code)
        self.details = details or {}
        self.status_code = get_http_status_code(code)
        super().__init__(self.message)


# ============================================
# 主要异常类型 - 简化版本
# ============================================

class ValidationError(CustomException):
    """数据验证异常 - 使用通用的请求数据错误码"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(ErrorCode.REQUEST_DATA_ERROR, message, details)


class ParameterError(CustomException):
    """请求参数错误异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(ErrorCode.PARAMETER_ERROR, message, details)


class BusinessError(CustomException):
    """业务逻辑异常 - 通用业务错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(ErrorCode.BUSINESS_ERROR, message, details)


class TokenError(CustomException):
    """token相关错误（过期、无效、不存在等）"""
    
    def __init__(self, message: Optional[str] = None):
        super().__init__(ErrorCode.TOKEN_ERROR, message)


class LoginFailedError(CustomException):
    """登录失败异常"""
    
    def __init__(self, message: Optional[str] = None):
        super().__init__(ErrorCode.LOGIN_FAILED, message)


class PermissionDeniedError(CustomException):
    """权限不足异常"""
    
    def __init__(self, message: Optional[str] = None):
        super().__init__(ErrorCode.PERMISSION_DENIED, message)


class ResourceNotFoundError(CustomException):
    """资源不存在异常"""
    
    def __init__(self, message: str):
        super().__init__(ErrorCode.RESOURCE_NOT_FOUND, message)


class SystemError(CustomException):
    """系统异常"""
    
    def __init__(self, message: Optional[str] = None):
        super().__init__(ErrorCode.SYSTEM_ERROR, message)


# ============================================
# 便捷异常函数 - 使用通用错误码但提供具体消息
# ============================================

def UserNotFoundError(user_identifier: str):
    """用户不存在 - 使用资源不存在错误码"""
    return ResourceNotFoundError(f"用户 '{user_identifier}' 不存在")


def UsernameExistsError(username: str):
    """用户名已存在 - 使用业务错误码"""
    return BusinessError(f"用户名 '{username}' 已存在")


def EmailExistsError(email: str):
    """邮箱已存在 - 使用业务错误码"""
    return BusinessError(f"邮箱 '{email}' 已存在")


def MobileExistsError(mobile: str):
    """手机号已存在 - 使用业务错误码"""
    return BusinessError(f"手机号 '{mobile}' 已存在")


def OldPasswordError(message: str = "旧密码错误"):
    """旧密码错误 - 使用数据验证错误码"""
    return ValidationError(message)


def PasswordChangeFailedError(message: str = "密码修改失败"):
    """密码修改失败 - 使用数据验证错误码"""
    return ValidationError(message)


def PasswordResetFailedError(message: str = "密码重置失败"):
    """密码重置失败 - 使用数据验证错误码"""
    return ValidationError(message)


def CannotDeleteSelfError(message: str = "不能删除自己的账户"):
    """不能删除自己 - 使用业务错误码"""
    return BusinessError(message)


# Token相关的便捷函数
def TokenExpiredError(message: str = "用户登录信息过期，需要重新登录"):
    """Token过期 - 使用token错误码"""
    return TokenError(message)


def InvalidTokenError(message: str = "不合法的token"):
    """Token无效 - 使用token错误码"""
    return TokenError(message)


def TokenNotExistsError(message: str = "请求token不存在"):
    """Token不存在 - 使用token错误码"""
    return TokenError(message)


def ROS2Error(message: str):
    """ROS2异常 - 使用系统异常码"""
    return SystemError(f"ROS2异常: {message}")


def DatabaseError(message: str):
    """数据库异常 - 使用系统异常码"""
    return SystemError(f"数据库异常: {message}")


def RedisError(message: str):
    """Redis异常 - 使用系统异常码"""
    return SystemError(f"Redis异常: {message}")


def WebSocketError(message: str):
    """WebSocket异常 - 使用系统异常码"""
    return SystemError(f"WebSocket异常: {message}")


# ============================================
# 向后兼容的别名
# ============================================

AuthenticationError = LoginFailedError
AuthorizationError = PermissionDeniedError
BusinessLogicError = BusinessError