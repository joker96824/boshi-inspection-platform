"""
环境传感器数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.environmentsensor import EnvironmentSensor
from ..core.exceptions import ResourceNotFoundError


class EnvironmentSensorRepository:
    """环境传感器数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> EnvironmentSensor:
        """创建环境传感器"""
        environment_sensor = EnvironmentSensor(**data)
        self.db.add(environment_sensor)
        await self.db.commit()
        await self.db.refresh(environment_sensor)
        return environment_sensor

    async def get_by_id(self, sensor_id: str) -> Optional[EnvironmentSensor]:
        """根据ID获取环境传感器"""
        stmt = select(EnvironmentSensor).where(
            EnvironmentSensor.id == sensor_id,
            EnvironmentSensor.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, page: int = 1, size: int = 20, 
                      station_number: int = None, baud_rate: int = None) -> Tuple[List[EnvironmentSensor], int]:
        """获取环境传感器列表"""
        skip = (page - 1) * size
        conditions = [EnvironmentSensor.is_deleted == False]
        
        if station_number is not None:
            conditions.append(EnvironmentSensor.station_number == station_number)
        if baud_rate is not None:
            conditions.append(EnvironmentSensor.baud_rate == baud_rate)
        
        # 查询总数
        count_query = select(func.count(EnvironmentSensor.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(EnvironmentSensor)
                .where(and_(*conditions))
                .order_by(EnvironmentSensor.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        sensors = list(result.scalars().all())
        return sensors, total

    async def get_by_ids(self, sensor_ids: List[str]) -> List[EnvironmentSensor]:
        """根据ID列表获取环境传感器"""
        stmt = select(EnvironmentSensor).where(
            EnvironmentSensor.id.in_(sensor_ids),
            EnvironmentSensor.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_robot_id(self, robot_id: str) -> Optional[EnvironmentSensor]:
        """根据机器人ID获取环境传感器"""
        stmt = select(EnvironmentSensor).where(
            EnvironmentSensor.robot_id == robot_id,
            EnvironmentSensor.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, sensor_id: str, data: Dict[str, Any]) -> Optional[EnvironmentSensor]:
        """更新环境传感器"""
        stmt = select(EnvironmentSensor).where(
            EnvironmentSensor.id == sensor_id,
            EnvironmentSensor.is_deleted == False
        )
        result = await self.db.execute(stmt)
        sensor = result.scalar_one_or_none()
        
        if not sensor:
            return None
        
        for key, value in data.items():
            if hasattr(sensor, key):
                setattr(sensor, key, value)
        
        await self.db.commit()
        await self.db.refresh(sensor)
        return sensor

    async def soft_delete(self, sensor_id: str, updated_by: str) -> bool:
        """软删除环境传感器"""
        stmt = select(EnvironmentSensor).where(
            EnvironmentSensor.id == sensor_id,
            EnvironmentSensor.is_deleted == False
        )
        result = await self.db.execute(stmt)
        sensor = result.scalar_one_or_none()
        
        if not sensor:
            return False
        
        sensor.is_deleted = True
        sensor.updated_by = updated_by
        await self.db.commit()
        return True

    async def get_stats(self) -> Dict[str, Any]:
        """获取环境传感器统计信息"""
        # 总数统计
        total_stmt = select(func.count(EnvironmentSensor.id)).where(EnvironmentSensor.is_deleted == False)
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar() or 0
        
        # 按站号统计
        station_stmt = select(
            EnvironmentSensor.station_number,
            func.count(EnvironmentSensor.id).label('count')
        ).where(EnvironmentSensor.is_deleted == False).group_by(EnvironmentSensor.station_number)
        station_result = await self.db.execute(station_stmt)
        station_stats = {row.station_number: row.count for row in station_result}
        
        # 按波特率统计
        baud_stmt = select(
            EnvironmentSensor.baud_rate,
            func.count(EnvironmentSensor.id).label('count')
        ).where(EnvironmentSensor.is_deleted == False).group_by(EnvironmentSensor.baud_rate)
        baud_result = await self.db.execute(baud_stmt)
        baud_stats = {row.baud_rate: row.count for row in baud_result}
        
        return {
            "total": total,
            "station_stats": station_stats,
            "baud_stats": baud_stats
        }

