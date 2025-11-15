"""
巡检点相关API路由
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db, validate_pagination_params
from ...core.auth import get_current_user
from ...core.permissions import require_write_permission, require_read_permission, require_no_auth
from ...schemas.point import PointCreate, PointUpdate, PointQuery
from ...services.point_service import PointService
from ...utils.response import ApiResponse

router = APIRouter()


@router.post("/", response_model=dict)
async def create_point(
    point_data: PointCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建巡检点
    
    Args:
        point_data: 巡检点创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的巡检点对象
    """
    point_service = PointService(db)
    return await point_service.create_point(point_data, current_user)


@router.get("/", response_model=dict)
async def get_points(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    point_name: str = Query(None, description="巡检点名称（模糊匹配）"),
    map_id: str = Query(None, description="地图ID（可选过滤）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取巡检点列表
    
    Args:
        page: 页码
        size: 每页数量
        point_name: 巡检点名称（模糊匹配）
        map_id: 地图ID（可选过滤）
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        巡检点列表
    """
    point_service = PointService(db)
    return await point_service.get_points(current_user, page, size, point_name, map_id)


@router.get("/by-ids", response_model=dict)
async def get_points_by_ids(
    point_ids: List[str] = Query(..., description="巡检点ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表查询巡检点
    
    支持单个或多个ID查询
    
    Args:
        point_ids: 巡检点ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        巡检点列表
    """
    point_service = PointService(db)
    return await point_service.get_points_by_ids(point_ids, current_user)


@router.get("/{point_id}", response_model=dict)
async def get_point_by_id(
    point_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取巡检点
    
    Args:
        point_id: 巡检点ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        巡检点信息
    """
    point_service = PointService(db)
    return await point_service.get_point_by_id(point_id, current_user)


@router.put("/{point_id}", response_model=dict)
async def update_point(
    point_id: str,
    point_data: PointUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新巡检点
    
    Args:
        point_id: 巡检点ID
        point_data: 巡检点更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的巡检点对象
    """
    point_service = PointService(db)
    return await point_service.update_point(point_id, point_data, current_user)


@router.delete("/{point_id}", response_model=dict)
async def delete_point(
    point_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除巡检点
    
    Args:
        point_id: 巡检点ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    point_service = PointService(db)
    return await point_service.delete_point(point_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_point_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取巡检点统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        巡检点统计信息
    """
    point_service = PointService(db)
    return await point_service.get_point_stats(current_user)
