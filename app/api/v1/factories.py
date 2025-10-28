"""
厂区管理API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_no_auth
from ...services.factory_service import FactoryService
from ...schemas.factory import (
    FactoryCreate, FactoryUpdate, FactoryQuery
)
from ...config.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=dict)
async def create_factory(
    factory_data: FactoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建厂区
    
    Args:
        factory_data: 厂区创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建结果
    
    Raises:
        400: 厂区名称已存在
        401: 用户未认证
    """
    factory_service = FactoryService(db)
    return await factory_service.create_factory(factory_data, current_user)


@router.get("/", response_model=dict)
async def list_factories(
    factory_name: Optional[str] = Query(None, description="厂区名称筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取厂区列表
    
    Args:
        factory_name: 厂区名称筛选
        page: 页码
        size: 每页数量
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        厂区列表（分页）
    
    Raises:
        401: 用户未认证
    """
    query = FactoryQuery(factory_name=factory_name, page=page, size=size)
    factory_service = FactoryService(db)
    return await factory_service.list_factories(query, current_user)


@router.get("/{factory_id}", response_model=dict)
async def get_factory_by_id(
    factory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取厂区详情
    
    Args:
        factory_id: 厂区ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        厂区详情
    
    Raises:
        404: 厂区不存在
        401: 用户未认证
    """
    factory_service = FactoryService(db)
    return await factory_service.get_factory(factory_id, current_user)


@router.put("/{factory_id}", response_model=dict)
async def update_factory(
    factory_id: str,
    factory_data: FactoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新厂区信息
    
    Args:
        factory_id: 厂区ID
        factory_data: 更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新结果
    
    Raises:
        404: 厂区不存在
        400: 厂区名称已存在
        401: 用户未认证
    """
    factory_service = FactoryService(db)
    return await factory_service.update_factory(factory_id, factory_data, current_user)


@router.delete("/{factory_id}", response_model=dict)
async def delete_factory(
    factory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除厂区
    
    Args:
        factory_id: 厂区ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    
    Raises:
        404: 厂区不存在
        401: 用户未认证
    """
    factory_service = FactoryService(db)
    return await factory_service.delete_factory(factory_id, current_user)


@router.get("/by-ids", response_model=dict)
async def get_factories_by_ids(
    factory_ids: List[str] = Query(..., description="厂区ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表获取厂区
    
    Args:
        factory_ids: 厂区ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        厂区列表
    
    Raises:
        401: 用户未认证
    """
    factory_service = FactoryService(db)
    return await factory_service.get_factories_by_ids(factory_ids, current_user)

