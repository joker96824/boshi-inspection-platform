"""
报警信息API路由
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_no_auth
from ...services.alarminfo_service import AlarmInfoService
from ...schemas.alarminfo import AlarmInfoQuery, AlarmInfoProcessRequest, AlarmInfoStatusUpdateRequest

router = APIRouter()


@router.get("/", response_model=dict)
async def get_alarminfos(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    alarm_rule_id: Optional[str] = Query(None, description="报警规则ID"),
    alarm_category: Optional[str] = Query(None, description="报警分类"),
    alarm_level: Optional[int] = Query(None, description="报警等级"),
    alarm_status: Optional[str] = Query(None, description="报警状态"),
    source_type: Optional[str] = Query(None, description="数据源类型"),
    relation_type: Optional[str] = Query(None, description="关联对象类型"),
    relation_id: Optional[str] = Query(None, description="关联对象ID"),
    trigger_item_id: Optional[str] = Query(None, description="触发源对应的巡检项目ID"),
    trigger_project_id: Optional[str] = Query(None, description="触发源对应的云台巡检项目ID"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """分页查询报警信息列表
    
    Args:
        page: 页码
        size: 每页数量
        alarm_rule_id: 报警规则ID
        alarm_category: 报警分类
        alarm_level: 报警等级
        alarm_status: 报警状态
        source_type: 数据源类型
        relation_type: 关联对象类型
        relation_id: 关联对象ID
        trigger_item_id: 触发源对应的巡检项目ID
        trigger_project_id: 触发源对应的云台巡检项目ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        分页的报警信息列表
    """
    query = AlarmInfoQuery(
        page=page,
        size=size,
        alarm_rule_id=alarm_rule_id,
        alarm_category=alarm_category,
        alarm_level=alarm_level,
        alarm_status=alarm_status,
        source_type=source_type,
        relation_type=relation_type,
        relation_id=relation_id,
        trigger_item_id=trigger_item_id,
        trigger_project_id=trigger_project_id
    )
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


@router.put("/{alarminfo_id}/view", response_model=dict)
async def view_alarm(
    alarminfo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """查看报警（同时更新报警信息和数据源的查看状态）
    
    此接口会：
    1. 将报警信息的 alarm_status 从 unviewed 更新为 unprocessed
    2. 根据 source_type 更新对应数据源的查看状态：
       - itemhistory: 更新 process_status 为 'viewed'
       - gimbalhistory/sensorhistory/robot_status: 暂不支持（无查看状态字段）
    
    注意：此接口不需要认证，任何人都可以查看报警
    
    Args:
        alarminfo_id: 报警信息ID
        db: 数据库会话
        current_user: 当前用户（可选）
    
    Returns:
        更新后的报警信息对象
    """
    service = AlarmInfoService(db)
    # 如果没有用户信息，使用默认值
    if not current_user:
        current_user = {"username": "anonymous", "role": "user"}
    return await service.view_alarm(alarminfo_id, current_user)


@router.put("/{alarminfo_id}/status", response_model=dict)
async def update_alarm_status(
    alarminfo_id: str,
    request: AlarmInfoStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新报警状态（直接更新状态，不更新数据源查看状态）
    
    Args:
        alarminfo_id: 报警信息ID
        request: 更新报警状态请求数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的报警信息对象
    """
    service = AlarmInfoService(db)
    return await service.update_alarm_status(alarminfo_id, request.alarm_status, current_user)


@router.put("/{alarminfo_id}/process", response_model=dict)
async def process_alarm(
    alarminfo_id: str,
    request: AlarmInfoProcessRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """处理报警
    
    Args:
        alarminfo_id: 报警信息ID
        request: 处理报警请求数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的报警信息对象
    """
    service = AlarmInfoService(db)
    return await service.process_alarm(alarminfo_id, request.process_remark, current_user)


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
async def get_alarm_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取报警统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        统计信息
    """
    service = AlarmInfoService(db)
    return await service.get_alarm_stats(current_user)
