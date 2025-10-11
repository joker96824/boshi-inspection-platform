"""
地图路网数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from ..models.mapnet import MapNet
from ..models.map import Map


class MapNetRepository:
    """地图路网数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> MapNet:
        """创建路网元素"""
        mapnet = MapNet(**data)
        self.db.add(mapnet)
        await self.db.commit()
        await self.db.refresh(mapnet)
        return mapnet
    
    async def get_by_id(self, mapnet_id: str) -> Optional[MapNet]:
        """根据ID获取路网元素"""
        query = select(MapNet).where(MapNet.id == mapnet_id, MapNet.is_deleted == False)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, mapnet_ids: List[str]) -> List[MapNet]:
        """根据ID列表获取路网元素"""
        query = select(MapNet).where(
            MapNet.id.in_(mapnet_ids),
            MapNet.is_deleted == False
        ).order_by(MapNet.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_map_id(
        self, 
        map_id: str, 
        map_net_type: str = None,
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[MapNet], int]:
        """根据地图ID获取路网元素列表（支持元素类型过滤）"""
        # 构建基础查询条件
        conditions = [MapNet.map_id == map_id, MapNet.is_deleted == False]
        
        # 添加元素类型过滤条件
        if map_net_type and map_net_type.strip():
            conditions.append(MapNet.map_net_type.like(f"%{map_net_type.strip()}%"))
        
        # 查询总数
        count_query = select(func.count(MapNet.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # 查询数据列表
        query = (
            select(MapNet)
            .where(and_(*conditions))
            .order_by(MapNet.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        mapnets = result.scalars().all()
        
        return list(mapnets), total
    
    async def update(self, mapnet_id: str, data: Dict[str, Any]) -> Optional[MapNet]:
        """更新路网元素"""
        mapnet = await self.get_by_id(mapnet_id)
        if not mapnet:
            return None
        
        # 更新字段（包括0值）
        for key, value in data.items():
            if hasattr(mapnet, key):
                setattr(mapnet, key, value)
        
        await self.db.commit()
        await self.db.refresh(mapnet)
        return mapnet
    
    async def soft_delete(self, mapnet_id: str, deleted_by: str) -> bool:
        """软删除路网元素"""
        mapnet = await self.get_by_id(mapnet_id)
        if not mapnet:
            return False
        
        mapnet.is_deleted = True
        mapnet.updated_by = deleted_by
        
        await self.db.commit()
        return True
    
    async def count_by_map_id(self, map_id: str) -> int:
        """统计地图的路网元素数量"""
        query = select(func.count(MapNet.id)).where(
            MapNet.map_id == map_id, 
            MapNet.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar()
    
    async def get_types_by_map_id(self, map_id: str) -> List[str]:
        """获取地图中所有的路网元素类型"""
        query = (
            select(MapNet.map_net_type)
            .where(MapNet.map_id == map_id, MapNet.is_deleted == False)
            .distinct()
            .order_by(MapNet.map_net_type)
        )
        result = await self.db.execute(query)
        return [row[0] for row in result.fetchall()]
    
    async def check_map_access(self, map_id: str, user_id: str) -> bool:
        """检查用户是否有访问指定地图的权限"""
        query = select(Map).where(
            Map.id == map_id, 
            Map.user_id == user_id, 
            Map.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
