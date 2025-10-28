"""
传感器记录数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.sensorhistory import SensorHistory
from ..core.exceptions import ResourceNotFoundError


class SensorHistoryRepository:
    """传感器记录数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> SensorHistory:
        """创建传感器记录"""
        history = SensorHistory(**data)
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history
    
    async def get_by_id(self, history_id: str) -> Optional[SensorHistory]:
        """根据ID获取传感器记录"""
        query = select(SensorHistory).where(
            SensorHistory.id == history_id,
            SensorHistory.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, history_ids: List[str]) -> List[SensorHistory]:
        """根据ID列表获取传感器记录"""
        if not history_ids:
            return []
        
        query = select(SensorHistory).where(
            SensorHistory.id.in_(history_ids),
            SensorHistory.is_deleted == False
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(self, page: int = 1, size: int = 20,
                     sensor_id: str = None) -> Tuple[List[SensorHistory], int]:
        """获取传感器记录列表"""
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [SensorHistory.is_deleted == False]
        
        if sensor_id:
            conditions.append(SensorHistory.sensor_id == sensor_id)
        
        # 查询总数
        count_query = select(func.count(SensorHistory.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(SensorHistory)
                .where(and_(*conditions))
                .order_by(SensorHistory.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        histories = list(result.scalars().all())
        
        return histories, total
    
    async def update(self, history_id: str, data: Dict[str, Any]) -> Optional[SensorHistory]:
        """更新传感器记录"""
        history = await self.get_by_id(history_id)
        if not history:
            raise ResourceNotFoundError(f"传感器记录ID '{history_id}' 不存在")
        
        for key, value in data.items():
            setattr(history, key, value)
        
        await self.db.commit()
        await self.db.refresh(history)
        return history
    
    async def soft_delete(self, history_id: str, deleted_by: str) -> bool:
        """软删除传感器记录"""
        history = await self.get_by_id(history_id)
        if not history:
            return False
        
        history.is_deleted = True
        history.updated_by = deleted_by
        await self.db.commit()
        return True
    
    async def get_by_sensor_id(self, sensor_id: str) -> List[SensorHistory]:
        """根据传感器ID获取所有传感器记录"""
        query = select(SensorHistory).where(
            SensorHistory.sensor_id == sensor_id,
            SensorHistory.is_deleted == False
        ).order_by(SensorHistory.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_all(self) -> int:
        """统计所有传感器记录数量"""
        stmt = select(func.count(SensorHistory.id)).where(SensorHistory.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar() or 0
