"""
统一错误码定义 - 简化版本

错误码规范:
- 1XX: 表示请求失败，请求数据有误
- 200: 表示请求成功
- 210: 登录成功，但是需要重置密码
- 301: 请求参数错误
- 4XX: 表示请求失败，用户无权限或其他
- 410: 用户登录信息过期，需要重新登录
- 411: 不合法的token
- 412: 用户加载失败
- 413: 请求token不存在
- 414: 登录失败
- 415: 密码重置失败
- 416: 密码修改失败
- 417: 免登录校验失败，访问失败
- 420: 用户访问频率过高
- 999: 表示系统异常
"""

from enum import IntEnum
from typing import Dict


class ErrorCode(IntEnum):
    """统一错误码枚举 - 简化版本"""
    
    # ============================================
    # 成功状态码
    # ============================================
    SUCCESS = 200                    # 请求成功
    LOGIN_SUCCESS_NEED_RESET = 210   # 登录成功，但需要重置密码
    
    # ============================================
    # 1XX: 请求失败，请求数据有误
    # ============================================
    REQUEST_DATA_ERROR = 100         # 请求数据有误（通用）
    
    # ============================================
    # 3XX: 请求参数错误
    # ============================================
    PARAMETER_ERROR = 301            # 请求参数错误
    
    # ============================================
    # 4XX: 认证授权错误
    # ============================================
    TOKEN_ERROR = 410                # token相关错误（过期、无效、不存在等）
    LOGIN_FAILED = 414               # 登录失败
    
    # ============================================
    # 4XX: 其他业务错误（通用）
    # ============================================
    PERMISSION_DENIED = 403          # 权限不足
    RESOURCE_NOT_FOUND = 404         # 资源不存在
    BUSINESS_ERROR = 400             # 业务逻辑错误（通用）
    
    # ============================================
    # 999: 系统异常
    # ============================================
    SYSTEM_ERROR = 999               # 系统异常


class ErrorMessage:
    """错误码对应的默认消息"""
    
    MESSAGES: Dict[int, str] = {
        # 成功状态
        ErrorCode.SUCCESS: "请求成功",
        ErrorCode.LOGIN_SUCCESS_NEED_RESET: "登录成功，但需要重置密码",
        
        # 1XX: 请求数据有误
        ErrorCode.REQUEST_DATA_ERROR: "请求数据有误",
        
        # 3XX: 请求参数错误
        ErrorCode.PARAMETER_ERROR: "请求参数错误",
        
        # 4XX: 认证授权错误
        ErrorCode.TOKEN_ERROR: "token验证失败",
        ErrorCode.LOGIN_FAILED: "登录失败",
        
        # 4XX: 业务错误
        ErrorCode.PERMISSION_DENIED: "权限不足",
        ErrorCode.RESOURCE_NOT_FOUND: "资源不存在",
        ErrorCode.BUSINESS_ERROR: "业务处理失败",
        
        # 999: 系统异常
        ErrorCode.SYSTEM_ERROR: "系统异常",
    }
    
    @classmethod
    def get_message(cls, code: int) -> str:
        """根据错误码获取默认错误信息"""
        return cls.MESSAGES.get(code, "未知错误")


def get_http_status_code(error_code: int) -> int:
    """根据业务错误码获取对应的HTTP状态码"""
    if error_code == ErrorCode.SUCCESS:
        return 200
    elif error_code == ErrorCode.LOGIN_SUCCESS_NEED_RESET:
        return 200
    elif error_code == ErrorCode.REQUEST_DATA_ERROR:
        return 400
    elif error_code == ErrorCode.PARAMETER_ERROR:
        return 400
    elif error_code in [ErrorCode.TOKEN_ERROR, ErrorCode.LOGIN_FAILED]:
        return 401
    elif error_code == ErrorCode.PERMISSION_DENIED:
        return 403
    elif error_code == ErrorCode.RESOURCE_NOT_FOUND:
        return 404
    elif error_code == ErrorCode.BUSINESS_ERROR:
        return 400
    elif error_code == ErrorCode.SYSTEM_ERROR:
        return 500
    else:
        return 500