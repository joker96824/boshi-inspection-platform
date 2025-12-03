"""
超声波状态配置API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from decimal import Decimal

from ...core.deps import get_db, validate_pagination_params
from ...core.permissions import require_write_permission, require_no_auth
from ...services.ultrasonic_service import UltrasonicService
from ...schemas.ultrasonic import (
    UltrasonicCreate, UltrasonicUpdate, UltrasonicResponse, 
    UltrasonicQuery, UltrasonicListResponse, UltrasonicBatchUpdate
)
from ...utils.response import ApiResponse

router = APIRouter()


@router.get("/", response_model=dict)
async def get_ultrasonics(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    ultrasonic_id: Optional[int] = Query(None, description="超声波ID筛选"),
    baud_rate: Optional[int] = Query(None, description="波特率筛选"),
    obstacle_avoidance_distance_min: Optional[float] = Query(None, description="避障距离最小值筛选"),
    obstacle_avoidance_distance_max: Optional[float] = Query(None, description="避障距离最大值筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取超声波状态配置列表"""
    query = UltrasonicQuery(
        page=page,
        size=size,
        ultrasonic_id=ultrasonic_id,
        baud_rate=baud_rate,
        obstacle_avoidance_distance_min=Decimal(str(obstacle_avoidance_distance_min)) if obstacle_avoidance_distance_min is not None else None,
        obstacle_avoidance_distance_max=Decimal(str(obstacle_avoidance_distance_max)) if obstacle_avoidance_distance_max is not None else None
    )
    
    service = UltrasonicService(db)
    return await service.get_ultrasonics(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_ultrasonics_by_ids(
    ultrasonic_ids: List[str] = Query(..., description="超声波状态配置ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表获取超声波状态配置"""
    service = UltrasonicService(db)
    return await service.get_ultrasonics_by_ids(ultrasonic_ids, current_user)


@router.get("/{ultrasonic_id}", response_model=dict)
async def get_ultrasonic_by_id(
    ultrasonic_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取超声波状态配置"""
    service = UltrasonicService(db)
    return await service.get_ultrasonic_by_id(ultrasonic_id, current_user)


@router.post("/", response_model=dict)
async def create_ultrasonic(
    data: UltrasonicCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建超声波状态配置"""
    service = UltrasonicService(db)
    return await service.create_ultrasonic(data, current_user)


@router.put("/batch-update-by-robot", response_model=dict)
async def batch_update_ultrasonics_by_robot(
    data: UltrasonicBatchUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """批量更新机器人的超声波状态配置（真删除旧数据后重新添加）"""
    service = UltrasonicService(db)
    return await service.batch_update_ultrasonics_by_robot(data.robot_id, data.configs, current_user)


@router.put("/{ultrasonic_id}", response_model=dict)
async def update_ultrasonic(
    ultrasonic_id: str,
    data: UltrasonicUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新超声波状态配置（单个，兼容旧接口）"""
    service = UltrasonicService(db)
    return await service.update_ultrasonic(ultrasonic_id, data, current_user)


@router.delete("/{ultrasonic_id}", response_model=dict)
async def delete_ultrasonic(
    ultrasonic_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除超声波状态配置"""
    service = UltrasonicService(db)
    return await service.delete_ultrasonic(ultrasonic_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_ultrasonic_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取超声波状态配置统计信息"""
    service = UltrasonicService(db)
    return await service.get_ultrasonic_stats(current_user)
