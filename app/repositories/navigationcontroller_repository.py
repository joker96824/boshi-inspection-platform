"""
导航控制器配置数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.navigationcontroller import NavigationController
from ..core.exceptions import ResourceNotFoundError


class NavigationControllerRepository:
    """导航控制器配置数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> NavigationController:
        """创建导航控制器配置"""
        navigation_controller = NavigationController(**data)
        self.db.add(navigation_controller)
        await self.db.commit()
        await self.db.refresh(navigation_controller)
        return navigation_controller

    async def get_by_id(self, controller_id: str) -> Optional[NavigationController]:
        """根据ID获取导航控制器配置"""
        stmt = select(NavigationController).where(
            NavigationController.id == controller_id,
            NavigationController.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, page: int = 1, size: int = 20, 
                      module_group: int = None, ethernet_ip: str = None, 
                      ethernet_port: int = None, baud_rate: int = None) -> Tuple[List[NavigationController], int]:
        """获取导航控制器配置列表"""
        skip = (page - 1) * size
        conditions = [NavigationController.is_deleted == False]
        
        if module_group is not None:
            conditions.append(NavigationController.module_group == module_group)
        if ethernet_ip is not None:
            conditions.append(NavigationController.ethernet_ip.like(f"%{ethernet_ip}%"))
        if ethernet_port is not None:
            conditions.append(NavigationController.ethernet_port == ethernet_port)
        if baud_rate is not None:
            conditions.append(NavigationController.baud_rate == baud_rate)
        
        # 查询总数
        count_query = select(func.count(NavigationController.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(NavigationController)
                .where(and_(*conditions))
                .order_by(NavigationController.module_group.asc(), NavigationController.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        navigation_controllers = list(result.scalars().all())
        return navigation_controllers, total

    async def get_by_ids(self, controller_ids: List[str]) -> List[NavigationController]:
        """根据ID列表获取导航控制器配置"""
        stmt = select(NavigationController).where(
            NavigationController.id.in_(controller_ids),
            NavigationController.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_module_group(self, module_group: int) -> List[NavigationController]:
        """根据模块组获取导航控制器配置"""
        stmt = select(NavigationController).where(
            NavigationController.module_group == module_group,
            NavigationController.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, controller_id: str, data: Dict[str, Any]) -> Optional[NavigationController]:
        """更新导航控制器配置"""
        stmt = select(NavigationController).where(
            NavigationController.id == controller_id,
            NavigationController.is_deleted == False
        )
        result = await self.db.execute(stmt)
        navigation_controller = result.scalar_one_or_none()
        
        if not navigation_controller:
            return None
        
        for key, value in data.items():
            if hasattr(navigation_controller, key):
                setattr(navigation_controller, key, value)
        
        await self.db.commit()
        await self.db.refresh(navigation_controller)
        return navigation_controller

    async def soft_delete(self, controller_id: str, updated_by: str) -> bool:
        """软删除导航控制器配置"""
        stmt = select(NavigationController).where(
            NavigationController.id == controller_id,
            NavigationController.is_deleted == False
        )
        result = await self.db.execute(stmt)
        navigation_controller = result.scalar_one_or_none()
        
        if not navigation_controller:
            return False
        
        navigation_controller.is_deleted = True
        navigation_controller.updated_by = updated_by
        await self.db.commit()
        return True

    async def get_stats(self) -> Dict[str, Any]:
        """获取导航控制器配置统计信息"""
        # 总数统计
        total_stmt = select(func.count(NavigationController.id)).where(NavigationController.is_deleted == False)
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar() or 0
        
        # 按模块组统计
        group_stmt = select(
            NavigationController.module_group,
            func.count(NavigationController.id).label('count')
        ).where(NavigationController.is_deleted == False).group_by(NavigationController.module_group)
        group_result = await self.db.execute(group_stmt)
        group_stats = {row.module_group: row.count for row in group_result}
        
        # 按以太网IP段统计
        ip_stmt = select(
            func.substring_index(NavigationController.ethernet_ip, '.', 3).label('ip_segment'),
            func.count(NavigationController.id).label('count')
        ).where(NavigationController.is_deleted == False).group_by('ip_segment')
        ip_result = await self.db.execute(ip_stmt)
        ip_stats = {row.ip_segment: row.count for row in ip_result}
        
        # 按端口统计
        port_stmt = select(
            NavigationController.ethernet_port,
            func.count(NavigationController.id).label('count')
        ).where(NavigationController.is_deleted == False).group_by(NavigationController.ethernet_port)
        port_result = await self.db.execute(port_stmt)
        port_stats = {row.ethernet_port: row.count for row in port_result}
        
        # 按波特率统计
        baud_stmt = select(
            NavigationController.baud_rate,
            func.count(NavigationController.id).label('count')
        ).where(NavigationController.is_deleted == False).group_by(NavigationController.baud_rate)
        baud_result = await self.db.execute(baud_stmt)
        baud_stats = {row.baud_rate: row.count for row in baud_result}
        
        # 速度参数统计
        velocity_stats_stmt = select(
            func.avg(NavigationController.max_linear_velocity).label('avg_linear_velocity'),
            func.min(NavigationController.max_linear_velocity).label('min_linear_velocity'),
            func.max(NavigationController.max_linear_velocity).label('max_linear_velocity'),
            func.avg(NavigationController.max_angular_velocity).label('avg_angular_velocity'),
            func.min(NavigationController.max_angular_velocity).label('min_angular_velocity'),
            func.max(NavigationController.max_angular_velocity).label('max_angular_velocity'),
            func.avg(NavigationController.acceleration).label('avg_acceleration'),
            func.avg(NavigationController.deceleration).label('avg_deceleration')
        ).where(NavigationController.is_deleted == False)
        velocity_result = await self.db.execute(velocity_stats_stmt)
        velocity_stats = velocity_result.first()
        
        return {
            "total": total,
            "group_stats": group_stats,
            "ip_stats": ip_stats,
            "port_stats": port_stats,
            "baud_stats": baud_stats,
            "velocity_stats": {
                "avg_linear_velocity": float(velocity_stats.avg_linear_velocity) if velocity_stats.avg_linear_velocity else 0,
                "min_linear_velocity": float(velocity_stats.min_linear_velocity) if velocity_stats.min_linear_velocity else 0,
                "max_linear_velocity": float(velocity_stats.max_linear_velocity) if velocity_stats.max_linear_velocity else 0,
                "avg_angular_velocity": float(velocity_stats.avg_angular_velocity) if velocity_stats.avg_angular_velocity else 0,
                "min_angular_velocity": float(velocity_stats.min_angular_velocity) if velocity_stats.min_angular_velocity else 0,
                "max_angular_velocity": float(velocity_stats.max_angular_velocity) if velocity_stats.max_angular_velocity else 0,
                "avg_acceleration": float(velocity_stats.avg_acceleration) if velocity_stats.avg_acceleration else 0,
                "avg_deceleration": float(velocity_stats.avg_deceleration) if velocity_stats.avg_deceleration else 0
            }
        }

