"""
车体控制器API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db, validate_pagination_params
from ...core.permissions import require_write_permission, require_no_auth
from ...services.vehicle_controller_service import VehicleControllerService
from ...schemas.vehiclecontroller import (
    VehicleControllerCreate, VehicleControllerUpdate, VehicleControllerResponse, 
    VehicleControllerQuery, VehicleControllerListResponse
)
from ...utils.response import ApiResponse

router = APIRouter()


@router.get("/", response_model=dict)
async def get_vehicle_controllers(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    vehicle_model: Optional[str] = Query(None, description="车体模型筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取车体控制器列表"""
    query = VehicleControllerQuery(
        page=page,
        size=size,
        vehicle_model=vehicle_model
    )
    
    service = VehicleControllerService(db)
    return await service.get_controllers(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_vehicle_controllers_by_ids(
    vehiclecontroller_ids: List[str] = Query(..., description="车体控制器ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表获取车体控制器"""
    service = VehicleControllerService(db)
    return await service.get_controllers_by_ids(vehiclecontroller_ids, current_user)


@router.get("/{controller_id}", response_model=dict)
async def get_vehicle_controller_by_id(
    controller_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取车体控制器"""
    service = VehicleControllerService(db)
    return await service.get_controller_by_id(controller_id, current_user)


@router.post("/", response_model=dict)
async def create_vehicle_controller(
    data: VehicleControllerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建车体控制器"""
    service = VehicleControllerService(db)
    return await service.create_controller(data, current_user)


@router.put("/{controller_id}", response_model=dict)
async def update_vehicle_controller(
    controller_id: str,
    data: VehicleControllerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新车体控制器"""
    service = VehicleControllerService(db)
    return await service.update_controller(controller_id, data, current_user)


@router.delete("/{controller_id}", response_model=dict)
async def delete_vehicle_controller(
    controller_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除车体控制器"""
    service = VehicleControllerService(db)
    return await service.delete_controller(controller_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_vehicle_controller_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取车体控制器统计信息"""
    service = VehicleControllerService(db)
    return await service.get_controller_stats(current_user)
