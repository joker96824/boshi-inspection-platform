"""
巡检中间表API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_read_permission
from ...services.point_item_service import PointItemService
from ...schemas.point_item import PointItemCreate, PointItemUpdate, PointItemResponse, PointItemQuery, PointItemListResponse, PointItemBatchUpdateByItem, PointItemBatchUpdateByPoint
from ...utils.response import ApiResponse

router = APIRouter()


@router.post("/", response_model=dict)
async def create_point_item(
    point_item_data: PointItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建巡检中间表记录
    
    Args:
        point_item_data: 巡检中间表创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的巡检中间表记录信息
    """
    service = PointItemService(db)
    return await service.create_point_item(point_item_data, current_user)


@router.get("/from-points", response_model=dict)
async def get_point_items_from_points(
    point_ids: Optional[List[str]] = Query(None, description="巡检点ID列表（可选）"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    with_details: bool = Query(False, description="是否返回详细信息（显示巡检项目信息）"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """从巡检点角度查询巡检中间表记录
    
    Args:
        point_ids: 巡检点ID列表（可选，不传则查询所有）
        page: 页码
        size: 每页数量
        with_details: 是否返回详细信息（显示巡检项目信息）
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        巡检中间表记录列表和分页信息
    """
    query = PointItemQuery(
        page=page,
        size=size,
        point_ids=point_ids,
        item_ids=None
    )
    service = PointItemService(db)
    
    if with_details:
        return await service.get_point_items_with_item_details(query, current_user)
    else:
        return await service.get_point_items(query, current_user)


@router.get("/from-items", response_model=dict)
async def get_point_items_from_items(
    item_ids: Optional[List[str]] = Query(None, description="巡检项目ID列表（可选）"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    with_details: bool = Query(False, description="是否返回详细信息（显示巡检点信息）"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """从巡检项目角度查询巡检中间表记录
    
    Args:
        item_ids: 巡检项目ID列表（可选，不传则查询所有）
        page: 页码
        size: 每页数量
        with_details: 是否返回详细信息（显示巡检点信息）
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        巡检中间表记录列表和分页信息
    """
    query = PointItemQuery(
        page=page,
        size=size,
        point_ids=None,
        item_ids=item_ids
    )
    service = PointItemService(db)
    
    if with_details:
        return await service.get_point_items_with_point_details(query, current_user)
    else:
        return await service.get_point_items(query, current_user)


@router.get("/{point_item_id}", response_model=dict)
async def get_point_item_by_id(
    point_item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """根据ID获取巡检中间表记录详情
    
    Args:
        point_item_id: 巡检中间表记录ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        巡检中间表记录详情
    """
    service = PointItemService(db)
    return await service.get_point_item_by_id(point_item_id, current_user)


@router.put("/by-item/{item_id}", response_model=dict)
async def update_point_item_by_item(
    item_id: str,
    request_data: PointItemBatchUpdateByItem,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """通过巡检项目ID批量更新关联关系
    
    Args:
        item_id: 巡检项目ID
        request_data: 批量更新请求数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新结果
    """
    service = PointItemService(db)
    return await service.update_point_item_by_item(item_id, request_data.point_ids, current_user)


@router.put("/by-point/{point_id}", response_model=dict)
async def update_point_item_by_point(
    point_id: str,
    request_data: PointItemBatchUpdateByPoint,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """通过巡检点ID批量更新关联关系
    
    Args:
        point_id: 巡检点ID
        request_data: 批量更新请求数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新结果
    """
    service = PointItemService(db)
    return await service.update_point_item_by_point(point_id, request_data.item_ids, current_user)


@router.delete("/by-item/{item_id}", response_model=dict)
async def delete_point_items_by_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除指定巡检项目的所有关联记录（真删除）
    
    Args:
        item_id: 巡检项目ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = PointItemService(db)
    return await service.delete_point_items_by_item(item_id, current_user)


@router.delete("/by-point/{point_id}", response_model=dict)
async def delete_point_items_by_point(
    point_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除指定巡检点的所有关联记录（真删除）
    
    Args:
        point_id: 巡检点ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = PointItemService(db)
    return await service.delete_point_items_by_point(point_id, current_user)


@router.delete("/{point_item_id}", response_model=dict)
async def delete_point_item(
    point_item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除巡检中间表记录（真删除）
    
    Args:
        point_item_id: 巡检中间表记录ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = PointItemService(db)
    return await service.delete_point_item(point_item_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_point_item_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """获取巡检中间表统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        巡检中间表统计信息
    """
    service = PointItemService(db)
    return await service.get_point_item_stats(current_user)
