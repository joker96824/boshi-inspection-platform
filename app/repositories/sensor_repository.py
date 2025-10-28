"""
智能传感器数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.sensor import Sensor
from ..core.exceptions import ResourceNotFoundError


class SensorRepository:
    """智能传感器数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> Sensor:
        """创建智能传感器"""
        sensor = Sensor(**data)
        self.db.add(sensor)
        await self.db.commit()
        await self.db.refresh(sensor)
        return sensor
    
    async def get_by_id(self, sensor_id: str) -> Optional[Sensor]:
        """根据ID获取智能传感器"""
        query = select(Sensor).where(Sensor.id == sensor_id, Sensor.is_deleted == False)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, sensor_ids: List[str]) -> List[Sensor]:
        """根据ID列表获取智能传感器"""
        if not sensor_ids:
            return []
        
        query = select(Sensor).where(
            Sensor.id.in_(sensor_ids),
            Sensor.is_deleted == False
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(self, page: int = 1, size: int = 20, 
                     sensor_name: str = None, device_id: str = None) -> Tuple[List[Sensor], int]:
        """获取智能传感器列表"""
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [Sensor.is_deleted == False]
        
        if sensor_name:
            conditions.append(Sensor.sensor_name.like(f"%{sensor_name}%"))
        
        if device_id:
            conditions.append(Sensor.device_id == device_id)
        
        # 查询总数
        count_query = select(func.count(Sensor.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(Sensor)
                .where(and_(*conditions))
                .order_by(Sensor.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        sensors = list(result.scalars().all())
        
        return sensors, total
    
    async def update(self, sensor_id: str, data: Dict[str, Any]) -> Optional[Sensor]:
        """更新智能传感器"""
        sensor = await self.get_by_id(sensor_id)
        if not sensor:
            raise ResourceNotFoundError(f"智能传感器ID '{sensor_id}' 不存在")
        
        for key, value in data.items():
            setattr(sensor, key, value)
        
        await self.db.commit()
        await self.db.refresh(sensor)
        return sensor
    
    async def soft_delete(self, sensor_id: str, deleted_by: str) -> bool:
        """软删除智能传感器"""
        sensor = await self.get_by_id(sensor_id)
        if not sensor:
            return False
        
        sensor.is_deleted = True
        sensor.updated_by = deleted_by
        await self.db.commit()
        return True
    
    async def get_by_device_id(self, device_id: str) -> List[Sensor]:
        """根据设备ID获取所有智能传感器"""
        query = select(Sensor).where(
            Sensor.device_id == device_id,
            Sensor.is_deleted == False
        ).order_by(Sensor.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_all(self) -> int:
        """统计所有智能传感器数量"""
        stmt = select(func.count(Sensor.id)).where(Sensor.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

