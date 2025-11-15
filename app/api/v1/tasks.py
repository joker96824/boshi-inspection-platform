"""
任务API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db
from ...core.auth import get_current_user
from ...core.permissions import require_write_permission, require_read_permission, require_no_auth
from ...services.task_service import TaskService
from ...schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskQuery, TaskListResponse
from ...utils.response import ApiResponse

router = APIRouter()


@router.post("/", response_model=dict)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建任务
    
    Args:
        task_data: 任务创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的任务对象
    """
    service = TaskService(db)
    return await service.create_task(task_data, current_user)


@router.get("/", response_model=dict)
async def get_tasks(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    task_name: str = Query(None, description="任务名称（模糊匹配）"),
    robot_id: str = Query(None, description="机器人ID"),
    sort_by: str = Query("task_order", description="排序字段: task_order, task_res_prior, task_int_prior"),
    sort_order: str = Query("asc", description="排序顺序: asc(正序), desc(反序)"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取任务列表
    
    Args:
        page: 页码
        size: 每页数量
        task_name: 任务名称（模糊匹配）
        robot_id: 机器人ID
        sort_by: 排序字段
        sort_order: 排序顺序
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        任务列表
    """
    service = TaskService(db)
    return await service.get_tasks(
        current_user, page, size, task_name, robot_id, sort_by, sort_order
    )


@router.get("/by-ids", response_model=dict)
async def get_tasks_by_ids(
    task_ids: List[str] = Query(..., description="任务ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表查询任务
    
    支持单个或多个ID查询
    
    Args:
        task_ids: 任务ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        任务列表
    """
    service = TaskService(db)
    return await service.get_tasks_by_ids(task_ids, current_user)


@router.get("/{task_id}", response_model=dict)
async def get_task_by_id(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取任务
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        任务对象
    """
    service = TaskService(db)
    return await service.get_task_by_id(task_id, current_user)


@router.put("/{task_id}", response_model=dict)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新任务
    
    Args:
        task_id: 任务ID
        task_data: 任务更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的任务对象
    """
    service = TaskService(db)
    return await service.update_task(task_id, task_data, current_user)


@router.delete("/{task_id}", response_model=dict)
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除任务
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = TaskService(db)
    return await service.delete_task(task_id, current_user)