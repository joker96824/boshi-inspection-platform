"""
双光云台配置API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db, validate_pagination_params
from ...core.permissions import require_write_permission, require_no_auth
from ...services.dual_ptz_service import DualPTZService
from ...schemas.dualptz import (
    DualPTZCreate, DualPTZUpdate, DualPTZResponse, 
    DualPTZQuery, DualPTZListResponse, DualPTZBatchUpdate
)
from ...utils.response import ApiResponse

router = APIRouter()


@router.get("/", response_model=dict)
async def get_dual_ptz_configs(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    ptz_ip: Optional[str] = Query(None, description="云台IP筛选"),
    operating_speed: Optional[int] = Query(None, description="运行速度筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取双光云台配置列表"""
    query = DualPTZQuery(
        page=page,
        size=size,
        ptz_ip=ptz_ip,
        operating_speed=operating_speed
    )
    
    service = DualPTZService(db)
    return await service.get_ptz_configs(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_dual_ptz_configs_by_ids(
    dualptz_ids: List[str] = Query(..., description="双光云台配置ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表获取双光云台配置"""
    service = DualPTZService(db)
    return await service.get_ptz_configs_by_ids(dualptz_ids, current_user)


@router.get("/{ptz_id}", response_model=dict)
async def get_dual_ptz_config_by_id(
    ptz_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取双光云台配置"""
    service = DualPTZService(db)
    return await service.get_ptz_config_by_id(ptz_id, current_user)


@router.post("/", response_model=dict)
async def create_dual_ptz_config(
    data: DualPTZCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建双光云台配置"""
    service = DualPTZService(db)
    return await service.create_ptz_config(data, current_user)


@router.put("/batch-update-by-robot", response_model=dict)
async def batch_update_dual_ptz_configs_by_robot(
    data: DualPTZBatchUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """批量更新机器人的双光云台配置（真删除旧数据后重新添加）"""
    service = DualPTZService(db)
    return await service.batch_update_ptz_configs_by_robot(data.robot_id, data.configs, current_user)


@router.put("/{ptz_id}", response_model=dict)
async def update_dual_ptz_config(
    ptz_id: str,
    data: DualPTZUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新双光云台配置（单个，兼容旧接口）"""
    service = DualPTZService(db)
    return await service.update_ptz_config(ptz_id, data, current_user)


@router.delete("/{ptz_id}", response_model=dict)
async def delete_dual_ptz_config(
    ptz_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除双光云台配置"""
    service = DualPTZService(db)
    return await service.delete_ptz_config(ptz_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_dual_ptz_config_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取双光云台配置统计信息"""
    service = DualPTZService(db)
    return await service.get_ptz_config_stats(current_user)
