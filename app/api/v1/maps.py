"""
地图管理API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ...core.deps import get_db
from ...core.auth import get_current_user
from ...core.permissions import require_write_permission, require_read_permission
from ...services.map_service import MapService
from ...schemas.map import (
    MapCreate, MapUpdate, MapResponse, MapQuery, MapListResponse
)
from ...config.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=dict)
async def create_map(
    map_data: MapCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建地图
    
    Args:
        map_data: 地图创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建结果
    
    Raises:
        400: 地图名称已存在
        401: 用户未认证
    """
    map_service = MapService(db)
    return await map_service.create_map(map_data, current_user)


@router.get("/", response_model=dict)
async def get_user_maps(
    map_name: Optional[str] = Query(None, description="地图名称（模糊匹配）"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """获取当前用户的地图列表
    
    Args:
        map_name: 地图名称模糊匹配（可选）
        page: 页码
        size: 每页数量
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        地图列表（分页）
    
    Raises:
        401: 用户未认证
    """
    query = MapQuery(map_name=map_name, page=page, size=size)
    map_service = MapService(db)
    return await map_service.get_user_maps(query, current_user)


@router.get("/{map_id}", response_model=dict)
async def get_map_by_id(
    map_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """根据ID获取地图详情
    
    Args:
        map_id: 地图ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        地图详情
    
    Raises:
        404: 地图不存在或无权限访问
        401: 用户未认证
    """
    map_service = MapService(db)
    return await map_service.get_map_by_id(map_id, current_user)


@router.put("/{map_id}", response_model=dict)
async def update_map(
    map_id: str,
    map_data: MapUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新地图信息
    
    Args:
        map_id: 地图ID
        map_data: 更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新结果
    
    Raises:
        404: 地图不存在或无权限访问
        400: 地图名称已存在
        401: 用户未认证
    """
    map_service = MapService(db)
    return await map_service.update_map(map_id, map_data, current_user)


@router.delete("/{map_id}", response_model=dict)
async def delete_map(
    map_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除地图
    
    Args:
        map_id: 地图ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    
    Raises:
        404: 地图不存在或无权限访问
        401: 用户未认证
    """
    map_service = MapService(db)
    return await map_service.delete_map(map_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_map_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """获取当前用户的地图统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        地图统计信息
    
    Raises:
        401: 用户未认证
    """
    map_service = MapService(db)
    return await map_service.get_map_stats(current_user)
