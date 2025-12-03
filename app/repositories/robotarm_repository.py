"""
机械臂状态配置数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.robotarm import RobotArm
from ..core.exceptions import ResourceNotFoundError


class RobotArmRepository:
    """机械臂状态配置数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> RobotArm:
        """创建机械臂状态配置"""
        robot_arm = RobotArm(**data)
        self.db.add(robot_arm)
        await self.db.commit()
        await self.db.refresh(robot_arm)
        return robot_arm

    async def get_by_id(self, arm_id: str) -> Optional[RobotArm]:
        """根据ID获取机械臂状态配置"""
        stmt = select(RobotArm).where(
            RobotArm.id == arm_id,
            RobotArm.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, page: int = 1, size: int = 20, 
                      robot_arm_ip: str = None, robot_arm_port: int = None, 
                      operating_speed: int = None, collision_detection_level: str = None) -> Tuple[List[RobotArm], int]:
        """获取机械臂状态配置列表"""
        skip = (page - 1) * size
        conditions = [RobotArm.is_deleted == False]
        
        if robot_arm_ip is not None:
            conditions.append(RobotArm.robot_arm_ip.like(f"%{robot_arm_ip}%"))
        if robot_arm_port is not None:
            conditions.append(RobotArm.robot_arm_port == robot_arm_port)
        if operating_speed is not None:
            conditions.append(RobotArm.operating_speed == operating_speed)
        if collision_detection_level is not None:
            conditions.append(RobotArm.collision_detection_level == collision_detection_level)
        
        # 查询总数
        count_query = select(func.count(RobotArm.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(RobotArm)
                .where(and_(*conditions))
                .order_by(RobotArm.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        robot_arms = list(result.scalars().all())
        return robot_arms, total

    async def get_by_ids(self, arm_ids: List[str]) -> List[RobotArm]:
        """根据ID列表获取机械臂状态配置"""
        stmt = select(RobotArm).where(
            RobotArm.id.in_(arm_ids),
            RobotArm.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_robot_id(self, robot_id: str) -> Optional[RobotArm]:
        """根据机器人ID获取机械臂状态配置"""
        stmt = select(RobotArm).where(
            RobotArm.robot_id == robot_id,
            RobotArm.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, arm_id: str, data: Dict[str, Any]) -> Optional[RobotArm]:
        """更新机械臂状态配置"""
        stmt = select(RobotArm).where(
            RobotArm.id == arm_id,
            RobotArm.is_deleted == False
        )
        result = await self.db.execute(stmt)
        robot_arm = result.scalar_one_or_none()
        
        if not robot_arm:
            return None
        
        for key, value in data.items():
            if hasattr(robot_arm, key):
                setattr(robot_arm, key, value)
        
        await self.db.commit()
        await self.db.refresh(robot_arm)
        return robot_arm

    async def soft_delete(self, arm_id: str, updated_by: str) -> bool:
        """软删除机械臂状态配置"""
        stmt = select(RobotArm).where(
            RobotArm.id == arm_id,
            RobotArm.is_deleted == False
        )
        result = await self.db.execute(stmt)
        robot_arm = result.scalar_one_or_none()
        
        if not robot_arm:
            return False
        
        robot_arm.is_deleted = True
        robot_arm.updated_by = updated_by
        await self.db.commit()
        return True

    async def get_stats(self) -> Dict[str, Any]:
        """获取机械臂状态配置统计信息"""
        # 总数统计
        total_stmt = select(func.count(RobotArm.id)).where(RobotArm.is_deleted == False)
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar() or 0
        
        # 按IP段统计
        ip_stmt = select(
            func.substring_index(RobotArm.robot_arm_ip, '.', 3).label('ip_segment'),
            func.count(RobotArm.id).label('count')
        ).where(RobotArm.is_deleted == False).group_by('ip_segment')
        ip_result = await self.db.execute(ip_stmt)
        ip_stats = {row.ip_segment: row.count for row in ip_result}
        
        # 按端口统计
        port_stmt = select(
            RobotArm.robot_arm_port,
            func.count(RobotArm.id).label('count')
        ).where(RobotArm.is_deleted == False).group_by(RobotArm.robot_arm_port)
        port_result = await self.db.execute(port_stmt)
        port_stats = {row.robot_arm_port: row.count for row in port_result}
        
        # 按运行速度统计
        speed_stmt = select(
            RobotArm.operating_speed,
            func.count(RobotArm.id).label('count')
        ).where(RobotArm.is_deleted == False).group_by(RobotArm.operating_speed)
        speed_result = await self.db.execute(speed_stmt)
        speed_stats = {row.operating_speed: row.count for row in speed_result}
        
        # 按碰撞检测级别统计
        collision_stmt = select(
            RobotArm.collision_detection_level,
            func.count(RobotArm.id).label('count')
        ).where(RobotArm.is_deleted == False).group_by(RobotArm.collision_detection_level)
        collision_result = await self.db.execute(collision_stmt)
        collision_stats = {row.collision_detection_level: row.count for row in collision_result}
        
        # 负载大小统计
        load_stats_stmt = select(
            func.avg(RobotArm.load_size).label('avg_load'),
            func.min(RobotArm.load_size).label('min_load'),
            func.max(RobotArm.load_size).label('max_load')
        ).where(RobotArm.is_deleted == False)
        load_result = await self.db.execute(load_stats_stmt)
        load_stats = load_result.first()
        
        return {
            "total": total,
            "ip_stats": ip_stats,
            "port_stats": port_stats,
            "speed_stats": speed_stats,
            "collision_stats": collision_stats,
            "load_stats": {
                "avg_load": float(load_stats.avg_load) if load_stats.avg_load else 0,
                "min_load": float(load_stats.min_load) if load_stats.min_load else 0,
                "max_load": float(load_stats.max_load) if load_stats.max_load else 0
            }
        }

