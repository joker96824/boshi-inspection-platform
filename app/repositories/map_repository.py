"""
地图数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from ..models.map import Map
from ..models.robot import Robot
from ..models.robotmap import RobotMap
from ..models.point import Point
from ..models.device import Device
from ..models.item import Item
from ..models.user import User


class MapRepository:
    """地图数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> Map:
        """创建地图"""
        map_obj = Map(**data)
        self.db.add(map_obj)
        await self.db.commit()
        await self.db.refresh(map_obj)
        return map_obj
    
    async def get_by_id(self, map_id: str) -> Optional[Map]:
        """根据ID获取地图"""
        query = select(Map).where(Map.id == map_id, Map.is_deleted == False)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_user_id(
        self, 
        user_id: str, 
        map_name: str = None,
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[Map], int]:
        """根据用户ID获取地图列表（支持地图名模糊匹配）"""
        # 构建基础查询条件
        conditions = [Map.user_id == user_id, Map.is_deleted == False]
        
        # 添加地图名模糊匹配条件
        if map_name and map_name.strip():
            conditions.append(Map.map_name.like(f"%{map_name.strip()}%"))
        
        # 查询总数
        count_query = select(func.count(Map.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # 查询数据列表
        query = (
            select(Map)
            .where(and_(*conditions))
            .order_by(Map.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        maps = result.scalars().all()
        
        return list(maps), total
    
    async def update(self, map_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Map]:
        """更新地图"""
        # 先查询地图是否存在且属于该用户
        map_obj = await self.get_by_id(map_id, user_id)
        if not map_obj:
            return None
        
        # 更新字段（包括0值）
        for key, value in data.items():
            if hasattr(map_obj, key):
                setattr(map_obj, key, value)
        
        await self.db.commit()
        await self.db.refresh(map_obj)
        return map_obj
    
    async def soft_delete(self, map_id: str, deleted_by: str) -> bool:
        """软删除地图"""
        map_obj = await self.get_by_id(map_id)
        if not map_obj:
            return False
        
        map_obj.is_deleted = True
        map_obj.updated_by = deleted_by
        
        await self.db.commit()
        return True
    
    async def exists_by_name(self, user_id: str, map_name: str, exclude_map_id: str = None) -> bool:
        """检查地图名是否已存在（同一用户下）"""
        conditions = [
            Map.user_id == user_id,
            Map.map_name == map_name,
            Map.is_deleted == False
        ]
        
        if exclude_map_id:
            conditions.append(Map.id != exclude_map_id)
        
        query = select(Map).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def exists_by_name_global(self, map_name: str, exclude_map_id: str = None) -> bool:
        """检查地图名是否已存在（全局）"""
        conditions = [
            Map.map_name == map_name,
            Map.is_deleted == False
        ]
        
        if exclude_map_id:
            conditions.append(Map.id != exclude_map_id)
        
        query = select(Map).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def get_all_by_user(self, user_id: str) -> List[Map]:
        """获取用户的所有地图（不分页）"""
        query = (
            select(Map)
            .where(Map.user_id == user_id, Map.is_deleted == False)
            .order_by(Map.created_at.desc())
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(self, map_name: str = None, factory_id: str = None, skip: Optional[int] = None, limit: Optional[int] = None) -> Tuple[List[Map], int]:
        """获取所有地图列表"""
        # 构建查询条件
        conditions = [Map.is_deleted == False]
        if map_name:
            conditions.append(Map.map_name.like(f"%{map_name}%"))
        if factory_id:
            conditions.append(Map.factory_id == factory_id)
        
        # 查询总数
        count_query = select(func.count(Map.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = select(Map).where(and_(*conditions))
        if skip is not None and limit is not None:
            query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        maps = list(result.scalars().all())
        
        return maps, total

    async def count_by_user(self, user_id: str) -> int:
        """统计用户的地图数量"""
        query = select(func.count(Map.id)).where(
            Map.user_id == user_id, 
            Map.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar()

    async def get_map_with_related_data(self, map_id: str) -> Optional[Dict[str, Any]]:
        """获取地图及其关联的机器人、巡检点和巡检项目数据"""
        # 获取地图
        map_obj = await self.get_by_id(map_id)
        if not map_obj:
            return None

        # 通过中间表获取该地图下的所有机器人
        robots_query = (
            select(Robot)
            .join(RobotMap, Robot.id == RobotMap.robot_id)
            .where(
                RobotMap.map_id == map_id,
                RobotMap.is_deleted == False,
                Robot.is_deleted == False
            )
            .order_by(Robot.created_at.desc())
        )
        robots_result = await self.db.execute(robots_query)
        robots = list(robots_result.scalars().all())

        # 获取该地图下的所有巡检点（包含设备和巡检项目）
        points_query = (
            select(Point)
            .options(
                selectinload(Point.devices).selectinload(Device.items),
                selectinload(Point.devices).selectinload(Device.sensors)
            )
            .where(
                Point.map_id == map_id,
                Point.is_deleted == False
            )
            .order_by(Point.created_at.desc())
        )
        points_result = await self.db.execute(points_query)
        points = list(points_result.scalars().all())

        return {
            "map": map_obj,
            "robots": robots,
            "points": points
        }
