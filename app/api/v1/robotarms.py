"""
机械臂状态配置API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db, validate_pagination_params
from ...core.permissions import require_write_permission, require_no_auth
from ...services.robot_arm_service import RobotArmService
from ...schemas.robotarm import (
    RobotArmCreate, RobotArmUpdate, RobotArmResponse, 
    RobotArmQuery, RobotArmListResponse
)
from ...utils.response import ApiResponse

router = APIRouter()


@router.get("/", response_model=dict)
async def get_robot_arms(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    robot_arm_ip: Optional[str] = Query(None, description="机械臂IP筛选"),
    robot_arm_port: Optional[int] = Query(None, description="机械臂端口筛选"),
    operating_speed: Optional[int] = Query(None, description="运行速度筛选"),
    collision_detection_level: Optional[str] = Query(None, description="碰撞检测级别筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取机械臂状态配置列表"""
    query = RobotArmQuery(
        page=page,
        size=size,
        robot_arm_ip=robot_arm_ip,
        robot_arm_port=robot_arm_port,
        operating_speed=operating_speed,
        collision_detection_level=collision_detection_level
    )
    
    service = RobotArmService(db)
    return await service.get_robot_arms(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_robot_arms_by_ids(
    robotarm_ids: List[str] = Query(..., description="机械臂状态配置ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表获取机械臂状态配置"""
    service = RobotArmService(db)
    return await service.get_robot_arms_by_ids(robotarm_ids, current_user)


@router.get("/{arm_id}", response_model=dict)
async def get_robot_arm_by_id(
    arm_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取机械臂状态配置"""
    service = RobotArmService(db)
    return await service.get_robot_arm_by_id(arm_id, current_user)


@router.post("/", response_model=dict)
async def create_robot_arm(
    data: RobotArmCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建机械臂状态配置"""
    service = RobotArmService(db)
    return await service.create_robot_arm(data, current_user)


@router.put("/{arm_id}", response_model=dict)
async def update_robot_arm(
    arm_id: str,
    data: RobotArmUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新机械臂状态配置"""
    service = RobotArmService(db)
    return await service.update_robot_arm(arm_id, data, current_user)


@router.delete("/{arm_id}", response_model=dict)
async def delete_robot_arm(
    arm_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除机械臂状态配置"""
    service = RobotArmService(db)
    return await service.delete_robot_arm(arm_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_robot_arm_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取机械臂状态配置统计信息"""
    service = RobotArmService(db)
    return await service.get_robot_arm_stats(current_user)
