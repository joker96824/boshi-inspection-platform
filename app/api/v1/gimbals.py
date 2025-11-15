"""
云台API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_no_auth
from ...services.gimbal_service import GimbalService
from ...schemas.gimbal import GimbalCreate, GimbalUpdate, GimbalResponse, GimbalQuery, GimbalListResponse
from ...utils.response import ApiResponse

router = APIRouter()


@router.post("/", response_model=dict)
async def create_gimbal(
    gimbal_data: GimbalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建云台
    
    Args:
        gimbal_data: 云台创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的云台信息
    """
    service = GimbalService(db)
    return await service.create_gimbal(gimbal_data, current_user)


@router.get("/", response_model=dict)
async def get_gimbals(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    gimbal_name: Optional[str] = Query(None, description="云台名称（模糊查询）"),
    map_id: Optional[str] = Query(None, description="地图ID筛选"),
    sort_by: str = Query("created_at", description="排序字段：created_at/gimbal_name/updated_at"),
    sort_order: str = Query("desc", description="排序方向：asc/desc"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取云台列表
    
    Args:
        page: 页码
        size: 每页数量
        gimbal_name: 云台名称（模糊查询）
        map_id: 地图ID筛选
        sort_by: 排序字段
        sort_order: 排序方向
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        云台列表和分页信息
    """
    query = GimbalQuery(
        page=page,
        size=size,
        gimbal_name=gimbal_name,
        map_id=map_id,
        sort_by=sort_by,
        sort_order=sort_order
    )
    service = GimbalService(db)
    return await service.get_gimbals(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_gimbals_by_ids(
    gimbal_ids: List[str] = Query(..., description="云台ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表查询云台
    
    支持单个或多个ID查询
    
    Args:
        gimbal_ids: 云台ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        云台列表
    """
    service = GimbalService(db)
    return await service.get_gimbals_by_ids(gimbal_ids, current_user)


@router.get("/{gimbal_id}", response_model=dict)
async def get_gimbal_by_id(
    gimbal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取云台详情
    
    Args:
        gimbal_id: 云台ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        云台详情
    """
    service = GimbalService(db)
    return await service.get_gimbal_by_id(gimbal_id, current_user)


@router.put("/{gimbal_id}", response_model=dict)
async def update_gimbal(
    gimbal_id: str,
    gimbal_data: GimbalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新云台
    
    Args:
        gimbal_id: 云台ID
        gimbal_data: 云台更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的云台信息
    """
    service = GimbalService(db)
    return await service.update_gimbal(gimbal_id, gimbal_data, current_user)


@router.delete("/{gimbal_id}", response_model=dict)
async def delete_gimbal(
    gimbal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除云台
    
    Args:
        gimbal_id: 云台ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = GimbalService(db)
    return await service.delete_gimbal(gimbal_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_gimbal_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取云台统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        云台统计信息
    """
    service = GimbalService(db)
    return await service.get_gimbal_stats(current_user)

