"""
巡检项目API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db, validate_pagination_params
from ...core.permissions import require_write_permission, require_read_permission, require_no_auth
from ...services.item_service import ItemService
from ...schemas.item import ItemCreate, ItemUpdate, ItemResponse, ItemQuery, ItemListResponse
from ...utils.response import ApiResponse

router = APIRouter()


@router.post("/", response_model=dict)
async def create_item(
    item_data: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建巡检项目
    
    Args:
        item_data: 巡检项目创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的巡检项目信息
    """
    service = ItemService(db)
    return await service.create_item(item_data, current_user)


@router.get("/", response_model=dict)
async def get_items(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    item_name: Optional[str] = Query(None, description="巡检项目名称（模糊查询）"),
    device_id: Optional[str] = Query(None, description="设备ID（筛选）"),
    robot_id: Optional[str] = Query(None, description="机器人ID（筛选）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取巡检项目列表
    
    Args:
        page: 页码
        size: 每页数量
        item_name: 巡检项目名称（模糊查询）
        device_id: 设备ID（筛选）
        robot_id: 机器人ID（筛选）
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        巡检项目列表和分页信息
    """
    query = ItemQuery(
        page=page,
        size=size,
        item_name=item_name,
        device_id=device_id,
        robot_id=robot_id
    )
    service = ItemService(db)
    return await service.get_items(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_items_by_ids(
    item_ids: List[str] = Query(..., description="巡检项目ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表查询巡检项目
    
    支持单个或多个ID查询
    
    Args:
        item_ids: 巡检项目ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        巡检项目列表
    """
    service = ItemService(db)
    return await service.get_items_by_ids(item_ids, current_user)


@router.get("/{item_id}", response_model=dict)
async def get_item_by_id(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取巡检项目详情
    
    Args:
        item_id: 巡检项目ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        巡检项目详情
    """
    service = ItemService(db)
    return await service.get_item_by_id(item_id, current_user)


@router.put("/{item_id}", response_model=dict)
async def update_item(
    item_id: str,
    item_data: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新巡检项目
    
    Args:
        item_id: 巡检项目ID
        item_data: 巡检项目更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的巡检项目信息
    """
    service = ItemService(db)
    return await service.update_item(item_id, item_data, current_user)


@router.delete("/{item_id}", response_model=dict)
async def delete_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除巡检项目
    
    Args:
        item_id: 巡检项目ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = ItemService(db)
    return await service.delete_item(item_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_item_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取巡检项目统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        巡检项目统计信息
    """
    service = ItemService(db)
    return await service.get_item_stats(current_user)
