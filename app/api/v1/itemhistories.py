"""
巡检记录API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_read_permission
from ...schemas.itemhistory import ItemHistoryCreate, ItemHistoryUpdate, ItemHistoryQuery
from ...services.itemhistory_service import ItemHistoryService

router = APIRouter()


@router.post("/", response_model=dict)
async def create_itemhistory(
    itemhistory_data: ItemHistoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建巡检记录
    
    Args:
        itemhistory_data: 巡检记录创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的巡检记录对象
    """
    service = ItemHistoryService(db)
    return await service.create_itemhistory(itemhistory_data, current_user)


@router.get("/from-taskhistories", response_model=dict)
async def get_itemhistories_from_taskhistories(
    taskhistory_ids: Optional[List[str]] = Query(None, description="任务记录ID列表（可选）"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    with_details: bool = Query(False, description="是否返回详细信息（显示巡检项目信息）"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """从任务记录角度查询巡检记录
    
    Args:
        taskhistory_ids: 任务记录ID列表（可选，不传则查询所有）
        page: 页码
        size: 每页数量
        with_details: 是否返回详细信息（显示巡检项目信息）
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        巡检记录列表
    """
    query = ItemHistoryQuery(
        page=page,
        size=size,
        taskhistory_ids=taskhistory_ids,
        item_ids=None
    )
    service = ItemHistoryService(db)
    
    if with_details:
        return await service.get_itemhistories_with_taskhistory_details(query, current_user)
    else:
        return await service.get_itemhistories(query, current_user)


@router.get("/from-items", response_model=dict)
async def get_itemhistories_from_items(
    item_ids: Optional[List[str]] = Query(None, description="巡检项目ID列表（可选）"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    with_details: bool = Query(False, description="是否返回详细信息（显示任务记录信息）"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """从巡检项目角度查询巡检记录
    
    Args:
        item_ids: 巡检项目ID列表（可选，不传则查询所有）
        page: 页码
        size: 每页数量
        with_details: 是否返回详细信息（显示任务记录信息）
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        巡检记录列表
    """
    query = ItemHistoryQuery(
        page=page,
        size=size,
        taskhistory_ids=None,
        item_ids=item_ids
    )
    service = ItemHistoryService(db)
    
    if with_details:
        return await service.get_itemhistories_with_item_details(query, current_user)
    else:
        return await service.get_itemhistories(query, current_user)


@router.get("/{itemhistory_id}", response_model=dict)
async def get_itemhistory_by_id(
    itemhistory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """根据ID获取巡检记录
    
    Args:
        itemhistory_id: 巡检记录ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        巡检记录信息
    """
    service = ItemHistoryService(db)
    return await service.get_itemhistory_by_id(itemhistory_id, current_user)


@router.put("/{itemhistory_id}", response_model=dict)
async def update_itemhistory(
    itemhistory_id: str,
    itemhistory_data: ItemHistoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新巡检记录
    
    Args:
        itemhistory_id: 巡检记录ID
        itemhistory_data: 巡检记录更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的巡检记录对象
    """
    service = ItemHistoryService(db)
    return await service.update_itemhistory(itemhistory_id, itemhistory_data, current_user)


@router.delete("/by-taskhistory/{taskhistory_id}", response_model=dict)
async def delete_itemhistories_by_taskhistory(
    taskhistory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除指定任务记录的所有关联记录（真删除）
    
    Args:
        taskhistory_id: 任务记录ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = ItemHistoryService(db)
    return await service.delete_itemhistories_by_taskhistory(taskhistory_id, current_user)


@router.delete("/{itemhistory_id}", response_model=dict)
async def delete_itemhistory(
    itemhistory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除巡检记录（真删除）
    
    Args:
        itemhistory_id: 巡检记录ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = ItemHistoryService(db)
    return await service.delete_itemhistory(itemhistory_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_itemhistory_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """获取巡检记录统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        巡检记录统计信息
    """
    service = ItemHistoryService(db)
    return await service.get_itemhistory_stats(current_user)
