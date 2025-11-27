"""
检测类型业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.detectiontype_repository import DetectionTypeRepository
from ..schemas.detectiontype import DetectionTypeCreate, DetectionTypeUpdate
from ..core.exceptions import (
    ValidationError,
    BusinessError,
    ResourceNotFoundError,
)
from ..utils.response import ApiResponse


class DetectionTypeService:
    """检测类型业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DetectionTypeRepository(db)
    
    async def create_detection_type(self, data: DetectionTypeCreate, user: dict) -> Dict[str, Any]:
        """创建检测类型"""
        # 检查代码是否已存在
        if await self.repo.exists_by_code(data.type_code):
            raise BusinessError(f"检测类型代码 '{data.type_code}' 已存在")
        
        # 检查名称是否已存在
        if await self.repo.exists_by_name(data.type_name):
            raise BusinessError(f"检测类型名称 '{data.type_name}' 已存在")
        
        # 创建数据
        create_data = {
            **data.dict(),
            "created_by": user.get("username"),
            "updated_by": user.get("username"),
        }
        
        detection_type = await self.repo.create(create_data)
        return ApiResponse.success(
            data=self._format_detection_type_response(detection_type),
            message="检测类型创建成功"
        )
    
    async def get_detection_types(
        self,
        page: Optional[int] = None,
        size: Optional[int] = None,
        type_name: Optional[str] = None,
        type_code: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """获取检测类型列表"""
        items, total = await self.repo.get_all(
            page=page,
            size=size,
            type_name=type_name,
            type_code=type_code,
            enabled=enabled,
        )
        
        formatted_items = [self._format_detection_type_response(item) for item in items]
        
        if page is not None and size is not None:
            return ApiResponse.paginated(
                items=formatted_items,
                total=total,
                page=page,
                size=size
            )
        else:
            return ApiResponse.success(data=formatted_items, message="获取成功")
    
    async def get_detection_type_by_id(self, detection_type_id: str) -> Dict[str, Any]:
        """根据ID获取检测类型"""
        detection_type = await self.repo.get_by_id(detection_type_id)
        if not detection_type:
            raise ResourceNotFoundError(f"检测类型 '{detection_type_id}' 不存在")
        
        return ApiResponse.success(
            data=self._format_detection_type_response(detection_type),
            message="获取成功"
        )
    
    async def update_detection_type(
        self,
        detection_type_id: str,
        data: DetectionTypeUpdate,
        user: dict
    ) -> Dict[str, Any]:
        """更新检测类型"""
        detection_type = await self.repo.get_by_id(detection_type_id)
        if not detection_type:
            raise ResourceNotFoundError(f"检测类型 '{detection_type_id}' 不存在")
        
        update_data = data.dict(exclude_unset=True)
        
        # 检查代码是否已存在（排除自己）
        if "type_code" in update_data:
            if await self.repo.exists_by_code(update_data["type_code"], exclude_id=detection_type_id):
                raise BusinessError(f"检测类型代码 '{update_data['type_code']}' 已存在")
        
        # 检查名称是否已存在（排除自己）
        if "type_name" in update_data:
            if await self.repo.exists_by_name(update_data["type_name"], exclude_id=detection_type_id):
                raise BusinessError(f"检测类型名称 '{update_data['type_name']}' 已存在")
        
        update_data["updated_by"] = user.get("username")
        updated = await self.repo.update(detection_type_id, update_data)
        
        if not updated:
            raise ResourceNotFoundError(f"检测类型 '{detection_type_id}' 不存在")
        
        return ApiResponse.success(
            data=self._format_detection_type_response(updated),
            message="检测类型更新成功"
        )
    
    async def delete_detection_type(self, detection_type_id: str, user: dict) -> Dict[str, Any]:
        """删除检测类型"""
        detection_type = await self.repo.get_by_id(detection_type_id)
        if not detection_type:
            raise ResourceNotFoundError(f"检测类型 '{detection_type_id}' 不存在")
        
        success = await self.repo.delete(detection_type_id, user)
        if not success:
            raise ResourceNotFoundError(f"检测类型 '{detection_type_id}' 不存在")
        
        return ApiResponse.success(message="检测类型删除成功")
    
    def _format_detection_type_response(self, detection_type) -> Dict[str, Any]:
        """格式化检测类型响应数据"""
        return {
            "id": detection_type.id,
            "type_name": detection_type.type_name,
            "type_code": detection_type.type_code,
            "description": detection_type.description,
            "sort_order": detection_type.sort_order,
            "enabled": detection_type.enabled,
            "created_at": detection_type.created_at.strftime("%Y-%m-%dT%H:%M:%S") if detection_type.created_at else None,
            "updated_at": detection_type.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if detection_type.updated_at else None,
            "created_by": detection_type.created_by,
            "updated_by": detection_type.updated_by,
        }

