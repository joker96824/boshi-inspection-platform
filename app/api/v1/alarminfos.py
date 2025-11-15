"""
报警信息API路由
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db, validate_pagination_params
from ...core.permissions import require_write_permission, require_read_permission, require_no_auth
from ...services.alarminfo_service import AlarmInfoService
from ...schemas.alarminfo import (
    AlarmInfoCreate, AlarmInfoUpdate, AlarmInfoQuery,
    AlarmInfoResponse, AlarmInfoListResponse
)

router = APIRouter()


@router.post("/", response_model=dict)
async def create_alarminfo(
    alarminfo_data: AlarmInfoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建报警信息
    
    Args:
        alarminfo_data: 报警信息创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的报警信息对象
    """
    service = AlarmInfoService(db)
    return await service.create_alarminfo(alarminfo_data, current_user)


@router.get("/by-ids", response_model=dict)
async def get_alarminfos_by_ids(
    alarminfo_ids: List[str] = Query(..., description="报警信息ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表查询报警信息
    
    支持单个或多个ID查询
    
    Args:
        alarminfo_ids: 报警信息ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        报警信息列表
    """
    service = AlarmInfoService(db)
    return await service.get_alarminfos_by_ids(alarminfo_ids, current_user)


@router.get("/", response_model=dict)
async def get_alarminfos(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    alarmrule_id: Optional[str] = Query(None, description="报警规则ID"),
    itemhistory_id: Optional[str] = Query(None, description="巡检记录ID"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """分页查询报警信息列表
    
    Args:
        page: 页码
        size: 每页数量
        alarmrule_id: 报警规则ID（可选）
        itemhistory_id: 巡检记录ID（可选）
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        分页的报警信息列表
    """
    query = AlarmInfoQuery(page=page, size=size, alarmrule_id=alarmrule_id, itemhistory_id=itemhistory_id)
    service = AlarmInfoService(db)
    return await service.get_alarminfos(query, current_user)


@router.get("/{alarminfo_id}", response_model=dict)
async def get_alarminfo_by_id(
    alarminfo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取报警信息
    
    Args:
        alarminfo_id: 报警信息ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        报警信息对象
    """
    service = AlarmInfoService(db)
    return await service.get_alarminfo_by_id(alarminfo_id, current_user)


@router.put("/{alarminfo_id}", response_model=dict)
async def update_alarminfo(
    alarminfo_id: str,
    alarminfo_data: AlarmInfoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新报警信息
    
    Args:
        alarminfo_id: 报警信息ID
        alarminfo_data: 更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的报警信息对象
    """
    service = AlarmInfoService(db)
    return await service.update_alarminfo(alarminfo_id, alarminfo_data, current_user)


@router.delete("/{alarminfo_id}", response_model=dict)
async def delete_alarminfo(
    alarminfo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除报警信息（软删除）
    
    Args:
        alarminfo_id: 报警信息ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = AlarmInfoService(db)
    return await service.delete_alarminfo(alarminfo_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_alarminfo_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取报警信息统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        统计信息
    """
    service = AlarmInfoService(db)
    return await service.get_alarminfo_stats(current_user)

