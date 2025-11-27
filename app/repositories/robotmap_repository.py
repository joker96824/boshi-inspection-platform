"""
机器人-地图关联数据仓库
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from ..models.robotmap import RobotMap
from ..models.robot import Robot
from ..models.map import Map
from ..config.logging import get_logger

logger = get_logger(__name__)


class RobotMapRepository:
    """机器人-地图关联数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> RobotMap:
        """创建机器人-地图关联"""
        robot_map = RobotMap(**data)
        self.db.add(robot_map)
        await self.db.commit()
        await self.db.refresh(robot_map)
        return robot_map
    
    async def get_by_id(self, robot_map_id: str) -> Optional[RobotMap]:
        """根据ID获取关联"""
        stmt = select(RobotMap).where(
            RobotMap.id == robot_map_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_robot_and_map(self, robot_id: str, map_id: str) -> Optional[RobotMap]:
        """根据机器人和地图ID获取关联"""
        stmt = select(RobotMap).where(
            RobotMap.robot_id == robot_id,
            RobotMap.map_id == map_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    
    async def get_maps_by_robot_id(self, robot_id: str) -> List[RobotMap]:
        """根据机器人ID获取所有关联的地图"""
        stmt = (
            select(RobotMap)
            .options(selectinload(RobotMap.map))
            .where(
                RobotMap.robot_id == robot_id
            )
            .order_by(RobotMap.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_robots_by_map_id(self, map_id: str) -> List[RobotMap]:
        """根据地图ID获取所有关联的机器人"""
        stmt = (
            select(RobotMap)
            .options(selectinload(RobotMap.robot))
            .where(
                RobotMap.map_id == map_id
            )
            .order_by(RobotMap.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def delete_by_robot_and_map(self, robot_id: str, map_id: str) -> bool:
        """删除机器人-地图关联（物理删除）"""
        from sqlalchemy import delete
        stmt = delete(RobotMap).where(
            RobotMap.robot_id == robot_id,
            RobotMap.map_id == map_id
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def delete_by_robot_id(self, robot_id: str) -> bool:
        """删除机器人的所有地图关联（物理删除）"""
        from sqlalchemy import delete
        stmt = delete(RobotMap).where(
            RobotMap.robot_id == robot_id
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def delete_by_map_id(self, map_id: str) -> bool:
        """删除地图的所有机器人关联（物理删除）"""
        from sqlalchemy import delete
        stmt = delete(RobotMap).where(
            RobotMap.map_id == map_id
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def exists(self, robot_id: str, map_id: str) -> bool:
        """检查关联是否存在"""
        robot_map = await self.get_by_robot_and_map(robot_id, map_id)
        return robot_map is not None

