"""
检测类型数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from ..models.detectiontype import DetectionType
from ..core.exceptions import ResourceNotFoundError


class DetectionTypeRepository:
    """检测类型数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> DetectionType:
        """创建检测类型"""
        detection_type = DetectionType(**data)
        self.db.add(detection_type)
        await self.db.commit()
        await self.db.refresh(detection_type)
        return detection_type
    
    async def get_by_id(self, detection_type_id: str) -> Optional[DetectionType]:
        """根据ID获取检测类型"""
        query = (select(DetectionType)
                .where(DetectionType.id == detection_type_id, DetectionType.is_deleted == False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_code(self, type_code: str) -> Optional[DetectionType]:
        """根据代码获取检测类型"""
        query = (select(DetectionType)
                .where(DetectionType.type_code == type_code, DetectionType.is_deleted == False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        page: Optional[int] = None,
        size: Optional[int] = None,
        type_name: Optional[str] = None,
        type_code: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> Tuple[List[DetectionType], int]:
        """获取检测类型列表"""
        query = select(DetectionType).where(DetectionType.is_deleted == False)
        
        # 应用筛选条件
        if type_name:
            query = query.where(DetectionType.type_name.like(f"%{type_name}%"))
        if type_code:
            query = query.where(DetectionType.type_code == type_code)
        if enabled is not None:
            query = query.where(DetectionType.enabled == enabled)
        
        # 排序
        query = query.order_by(DetectionType.sort_order.asc(), DetectionType.created_at.asc(), DetectionType.id.asc())
        
        # 获取总数
        count_query = select(func.count()).select_from(DetectionType).where(DetectionType.is_deleted == False)
        if type_name:
            count_query = count_query.where(DetectionType.type_name.like(f"%{type_name}%"))
        if type_code:
            count_query = count_query.where(DetectionType.type_code == type_code)
        if enabled is not None:
            count_query = count_query.where(DetectionType.enabled == enabled)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页
        if page is not None and size is not None:
            offset = (page - 1) * size
            query = query.offset(offset).limit(size)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return items, total
    
    async def update(self, detection_type_id: str, data: Dict[str, Any]) -> Optional[DetectionType]:
        """更新检测类型"""
        detection_type = await self.get_by_id(detection_type_id)
        if not detection_type:
            return None
        
        for key, value in data.items():
            if hasattr(detection_type, key):
                setattr(detection_type, key, value)
        
        await self.db.commit()
        await self.db.refresh(detection_type)
        return detection_type
    
    async def delete(self, detection_type_id: str, user: dict) -> bool:
        """软删除检测类型"""
        detection_type = await self.get_by_id(detection_type_id)
        if not detection_type:
            return False
        
        detection_type.is_deleted = True
        detection_type.updated_by = user.get("username")
        await self.db.commit()
        return True
    
    async def exists_by_code(self, type_code: str, exclude_id: Optional[str] = None) -> bool:
        """检查代码是否存在"""
        query = select(DetectionType).where(
            DetectionType.type_code == type_code,
            DetectionType.is_deleted == False
        )
        if exclude_id:
            query = query.where(DetectionType.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def exists_by_name(self, type_name: str, exclude_id: Optional[str] = None) -> bool:
        """检查名称是否存在"""
        query = select(DetectionType).where(
            DetectionType.type_name == type_name,
            DetectionType.is_deleted == False
        )
        if exclude_id:
            query = query.where(DetectionType.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

