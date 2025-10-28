"""
激光雷达配置数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.lidar import Lidar
from ..core.exceptions import ResourceNotFoundError


class LidarRepository:
    """激光雷达配置数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Lidar:
        """创建激光雷达配置"""
        lidar = Lidar(**data)
        self.db.add(lidar)
        await self.db.commit()
        await self.db.refresh(lidar)
        return lidar

    async def get_by_id(self, lidar_id: str) -> Optional[Lidar]:
        """根据ID获取激光雷达配置"""
        stmt = select(Lidar).where(
            Lidar.id == lidar_id,
            Lidar.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, page: int = 1, size: int = 20, 
                      lidar_ip: str = None, lidar_port: int = None, 
                      scan_frequency_rpm: int = None) -> Tuple[List[Lidar], int]:
        """获取激光雷达配置列表"""
        skip = (page - 1) * size
        conditions = [Lidar.is_deleted == False]
        
        if lidar_ip is not None:
            conditions.append(Lidar.lidar_ip.like(f"%{lidar_ip}%"))
        if lidar_port is not None:
            conditions.append(Lidar.lidar_port == lidar_port)
        if scan_frequency_rpm is not None:
            conditions.append(Lidar.scan_frequency_rpm == scan_frequency_rpm)
        
        # 查询总数
        count_query = select(func.count(Lidar.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(Lidar)
                .where(and_(*conditions))
                .order_by(Lidar.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        lidars = list(result.scalars().all())
        return lidars, total

    async def get_by_ids(self, lidar_ids: List[str]) -> List[Lidar]:
        """根据ID列表获取激光雷达配置"""
        stmt = select(Lidar).where(
            Lidar.id.in_(lidar_ids),
            Lidar.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, lidar_id: str, data: Dict[str, Any]) -> Optional[Lidar]:
        """更新激光雷达配置"""
        stmt = select(Lidar).where(
            Lidar.id == lidar_id,
            Lidar.is_deleted == False
        )
        result = await self.db.execute(stmt)
        lidar = result.scalar_one_or_none()
        
        if not lidar:
            return None
        
        for key, value in data.items():
            if hasattr(lidar, key):
                setattr(lidar, key, value)
        
        await self.db.commit()
        await self.db.refresh(lidar)
        return lidar

    async def soft_delete(self, lidar_id: str, updated_by: str) -> bool:
        """软删除激光雷达配置"""
        stmt = select(Lidar).where(
            Lidar.id == lidar_id,
            Lidar.is_deleted == False
        )
        result = await self.db.execute(stmt)
        lidar = result.scalar_one_or_none()
        
        if not lidar:
            return False
        
        lidar.is_deleted = True
        lidar.updated_by = updated_by
        await self.db.commit()
        return True

    async def get_stats(self) -> Dict[str, Any]:
        """获取激光雷达配置统计信息"""
        # 总数统计
        total_stmt = select(func.count(Lidar.id)).where(Lidar.is_deleted == False)
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar() or 0
        
        # 按IP段统计
        ip_stmt = select(
            func.substring_index(Lidar.lidar_ip, '.', 3).label('ip_segment'),
            func.count(Lidar.id).label('count')
        ).where(Lidar.is_deleted == False).group_by('ip_segment')
        ip_result = await self.db.execute(ip_stmt)
        ip_stats = {row.ip_segment: row.count for row in ip_result}
        
        # 按端口统计
        port_stmt = select(
            Lidar.lidar_port,
            func.count(Lidar.id).label('count')
        ).where(Lidar.is_deleted == False).group_by(Lidar.lidar_port)
        port_result = await self.db.execute(port_stmt)
        port_stats = {row.lidar_port: row.count for row in port_result}
        
        # 按扫描频率统计
        frequency_stmt = select(
            Lidar.scan_frequency_rpm,
            func.count(Lidar.id).label('count')
        ).where(Lidar.is_deleted == False).group_by(Lidar.scan_frequency_rpm)
        frequency_result = await self.db.execute(frequency_stmt)
        frequency_stats = {row.scan_frequency_rpm: row.count for row in frequency_result}
        
        # 扫描范围统计
        range_stats_stmt = select(
            func.avg(Lidar.scan_range_min).label('avg_range_min'),
            func.avg(Lidar.scan_range_max).label('avg_range_max'),
            func.min(Lidar.scan_range_min).label('min_range_min'),
            func.max(Lidar.scan_range_max).label('max_range_max')
        ).where(Lidar.is_deleted == False)
        range_result = await self.db.execute(range_stats_stmt)
        range_stats = range_result.first()
        
        # 扫描距离统计
        distance_stats_stmt = select(
            func.avg(Lidar.scan_distance_min).label('avg_distance_min'),
            func.avg(Lidar.scan_distance_max).label('avg_distance_max'),
            func.min(Lidar.scan_distance_min).label('min_distance_min'),
            func.max(Lidar.scan_distance_max).label('max_distance_max')
        ).where(Lidar.is_deleted == False)
        distance_result = await self.db.execute(distance_stats_stmt)
        distance_stats = distance_result.first()
        
        return {
            "total": total,
            "ip_stats": ip_stats,
            "port_stats": port_stats,
            "frequency_stats": frequency_stats,
            "range_stats": {
                "avg_range_min": float(range_stats.avg_range_min) if range_stats.avg_range_min else 0,
                "avg_range_max": float(range_stats.avg_range_max) if range_stats.avg_range_max else 0,
                "min_range_min": float(range_stats.min_range_min) if range_stats.min_range_min else 0,
                "max_range_max": float(range_stats.max_range_max) if range_stats.max_range_max else 0
            },
            "distance_stats": {
                "avg_distance_min": float(distance_stats.avg_distance_min) if distance_stats.avg_distance_min else 0,
                "avg_distance_max": float(distance_stats.avg_distance_max) if distance_stats.avg_distance_max else 0,
                "min_distance_min": float(distance_stats.min_distance_min) if distance_stats.min_distance_min else 0,
                "max_distance_max": float(distance_stats.max_distance_max) if distance_stats.max_distance_max else 0
            }
        }
