"""
机器人相关API路由
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db
from ...core.auth import get_current_user
from ...core.permissions import require_write_permission, require_read_permission, require_no_auth
from ...schemas.robot import RobotCreate, RobotUpdate, RobotQuery
from ...services.robot_service import RobotService
from ...utils.response import ApiResponse

router = APIRouter()


@router.post("/", response_model=dict)
async def create_robot(
    robot_data: RobotCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建机器人
    
    Args:
        robot_data: 机器人创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的机器人对象
    """
    robot_service = RobotService(db)
    return await robot_service.create_robot(robot_data, current_user)


@router.get("/", response_model=dict)
async def get_user_robots(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    robot_name: str = Query(None, description="机器人名称（模糊匹配）"),
    factory_id: str = Query(None, description="厂区ID筛选"),
    map_id: str = Query(None, description="地图ID筛选（通过中间表）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取当前用户的机器人列表
    
    Args:
        page: 页码
        size: 每页数量
        robot_name: 机器人名称（模糊匹配）
        factory_id: 厂区ID筛选
        map_id: 地图ID筛选（通过中间表）
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        机器人列表
    """
    robot_service = RobotService(db)
    return await robot_service.get_user_robots(current_user, page, size, robot_name, factory_id, map_id)


@router.get("/by-ids", response_model=dict)
async def get_robots_by_ids(
    robot_ids: List[str] = Query(..., description="机器人ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表查询机器人
    
    支持单个或多个ID查询
    
    Args:
        robot_ids: 机器人ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        机器人列表
    """
    robot_service = RobotService(db)
    return await robot_service.get_robots_by_ids(robot_ids, current_user)


@router.get("/{robot_id}", response_model=dict)
async def get_robot_by_id(
    robot_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取机器人
    
    Args:
        robot_id: 机器人ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        机器人信息
    """
    robot_service = RobotService(db)
    return await robot_service.get_robot_by_id(robot_id, current_user)


@router.put("/{robot_id}", response_model=dict)
async def update_robot(
    robot_id: str,
    robot_data: RobotUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新机器人
    
    Args:
        robot_id: 机器人ID
        robot_data: 机器人更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的机器人对象
    """
    robot_service = RobotService(db)
    return await robot_service.update_robot(robot_id, robot_data, current_user)


@router.delete("/{robot_id}", response_model=dict)
async def delete_robot(
    robot_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除机器人
    
    Args:
        robot_id: 机器人ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    robot_service = RobotService(db)
    return await robot_service.delete_robot(robot_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_robot_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取机器人统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        机器人统计信息
    """
    robot_service = RobotService(db)
    return await robot_service.get_robot_stats(current_user)
