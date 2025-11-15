"""
用户管理API接口
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ...core.deps import get_db, validate_pagination_params
from ...core.permissions import require_admin, get_current_user, require_no_auth
from ...services.user_service import UserService
from ...schemas.user import UserCreate, UserUpdate, UserPasswordUpdate
from ...core.exceptions import ParameterError

router = APIRouter()


@router.post("/", response_model=dict)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """创建用户
    
    Args:
        user_data: 用户创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建结果
    
    Raises:
        400: 用户名或手机号已存在
        401: 用户未认证
        403: 权限不足
    
    权限规则：
    - 只有admin和super_admin可以创建用户
    """
    user_service = UserService(db)
    return await user_service.create_user(user_data, current_user)


@router.get("/", response_model=dict)
async def get_users(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取用户列表
    
    返回按角色权限排序的用户列表：
    1. 首先按角色权限排序（super_admin > admin > operator > viewer > user）
    2. 同权限内按创建时间倒序排序（新用户在前）
    3. 然后进行分页处理
    """
    user_service = UserService(db)
    return await user_service.get_user_list(page, size)


@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取指定用户信息"""
    user_service = UserService(db)
    return await user_service.get_user_by_id(user_id)


@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """更新用户信息
    
    Args:
        user_id: 要更新的用户ID
        user_data: 更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新结果
    
    Raises:
        404: 用户不存在或无权限访问
        401: 用户未认证
        403: 权限不足
    
    权限规则：
    - 只有admin和super_admin可以调用
    - 可以强制修改用户名、手机、邮箱、角色、密码
    - 修改密码时无需提供旧密码
    - 只能修改比自己级别低的用户
    """
    user_service = UserService(db)
    return await user_service.force_update_user(user_id, user_data, current_user)


@router.put("/updatepassword", response_model=dict)
async def update_password(
    password_data: UserPasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """用户自己修改密码
    
    - 任何登录用户都可以调用
    - 必须提供正确的旧密码
    - 密码修改后所有会话失效，需要重新登录
    """
    user_service = UserService(db)
    return await user_service.update_password(password_data, current_user)


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除用户（软删除）
    
    Args:
        user_id: 要删除的用户ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    
    Raises:
        404: 用户不存在或无权限访问
        401: 用户未认证
        403: 权限不足
    
    权限规则：
    - 只有admin和super_admin可以删除用户
    - 只能删除权限级别低于自己的用户
    - 不能删除自己的账户
    - super_admin > admin > operator > viewer > user
    """
    user_service = UserService(db)
    return await user_service.delete_user(user_id, current_user)