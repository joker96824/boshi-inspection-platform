"""
设备数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from ..models.device import Device
from ..core.exceptions import ResourceNotFoundError


class DeviceRepository:
    """设备数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> Device:
        """创建设备"""
        device = Device(**data)
        self.db.add(device)
        await self.db.commit()
        await self.db.refresh(device)
        return device
    
    async def get_by_id(self, device_id: str) -> Optional[Device]:
        """根据ID获取设备"""
        query = (
            select(Device)
            .options(
                selectinload(Device.items),
                selectinload(Device.sensors)
            )
            .where(Device.id == device_id, Device.is_deleted == False)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, device_ids: List[str]) -> List[Device]:
        """根据ID列表获取设备"""
        if not device_ids:
            return []
        
        query = (
            select(Device)
            .options(
                selectinload(Device.items),
                selectinload(Device.sensors)
            )
            .where(
                Device.id.in_(device_ids),
                Device.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(self, page: Optional[int] = None, size: Optional[int] = None, 
                     device_name: str = None, point_id: str = None) -> Tuple[List[Device], int]:
        """获取设备列表"""
        # 如果未提供分页参数，返回所有数据
        if page is None or size is None:
            skip = None
            limit = None
        else:
            skip = (page - 1) * size
            limit = size
        
        # 构建查询条件
        conditions = [Device.is_deleted == False]
        
        if device_name:
            conditions.append(Device.device_name.like(f"%{device_name}%"))
        
        if point_id:
            conditions.append(Device.point_id == point_id)
        
        # 查询总数
        count_query = select(func.count(Device.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (
            select(Device)
            .options(
                selectinload(Device.items),
                selectinload(Device.sensors)
            )
            .where(and_(*conditions))
            .order_by(Device.created_at.desc())
        )
        if skip is not None and limit is not None:
            query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        devices = list(result.scalars().all())
        
        return devices, total
    
    async def update(self, device_id: str, data: Dict[str, Any]) -> Optional[Device]:
        """更新设备"""
        device = await self.get_by_id(device_id)
        if not device:
            raise ResourceNotFoundError(f"设备ID '{device_id}' 不存在")
        
        for key, value in data.items():
            setattr(device, key, value)
        
        await self.db.commit()
        await self.db.refresh(device)
        
        # 重新加载关联数据
        query = (
            select(Device)
            .options(
                selectinload(Device.items),
                selectinload(Device.sensors)
            )
            .where(Device.id == device_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def soft_delete(self, device_id: str, deleted_by: str) -> bool:
        """软删除设备"""
        device = await self.get_by_id(device_id)
        if not device:
            return False
        
        device.is_deleted = True
        device.updated_by = deleted_by
        await self.db.commit()
        return True
    
    async def exists_by_name(self, device_name: str, exclude_device_id: str = None) -> bool:
        """检查设备名是否已存在"""
        conditions = [
            Device.device_name == device_name,
            Device.is_deleted == False
        ]
        if exclude_device_id:
            conditions.append(Device.id != exclude_device_id)
        
        query = select(Device).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def count_all(self) -> int:
        """统计所有设备数量"""
        stmt = select(func.count(Device.id)).where(Device.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

