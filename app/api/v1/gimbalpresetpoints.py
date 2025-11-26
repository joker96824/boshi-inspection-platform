"""
云台预设点API路由
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db, validate_pagination_params
from ...core.permissions import require_write_permission, require_no_auth
from ...services.gimbalpresetpoint_service import GimbalPresetPointService
from ...schemas.gimbalpresetpoint import (
    GimbalPresetPointCreate,
    GimbalPresetPointUpdate,
    GimbalPresetPointQuery,
)
from ...utils.response import ApiResponse

router = APIRouter()


@router.post("/", response_model=dict)
async def create_preset_point(
    preset_point_data: GimbalPresetPointCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission),
):
    """创建云台预设点

    Args:
        preset_point_data: 预设点创建数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        创建的预设点信息
    """
    service = GimbalPresetPointService(db)
    return await service.create_preset_point(preset_point_data, current_user)


@router.get("/", response_model=dict)
async def get_preset_points(
    page: Optional[int] = Query(
        None, gt=0, description="页码（可选，大于0，必须与size同时提供）"
    ),
    size: Optional[int] = Query(
        None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"
    ),
    preset_name: Optional[str] = Query(None, description="预设点名称（模糊查询）"),
    gimbal_id: Optional[str] = Query(None, description="云台ID筛选"),
    sort_by: str = Query(
        "created_at", description="排序字段：created_at/preset_name/updated_at"
    ),
    sort_order: str = Query("desc", description="排序方向：asc/desc"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth()),
):
    """获取云台预设点列表

    Args:
        page: 页码
        size: 每页数量
        preset_name: 预设点名称（模糊查询）
        gimbal_id: 云台ID筛选
        sort_by: 排序字段
        sort_order: 排序方向
        db: 数据库会话
        current_user: 当前用户

    Returns:
        预设点列表和分页信息
    """
    validate_pagination_params(page, size)
    query = GimbalPresetPointQuery(
        page=page,
        size=size,
        preset_name=preset_name,
        gimbal_id=gimbal_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    service = GimbalPresetPointService(db)
    return await service.get_preset_points(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_preset_points_by_ids(
    preset_point_ids: List[str] = Query(
        ..., description="预设点ID列表（支持单个或多个ID查询）"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth()),
):
    """根据ID列表查询云台预设点

    支持单个或多个ID查询

    Args:
        preset_point_ids: 预设点ID列表
        db: 数据库会话
        current_user: 当前用户

    Returns:
        预设点列表
    """
    service = GimbalPresetPointService(db)
    return await service.get_preset_points_by_ids(preset_point_ids, current_user)


@router.get("/{preset_point_id}", response_model=dict)
async def get_preset_point_by_id(
    preset_point_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth()),
):
    """根据ID获取云台预设点详情

    Args:
        preset_point_id: 预设点ID
        db: 数据库会话
        current_user: 当前用户

    Returns:
        预设点详情
    """
    service = GimbalPresetPointService(db)
    return await service.get_preset_point_by_id(preset_point_id, current_user)


@router.put("/{preset_point_id}", response_model=dict)
async def update_preset_point(
    preset_point_id: str,
    preset_point_data: GimbalPresetPointUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission),
):
    """更新云台预设点

    Args:
        preset_point_id: 预设点ID
        preset_point_data: 预设点更新数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        更新后的预设点信息
    """
    service = GimbalPresetPointService(db)
    return await service.update_preset_point(
        preset_point_id, preset_point_data, current_user
    )


@router.delete("/{preset_point_id}", response_model=dict)
async def delete_preset_point(
    preset_point_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission),
):
    """删除云台预设点

    Args:
        preset_point_id: 预设点ID
        db: 数据库会话
        current_user: 当前用户

    Returns:
        删除结果
    """
    service = GimbalPresetPointService(db)
    return await service.delete_preset_point(preset_point_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_preset_point_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth()),
):
    """获取云台预设点统计信息

    Args:
        db: 数据库会话
        current_user: 当前用户

    Returns:
        预设点统计信息
    """
    service = GimbalPresetPointService(db)
    return await service.get_preset_point_stats(current_user)

