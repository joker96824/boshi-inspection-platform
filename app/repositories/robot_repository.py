"""
机器人数据仓库
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from ..models.robot import Robot
from ..config.logging import get_logger

logger = get_logger(__name__)


class RobotRepository:
    """机器人数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> Robot:
        """创建机器人"""
        robot = Robot(**data)
        self.db.add(robot)
        await self.db.commit()
        await self.db.refresh(robot)
        return robot
    
    async def get_by_id(self, robot_id: str) -> Optional[Robot]:
        """根据ID获取机器人"""
        stmt = select(Robot).where(
            Robot.id == robot_id,
            Robot.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: str, page: int = 1, size: int = 20, robot_name: str = None) -> tuple[List[Robot], int]:
        """根据用户ID获取机器人列表"""
        # 计算偏移量
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [
            Robot.user_id == user_id,
            Robot.is_deleted == False
        ]
        
        # 添加机器人名称模糊匹配条件
        if robot_name:
            conditions.append(Robot.robot_name.like(f"%{robot_name}%"))
        
        # 查询总数
        count_stmt = select(func.count(Robot.id)).where(*conditions)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # 查询数据
        stmt = select(Robot).where(*conditions).order_by(Robot.created_at.desc()).offset(skip).limit(size)
        
        result = await self.db.execute(stmt)
        robots = result.scalars().all()
        
        return list(robots), total
    
    async def update(self, robot_id: str, data: Dict[str, Any]) -> Optional[Robot]:
        """更新机器人"""
        robot = await self.get_by_id(robot_id)
        if not robot:
            return None
        
        for key, value in data.items():
            if hasattr(robot, key):
                setattr(robot, key, value)
        
        await self.db.commit()
        await self.db.refresh(robot)
        return robot
    
    async def soft_delete(self, robot_id: str) -> bool:
        """软删除机器人"""
        robot = await self.get_by_id(robot_id)
        if not robot:
            return False
        
        robot.is_deleted = True
        await self.db.commit()
        return True
    
    async def count_by_user(self, user_id: str) -> int:
        """统计用户的机器人数量"""
        stmt = select(func.count(Robot.id)).where(
            Robot.user_id == user_id,
            Robot.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def count_all(self) -> int:
        """统计所有机器人数量"""
        stmt = select(func.count(Robot.id)).where(Robot.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def check_user_access(self, robot_id: str, user_id: str) -> bool:
        """检查用户是否有权限访问机器人"""
        stmt = select(Robot).where(
            Robot.id == robot_id,
            Robot.user_id == user_id,
            Robot.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
