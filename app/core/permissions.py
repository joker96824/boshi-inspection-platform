"""
权限管理系统
"""

from enum import Enum
from typing import Dict, List, Optional
from fastapi import Depends
from ..core.auth import get_current_user
from ..core.exceptions import PermissionDeniedError


class UserRole(str, Enum):
    """用户角色枚举"""
    SUPER_ADMIN = "super_admin"    # 超级管理员
    ADMIN = "admin"                # 管理员
    OPERATOR = "operator"          # 操作员
    VIEWER = "viewer"              # 观察员
    USER = "user"                  # 普通用户


# 角色层级（数字越小权限越高）
ROLE_HIERARCHY: Dict[UserRole, int] = {
    UserRole.SUPER_ADMIN: 1,
    UserRole.ADMIN: 2,
    UserRole.OPERATOR: 3,
    UserRole.VIEWER: 4,
    UserRole.USER: 5,
}

# 简化权限管理：基于角色层级，不需要复杂的权限映射


def get_role_level(role: str) -> int:
    """获取角色层级"""
    try:
        user_role = UserRole(role)
        return ROLE_HIERARCHY[user_role]
    except (ValueError, KeyError):
        return 999  # 未知角色，最低权限


def can_manage_role(manager_role: str, target_role: str) -> bool:
    """检查是否可以管理目标角色"""
    manager_level = get_role_level(manager_role)
    target_level = get_role_level(target_role)
    
    # 只能管理级别低于自己的角色
    return manager_level < target_level


# 简化权限管理：只使用角色层级，不使用复杂的权限系统


def require_role_level(min_role: UserRole):
    """角色级别验证装饰器"""
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_level = get_role_level(current_user["role"])
        required_level = ROLE_HIERARCHY[min_role]
        
        if user_level > required_level:
            raise PermissionDeniedError("权限不足，无法访问此功能")
        return current_user
    
    return role_checker


def require_higher_role_than(target_role: str):
    """要求比目标角色更高的权限"""
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if not can_manage_role(current_user["role"], target_role):
            raise PermissionDeniedError("权限不足，无法执行此操作")
        return current_user
    
    return role_checker


# 常用权限验证器
require_super_admin = require_role_level(UserRole.SUPER_ADMIN)
require_admin = require_role_level(UserRole.ADMIN)
require_operator = require_role_level(UserRole.OPERATOR)
require_viewer = require_role_level(UserRole.USER)  # 所有用户都可以查看

# 增删改权限：只有 super_admin、admin、operator 可以
require_write_permission = require_role_level(UserRole.OPERATOR)

# 查询权限：所有用户都可以
require_read_permission = require_role_level(UserRole.USER)
