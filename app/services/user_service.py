"""
用户业务逻辑层
"""

from typing import Dict, List, Optional
from ..core.exceptions import (
    UsernameExistsError, EmailExistsError, MobileExistsError, UserNotFoundError,
    PermissionDeniedError, OldPasswordError, CannotDeleteSelfError
)
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from ..repositories.user_repository import UserRepository
from ..core.security import get_password_hash, verify_password
from ..core.permissions import can_manage_role
from ..schemas.user import UserCreate, UserUpdate, UserPasswordUpdate
from ..utils.response import ApiResponse
from ..config.logging import log_user_action


class UserService:
    """用户业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def create_user(self, user_data: UserCreate, creator: dict) -> dict:
        """创建用户"""
        # 检查用户名是否已存在
        if await self.user_repo.username_exists(user_data.username):
            raise UsernameExistsError(user_data.username)
        
        # 检查手机号是否已存在
        if await self.user_repo.mobile_exists(user_data.mobile):
            raise MobileExistsError(user_data.mobile)
        
        # 检查邮箱是否已存在（如果提供了邮箱）
        if user_data.email and await self.user_repo.email_exists(user_data.email):
            raise EmailExistsError(user_data.email)
        
        # 准备用户数据 - 自动设置默认值
        create_data = {
            "username": user_data.username,
            "password_hash": get_password_hash(user_data.password),
            "mobile": user_data.mobile,
            "email": user_data.email,  # 使用用户提供的邮箱（可能为空）
            "role": "user",  # 角色自动设置为最低级
            "created_by": creator["username"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        # 创建用户
        user = await self.user_repo.create(create_data)
        
        # 记录用户创建业务日志
        log_user_action(
            user=creator["username"],
            action="创建用户",
            result="成功",
            details=f"新用户: {user.username}, 角色: {user.role}, 手机: {user.mobile}"
        )
        
        return ApiResponse.success(
            data={"user": self._format_user_response(user)},
            message="用户创建成功"
        )
    
    async def get_user_list(self, page: int = 1, size: int = 20) -> dict:
        """获取用户列表"""
        # 计算 skip 和 limit
        skip = (page - 1) * size
        limit = size
        
        users = await self.user_repo.get_all(skip, limit)
        total = await self.user_repo.get_total_count()
        
        return ApiResponse.paginated(
            items=[self._format_user_response(user) for user in users],
            total=total,
            page=page,
            size=size
        )
    
    async def get_user_by_id(self, user_id: str) -> dict:
        """根据ID获取用户"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        
        return ApiResponse.success(
            data={"user": self._format_user_response(user)},
            message="获取用户信息成功"
        )
    
    async def force_update_user(self, target_user_id: str, user_data, operator: dict) -> dict:
        """管理员强制更新用户信息"""
        
        # 获取目标用户
        user = await self.user_repo.get_by_id(target_user_id)
        if not user:
            raise UserNotFoundError(target_user_id)
        
        # 准备更新数据
        update_data = {}
        updated_fields = []
        
        # 处理用户名更新
        if user_data.username and user_data.username != user.username:
            if await self.user_repo.username_exists(user_data.username, target_user_id):
                raise UsernameExistsError(user_data.username)
            update_data["username"] = user_data.username
            updated_fields.append("username")
        
        # 处理邮箱更新
        if user_data.email is not None and user_data.email != user.email:
            if user_data.email and await self.user_repo.email_exists(user_data.email, target_user_id):
                raise EmailExistsError(user_data.email)
            update_data["email"] = user_data.email
            updated_fields.append("email")
        
        # 处理手机号更新
        if user_data.mobile is not None and user_data.mobile != user.mobile:
            # 检查手机号是否已被其他用户使用
            if await self.user_repo.mobile_exists(user_data.mobile, target_user_id):
                raise MobileExistsError(user_data.mobile)
            update_data["mobile"] = user_data.mobile
            updated_fields.append("mobile")
        
        # 处理角色更新
        if user_data.role and user_data.role != user.role:
            # 检查是否有权限管理目标用户的当前角色
            if not can_manage_role(operator["role"], user.role):
                raise PermissionDeniedError("权限不足，无法修改该用户的角色")
            
            # 检查是否有权限设置新角色
            if not can_manage_role(operator["role"], user_data.role):
                raise PermissionDeniedError("权限不足，无法设置该角色")
            
            update_data["role"] = user_data.role
            updated_fields.append("role")
        
        # 处理密码更新（强制更新，无需旧密码）
        password_updated = False
        if user_data.new_password:
            update_data["password_hash"] = get_password_hash(user_data.new_password)
            updated_fields.append("password")
            password_updated = True
        
        # 执行更新
        if update_data:
            update_data["updated_by"] = operator["username"]
            user = await self.user_repo.update(user, update_data)
            
            # 如果密码被更新，使所有该用户的会话失效
            if password_updated:
                await self.user_repo.invalidate_user_sessions(target_user_id)
                
                return ApiResponse.success(
                    data={
                        "updated_fields": updated_fields,
                        "user": self._format_user_response(user)
                    },
                    message="用户信息和密码更新成功，所有会话已失效"
                )
            else:
                return ApiResponse.success(
                    data={
                        "updated_fields": updated_fields,
                        "user": self._format_user_response(user)
                    },
                    message="用户信息更新成功"
                )
        else:
            return ApiResponse.success(
                data={"user": self._format_user_response(user)},
                message="没有需要更新的字段"
            )
    
    async def update_password(self, password_data: UserPasswordUpdate, user: dict) -> dict:
        """用户自己修改密码"""
        user_id = user["id"]
        
        # 获取用户信息
        user_obj = await self.user_repo.get_by_id(user_id)
        if not user_obj:
            raise UserNotFoundError(user_id)
        
        # 验证旧密码
        if not verify_password(password_data.old_password, user_obj.password_hash):
            raise OldPasswordError("旧密码错误")
        
        # 更新密码
        update_data = {
            "password_hash": get_password_hash(password_data.new_password),
            "updated_by": user["username"]
        }
        
        await self.user_repo.update(user_obj, update_data)
        
        # 密码更新后，使所有该用户的会话失效
        await self.user_repo.invalidate_user_sessions(user_id)
        
        return ApiResponse.success(
            message="密码修改成功，所有会话已失效，请重新登录"
        )
    
    async def delete_user(self, user_id: str, operator: dict) -> dict:
        """删除用户
        
        权限规则：
        - 只有admin和super_admin可以删除用户
        - 只能删除权限级别低于自己的用户
        - 不能删除自己的账户
        """
        # 权限检查：只有admin和super_admin可以删除用户
        if operator["role"] not in ["admin", "super_admin"]:
            raise PermissionDeniedError("权限不足，只有管理员可以删除用户")
        
        # 不能删除自己
        if user_id == operator["id"]:
            raise CannotDeleteSelfError("不能删除自己的账户")
        
        # 获取要删除的用户
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        
        # 检查权限：只能删除比自己级别低的用户
        if not can_manage_role(operator["role"], user.role):
            raise PermissionDeniedError("权限不足，无法删除该用户")
        
        # 软删除用户
        await self.user_repo.soft_delete(user, operator["username"])
        
        # 使该用户的所有会话失效
        await self.user_repo.invalidate_user_sessions(user_id)
        
        # 记录用户删除业务日志
        log_user_action(
            user=operator["username"],
            action="删除用户",
            result="成功",
            details=f"目标用户: {user.username}, 角色: {user.role}"
        )
        
        return ApiResponse.success(
            data={
                "deleted_user": {
                    "id": str(user.id),
                    "username": user.username,
                    "role": user.role
                },
                "operator": {
                    "username": operator["username"],
                    "role": operator["role"]
                }
            },
            message=f"用户 '{user.username}' (角色: {user.role}) 删除成功，所有会话已失效"
        )
    
    def _format_user_response(self, user) -> dict:
        """格式化用户响应数据"""
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "mobile": user.mobile,
            "role": user.role,
            "last_login_at": user.last_login_at,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "is_deleted": user.is_deleted
        }