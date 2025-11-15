"""
云台巡检项目API路由
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.deps import get_db, validate_pagination_params
from ...core.permissions import require_no_auth, require_write_permission
from ...schemas.gimbalinspectionproject import (
    GimbalInspectionProjectCreate,
    GimbalInspectionProjectQuery,
    GimbalInspectionProjectUpdate,
)
from ...services.gimbalinspectionproject_service import (
    GimbalInspectionProjectService,
)

router = APIRouter()


@router.post("/", response_model=dict)
async def create_gimbal_inspection_project(
    project_data: GimbalInspectionProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission),
):
    """创建云台巡检项目

    Args:
        project_data: 巡检项目创建数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        创建的云台巡检项目信息
    """
    service = GimbalInspectionProjectService(db)
    return await service.create_project(project_data, current_user)


@router.get("/", response_model=dict)
async def get_gimbal_inspection_projects(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    task_name: Optional[str] = Query(None, description="巡检项目名称（模糊查询）"),
    detection_type: Optional[str] = Query(
        None, description="检测类型筛选：可见光视频/可见光图片/热成像图片/热成像视频"
    ),
    gimbaltask_id: Optional[str] = Query(None, description="云台任务ID筛选"),
    gimbal_id: Optional[str] = Query(
        None, description="云台ID筛选（通过云台任务）"
    ),
    map_id: Optional[str] = Query(
        None, description="地图ID筛选（通过关联云台）"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth()),
):
    """获取云台巡检项目列表"""
    query = GimbalInspectionProjectQuery(
        page=page,
        size=size,
        task_name=task_name,
        detection_type=detection_type,
        gimbaltask_id=gimbaltask_id,
        gimbal_id=gimbal_id,
        map_id=map_id,
    )
    service = GimbalInspectionProjectService(db)
    return await service.get_projects(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_gimbal_inspection_projects_by_ids(
    inspection_project_ids: List[str] = Query(
        ..., description="云台巡检项目ID列表（支持单个或多个ID查询）"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth()),
):
    """根据ID列表查询云台巡检项目"""
    service = GimbalInspectionProjectService(db)
    return await service.get_projects_by_ids(inspection_project_ids, current_user)


@router.get("/{project_id}", response_model=dict)
async def get_gimbal_inspection_project_by_id(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth()),
):
    """根据ID获取云台巡检项目详情"""
    service = GimbalInspectionProjectService(db)
    return await service.get_project_by_id(project_id, current_user)


@router.put("/{project_id}", response_model=dict)
async def update_gimbal_inspection_project(
    project_id: str,
    project_data: GimbalInspectionProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission),
):
    """更新云台巡检项目"""
    service = GimbalInspectionProjectService(db)
    return await service.update_project(project_id, project_data, current_user)


@router.delete("/{project_id}", response_model=dict)
async def delete_gimbal_inspection_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission),
):
    """删除云台巡检项目"""
    service = GimbalInspectionProjectService(db)
    return await service.delete_project(project_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_gimbal_inspection_project_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth()),
):
    """获取云台巡检项目统计信息"""
    service = GimbalInspectionProjectService(db)
    return await service.get_project_stats(current_user)

