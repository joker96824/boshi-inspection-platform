"""
双光云台配置数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.dualptz import DualPTZ
from ..core.exceptions import ResourceNotFoundError


class DualPTZRepository:
    """双光云台配置数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> DualPTZ:
        """创建双光云台配置"""
        dual_ptz = DualPTZ(**data)
        self.db.add(dual_ptz)
        await self.db.commit()
        await self.db.refresh(dual_ptz)
        return dual_ptz

    async def get_by_id(self, ptz_id: str) -> Optional[DualPTZ]:
        """根据ID获取双光云台配置"""
        stmt = select(DualPTZ).where(
            DualPTZ.id == ptz_id,
            DualPTZ.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, page: int = 1, size: int = 20, 
                      ptz_ip: str = None, operating_speed: int = None) -> Tuple[List[DualPTZ], int]:
        """获取双光云台配置列表"""
        skip = (page - 1) * size
        conditions = [DualPTZ.is_deleted == False]
        
        if ptz_ip is not None:
            conditions.append(DualPTZ.ptz_ip.like(f"%{ptz_ip}%"))
        if operating_speed is not None:
            conditions.append(DualPTZ.operating_speed == operating_speed)
        
        # 查询总数
        count_query = select(func.count(DualPTZ.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(DualPTZ)
                .where(and_(*conditions))
                .order_by(DualPTZ.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        ptz_configs = list(result.scalars().all())
        return ptz_configs, total

    async def get_by_ids(self, ptz_ids: List[str]) -> List[DualPTZ]:
        """根据ID列表获取双光云台配置"""
        stmt = select(DualPTZ).where(
            DualPTZ.id.in_(ptz_ids),
            DualPTZ.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, ptz_id: str, data: Dict[str, Any]) -> Optional[DualPTZ]:
        """更新双光云台配置"""
        stmt = select(DualPTZ).where(
            DualPTZ.id == ptz_id,
            DualPTZ.is_deleted == False
        )
        result = await self.db.execute(stmt)
        ptz_config = result.scalar_one_or_none()
        
        if not ptz_config:
            return None
        
        for key, value in data.items():
            if hasattr(ptz_config, key):
                setattr(ptz_config, key, value)
        
        await self.db.commit()
        await self.db.refresh(ptz_config)
        return ptz_config

    async def soft_delete(self, ptz_id: str, updated_by: str) -> bool:
        """软删除双光云台配置"""
        stmt = select(DualPTZ).where(
            DualPTZ.id == ptz_id,
            DualPTZ.is_deleted == False
        )
        result = await self.db.execute(stmt)
        ptz_config = result.scalar_one_or_none()
        
        if not ptz_config:
            return False
        
        ptz_config.is_deleted = True
        ptz_config.updated_by = updated_by
        await self.db.commit()
        return True

    async def get_stats(self) -> Dict[str, Any]:
        """获取双光云台配置统计信息"""
        # 总数统计
        total_stmt = select(func.count(DualPTZ.id)).where(DualPTZ.is_deleted == False)
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar() or 0
        
        # 按IP段统计
        ip_stmt = select(
            func.substring_index(DualPTZ.ptz_ip, '.', 3).label('ip_segment'),
            func.count(DualPTZ.id).label('count')
        ).where(DualPTZ.is_deleted == False).group_by('ip_segment')
        ip_result = await self.db.execute(ip_stmt)
        ip_stats = {row.ip_segment: row.count for row in ip_result}
        
        # 按运行速度统计
        speed_stmt = select(
            DualPTZ.operating_speed,
            func.count(DualPTZ.id).label('count')
        ).where(DualPTZ.is_deleted == False).group_by(DualPTZ.operating_speed)
        speed_result = await self.db.execute(speed_stmt)
        speed_stats = {row.operating_speed: row.count for row in speed_result}
        
        # 功能统计
        fill_light_stmt = select(func.count(DualPTZ.id)).where(
            DualPTZ.is_deleted == False,
            DualPTZ.fill_light_enabled == True
        )
        fill_light_result = await self.db.execute(fill_light_stmt)
        fill_light_count = fill_light_result.scalar() or 0
        
        wiper_stmt = select(func.count(DualPTZ.id)).where(
            DualPTZ.is_deleted == False,
            DualPTZ.wiper_enabled == True
        )
        wiper_result = await self.db.execute(wiper_stmt)
        wiper_count = wiper_result.scalar() or 0
        
        auto_focus_stmt = select(func.count(DualPTZ.id)).where(
            DualPTZ.is_deleted == False,
            DualPTZ.auto_focus_enabled == True
        )
        auto_focus_result = await self.db.execute(auto_focus_stmt)
        auto_focus_count = auto_focus_result.scalar() or 0
        
        backlight_stmt = select(func.count(DualPTZ.id)).where(
            DualPTZ.is_deleted == False,
            DualPTZ.backlight_compensation_enabled == True
        )
        backlight_result = await self.db.execute(backlight_stmt)
        backlight_count = backlight_result.scalar() or 0
        
        return {
            "total": total,
            "ip_stats": ip_stats,
            "speed_stats": speed_stats,
            "feature_stats": {
                "fill_light_enabled": fill_light_count,
                "wiper_enabled": wiper_count,
                "auto_focus_enabled": auto_focus_count,
                "backlight_compensation_enabled": backlight_count
            }
        }

