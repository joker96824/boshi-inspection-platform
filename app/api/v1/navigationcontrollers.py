"""
导航控制器配置API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_no_auth
from ...services.navigation_controller_service import NavigationControllerService
from ...schemas.navigationcontroller import (
    NavigationControllerCreate, NavigationControllerUpdate, NavigationControllerResponse, 
    NavigationControllerQuery, NavigationControllerListResponse
)
from ...utils.response import ApiResponse

router = APIRouter()


@router.get("/", response_model=dict)
async def get_navigation_controllers(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    module_group: Optional[int] = Query(None, description="模块组筛选"),
    ethernet_ip: Optional[str] = Query(None, description="以太网IP筛选"),
    ethernet_port: Optional[int] = Query(None, description="以太网端口筛选"),
    baud_rate: Optional[int] = Query(None, description="波特率筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取导航控制器配置列表"""
    query = NavigationControllerQuery(
        page=page,
        size=size,
        module_group=module_group,
        ethernet_ip=ethernet_ip,
        ethernet_port=ethernet_port,
        baud_rate=baud_rate
    )
    
    service = NavigationControllerService(db)
    return await service.get_navigation_controllers(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_navigation_controllers_by_ids(
    navigationcontroller_ids: List[str] = Query(..., description="导航控制器配置ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表获取导航控制器配置"""
    service = NavigationControllerService(db)
    return await service.get_navigation_controllers_by_ids(navigationcontroller_ids, current_user)


@router.get("/by-module-group/{module_group}", response_model=dict)
async def get_navigation_controllers_by_module_group(
    module_group: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据模块组获取导航控制器配置"""
    service = NavigationControllerService(db)
    return await service.get_navigation_controllers_by_module_group(module_group, current_user)


@router.get("/{controller_id}", response_model=dict)
async def get_navigation_controller_by_id(
    controller_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取导航控制器配置"""
    service = NavigationControllerService(db)
    return await service.get_navigation_controller_by_id(controller_id, current_user)


@router.post("/", response_model=dict)
async def create_navigation_controller(
    data: NavigationControllerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建导航控制器配置"""
    service = NavigationControllerService(db)
    return await service.create_navigation_controller(data, current_user)


@router.put("/{controller_id}", response_model=dict)
async def update_navigation_controller(
    controller_id: str,
    data: NavigationControllerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新导航控制器配置"""
    service = NavigationControllerService(db)
    return await service.update_navigation_controller(controller_id, data, current_user)


@router.delete("/{controller_id}", response_model=dict)
async def delete_navigation_controller(
    controller_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除导航控制器配置"""
    service = NavigationControllerService(db)
    return await service.delete_navigation_controller(controller_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_navigation_controller_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取导航控制器配置统计信息"""
    service = NavigationControllerService(db)
    return await service.get_navigation_controller_stats(current_user)


@router.get("/template/download")
async def download_navigation_controller_template(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """下载导航控制器配置模板
    
    权限要求：write 及以上
    
    Returns:
        Excel模板文件
    """
    service = NavigationControllerService(db)
    return await service.download_template()


@router.post("/export")
async def export_navigation_controllers(
    module_group: Optional[int] = Query(None, description="模块组筛选"),
    ethernet_ip: Optional[str] = Query(None, description="以太网IP筛选"),
    ethernet_port: Optional[int] = Query(None, description="以太网端口筛选"),
    baud_rate: Optional[int] = Query(None, description="波特率筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据筛选条件导出导航控制器配置数据
    
    Args:
        module_group: 模块组筛选
        ethernet_ip: 以太网IP筛选
        ethernet_port: 以太网端口筛选
        baud_rate: 波特率筛选
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        Excel数据文件
    """
    service = NavigationControllerService(db)
    return await service.export_navigation_controllers_by_filter(
        module_group=module_group,
        ethernet_ip=ethernet_ip,
        ethernet_port=ethernet_port,
        baud_rate=baud_rate,
        user=current_user
    )


@router.post("/export/by-ids")
async def export_navigation_controllers_by_ids(
    controller_ids: List[str] = Query(..., description="导航控制器ID列表"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表导出导航控制器配置数据
    
    Args:
        controller_ids: 导航控制器ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        Excel数据文件
    """
    service = NavigationControllerService(db)
    return await service.export_navigation_controllers_by_ids(
        controller_ids=controller_ids,
        user=current_user
    )


@router.post("/import", response_model=dict)
async def import_navigation_controllers(
    file: UploadFile = File(..., description="Excel文件"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """导入导航控制器配置数据
    
    权限要求：write 及以上
    
    Args:
        file: Excel文件
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        导入结果
    """
    # 验证文件类型
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持Excel文件格式(.xlsx, .xls)")
    
    # 读取文件内容
    file_content = await file.read()
    
    service = NavigationControllerService(db)
    return await service.import_navigation_controllers(file_content, current_user)
