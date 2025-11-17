"""
任务日程API路由
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db, validate_pagination_params
from ...core.auth import get_current_user
from ...core.permissions import require_write_permission, require_read_permission, require_no_auth
from ...services.taskschedule_service import TaskScheduleService
from ...schemas.taskschedule import TaskScheduleCreate, TaskScheduleUpdate

router = APIRouter()


@router.post("/", response_model=dict)
async def create_taskschedule(
    taskschedule_data: TaskScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建任务日程
    
    Args:
        taskschedule_data: 任务日程创建数据（后端格式）
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的任务日程信息
    """
    taskschedule_service = TaskScheduleService(db)
    return await taskschedule_service.create_taskschedule(taskschedule_data, current_user)


@router.get("/", response_model=dict)
async def get_taskschedules(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    task_id: str = Query(None, description="任务ID"),
    cycle_type: Optional[str] = Query(None, description="周期类型：daily/monthly_days/weekly"),
    enabled: bool = Query(None, description="启用状态"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取任务日程列表
    
    Args:
        page: 页码
        size: 每页数量
        task_id: 任务ID
        cycle_type: 周期类型：daily/monthly_days/weekly
        enabled: 启用状态
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        任务日程列表
    """
    taskschedule_service = TaskScheduleService(db)
    return await taskschedule_service.get_taskschedules(
        current_user, page, size, task_id, cycle_type, enabled
    )


@router.get("/by-ids", response_model=dict)
async def get_taskschedules_by_ids(
    taskschedule_ids: List[str] = Query(..., description="任务日程ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表查询任务日程
    
    支持单个或多个ID查询
    
    Args:
        taskschedule_ids: 任务日程ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        任务日程列表
    """
    taskschedule_service = TaskScheduleService(db)
    return await taskschedule_service.get_taskschedules_by_ids(taskschedule_ids, current_user)


@router.get("/stats/{task_id}", response_model=dict)
async def get_taskschedule_stats(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取任务日程统计信息
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        任务日程统计信息
    """
    taskschedule_service = TaskScheduleService(db)
    return await taskschedule_service.get_taskschedule_stats(task_id, current_user)


@router.get("/{taskschedule_id}", response_model=dict)
async def get_taskschedule_by_id(
    taskschedule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取任务日程
    
    Args:
        taskschedule_id: 任务日程ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        任务日程详情
    """
    taskschedule_service = TaskScheduleService(db)
    return await taskschedule_service.get_taskschedule_by_id(taskschedule_id, current_user)


@router.put("/{taskschedule_id}", response_model=dict)
async def update_taskschedule(
    taskschedule_id: str,
    taskschedule_data: TaskScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新任务日程
    
    Args:
        taskschedule_id: 任务日程ID
        taskschedule_data: 任务日程更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的任务日程信息
    """
    taskschedule_service = TaskScheduleService(db)
    return await taskschedule_service.update_taskschedule(taskschedule_id, taskschedule_data, current_user)


@router.delete("/{taskschedule_id}", response_model=dict)
async def delete_taskschedule(
    taskschedule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除任务日程
    
    Args:
        taskschedule_id: 任务日程ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    taskschedule_service = TaskScheduleService(db)
    return await taskschedule_service.delete_taskschedule(taskschedule_id, current_user)
