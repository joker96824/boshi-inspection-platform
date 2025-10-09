"""
核心功能模块
"""

from .auth import create_access_token, verify_token, get_current_user
from .permissions import (
    require_admin, require_super_admin, require_operator, require_viewer,
    require_role_level, can_manage_role, UserRole
)
from .security import verify_password, get_password_hash
from .error_codes import ErrorCode, ErrorMessage, get_http_status_code
from .exceptions import (
    # 核心异常类
    CustomException,
    ValidationError,
    ParameterError,
    BusinessError,
    TokenError,
    LoginFailedError,
    PermissionDeniedError,
    ResourceNotFoundError,
    SystemError,
    
    # 便捷异常函数
    UserNotFoundError,
    UsernameExistsError,
    EmailExistsError,
    MobileExistsError,
    OldPasswordError,
    PasswordChangeFailedError,
    PasswordResetFailedError,
    CannotDeleteSelfError,
    TokenExpiredError,
    InvalidTokenError,
    TokenNotExistsError,
    ROS2Error,
    DatabaseError,
    RedisError,
    WebSocketError,
    
    # 向后兼容
    AuthenticationError,
    AuthorizationError,
    BusinessLogicError,
)
from .middleware import (
    LoggingMiddleware,
    RateLimitMiddleware,
)
from .deps import get_db
from .app_factory import create_app, setup_lifespan_events

__all__ = [
    # 认证相关
    "create_access_token",
    "verify_token",
    "get_current_user",
    "verify_password",
    "get_password_hash",
    
    # 错误码和异常
    "ErrorCode",
    "ErrorMessage", 
    "get_http_status_code",
    "CustomException",
    "ValidationError",
    "ParameterError",
    "RequiredFieldMissingError",
    "DuplicateDataError",
    "TokenExpiredError",
    "InvalidTokenError",
    "TokenNotExistsError",
    "LoginFailedError",
    "PermissionDeniedError",
    "AccessFrequencyTooHighError",
    "UserNotFoundError",
    "UserLoadFailedError",
    "UsernameExistsError",
    "EmailExistsError",
    "MobileExistsError",
    "OldPasswordError",
    "PasswordChangeFailedError",
    "CannotDeleteSelfError",
    "ResourceNotFoundError",
    "SystemError",
    "DatabaseError",
    "RedisError",
    "ROS2Error",
    "WebSocketError",
    "BusinessLogicError",
    "AuthenticationError",
    "AuthorizationError",
    
    # 中间件
    "LoggingMiddleware",
    "RateLimitMiddleware",
    
    # 依赖注入
    "get_db",
    
    # 权限管理
    "require_admin",
    "require_super_admin",
    "require_operator",
    "require_viewer",
    "require_role_level",
    "can_manage_role",
    "UserRole",
    
    # 应用工厂
    "create_app",
    "setup_lifespan_events",
]
