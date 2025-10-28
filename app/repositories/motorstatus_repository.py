"""
电机状态配置数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.motorstatus import MotorStatus
from ..core.exceptions import ResourceNotFoundError


class MotorStatusRepository:
    """电机状态配置数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> MotorStatus:
        """创建电机状态配置"""
        motor_status = MotorStatus(**data)
        self.db.add(motor_status)
        await self.db.commit()
        await self.db.refresh(motor_status)
        return motor_status

    async def get_by_id(self, status_id: str) -> Optional[MotorStatus]:
        """根据ID获取电机状态配置"""
        stmt = select(MotorStatus).where(
            MotorStatus.id == status_id,
            MotorStatus.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, page: int = 1, size: int = 20, 
                      motor_id: int = None, baud_rate: int = None) -> Tuple[List[MotorStatus], int]:
        """获取电机状态配置列表"""
        skip = (page - 1) * size
        conditions = [MotorStatus.is_deleted == False]
        
        if motor_id is not None:
            conditions.append(MotorStatus.motor_id == motor_id)
        if baud_rate is not None:
            conditions.append(MotorStatus.baud_rate == baud_rate)
        
        # 查询总数
        count_query = select(func.count(MotorStatus.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(MotorStatus)
                .where(and_(*conditions))
                .order_by(MotorStatus.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        status_configs = list(result.scalars().all())
        return status_configs, total

    async def get_by_ids(self, status_ids: List[str]) -> List[MotorStatus]:
        """根据ID列表获取电机状态配置"""
        stmt = select(MotorStatus).where(
            MotorStatus.id.in_(status_ids),
            MotorStatus.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, status_id: str, data: Dict[str, Any]) -> Optional[MotorStatus]:
        """更新电机状态配置"""
        stmt = select(MotorStatus).where(
            MotorStatus.id == status_id,
            MotorStatus.is_deleted == False
        )
        result = await self.db.execute(stmt)
        status_config = result.scalar_one_or_none()
        
        if not status_config:
            return None
        
        for key, value in data.items():
            if hasattr(status_config, key):
                setattr(status_config, key, value)
        
        await self.db.commit()
        await self.db.refresh(status_config)
        return status_config

    async def soft_delete(self, status_id: str, updated_by: str) -> bool:
        """软删除电机状态配置"""
        stmt = select(MotorStatus).where(
            MotorStatus.id == status_id,
            MotorStatus.is_deleted == False
        )
        result = await self.db.execute(stmt)
        status_config = result.scalar_one_or_none()
        
        if not status_config:
            return False
        
        status_config.is_deleted = True
        status_config.updated_by = updated_by
        await self.db.commit()
        return True

    async def get_stats(self) -> Dict[str, Any]:
        """获取电机状态配置统计信息"""
        # 总数统计
        total_stmt = select(func.count(MotorStatus.id)).where(MotorStatus.is_deleted == False)
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar() or 0
        
        # 按电机ID统计
        motor_stmt = select(
            MotorStatus.motor_id,
            func.count(MotorStatus.id).label('count')
        ).where(MotorStatus.is_deleted == False).group_by(MotorStatus.motor_id)
        motor_result = await self.db.execute(motor_stmt)
        motor_stats = {row.motor_id: row.count for row in motor_result}
        
        # 按波特率统计
        baud_stmt = select(
            MotorStatus.baud_rate,
            func.count(MotorStatus.id).label('count')
        ).where(MotorStatus.is_deleted == False).group_by(MotorStatus.baud_rate)
        baud_result = await self.db.execute(baud_stmt)
        baud_stats = {row.baud_rate: row.count for row in baud_result}
        
        # TPDO/RPDO配置统计
        tpdo_enabled_stmt = select(func.count(MotorStatus.id)).where(
            MotorStatus.is_deleted == False,
            MotorStatus.tpdo_config.isnot(None)
        )
        tpdo_enabled_result = await self.db.execute(tpdo_enabled_stmt)
        tpdo_enabled_count = tpdo_enabled_result.scalar() or 0
        
        rpdo_enabled_stmt = select(func.count(MotorStatus.id)).where(
            MotorStatus.is_deleted == False,
            MotorStatus.rpdo_config.isnot(None)
        )
        rpdo_enabled_result = await self.db.execute(rpdo_enabled_stmt)
        rpdo_enabled_count = rpdo_enabled_result.scalar() or 0
        
        return {
            "total": total,
            "motor_stats": motor_stats,
            "baud_stats": baud_stats,
            "config_stats": {
                "tpdo_enabled": tpdo_enabled_count,
                "rpdo_enabled": rpdo_enabled_count
            }
        }

