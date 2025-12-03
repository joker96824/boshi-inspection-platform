"""
分组API路由
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_read_permission
from ...services.group_service import GroupService
from ...schemas.group import (
    GroupCreate,
    GroupUpdate,
)

router = APIRouter()


@router.post("/", response_model=dict)
async def create_group(
    group_data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建分组
    
    Args:
        group_data: 分组创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的分组对象
    """
    service = GroupService(db)
    return await service.create_group(group_data, current_user)


@router.get("/", response_model=dict)
async def get_groups(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    group_name: Optional[str] = Query(None, description="分组名称（模糊查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """获取分组列表
    
    Args:
        page: 页码
        size: 每页数量
        group_name: 分组名称（模糊查询）
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        分组列表
    """
    service = GroupService(db)
    return await service.get_groups(
        page=page,
        size=size,
        group_name=group_name,
    )


@router.get("/{group_id}", response_model=dict)
async def get_group_by_id(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """根据ID获取分组
    
    Args:
        group_id: 分组ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        分组对象
    """
    service = GroupService(db)
    return await service.get_group_by_id(group_id)


@router.put("/{group_id}", response_model=dict)
async def update_group(
    group_id: str,
    group_data: GroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新分组
    
    Args:
        group_id: 分组ID
        group_data: 分组更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的分组对象
    """
    service = GroupService(db)
    return await service.update_group(group_id, group_data, current_user)


@router.delete("/{group_id}", response_model=dict)
async def delete_group(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除分组
    
    Args:
        group_id: 分组ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = GroupService(db)
    return await service.delete_group(group_id, current_user)

