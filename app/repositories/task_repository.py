"""
任务数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from ..models.task import Task
from ..models.map import Map
from ..models.robot import Robot
from ..core.exceptions import ResourceNotFoundError


class TaskRepository:
    """任务数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> Task:
        """创建任务"""
        task = Task(**data)
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task
    
    async def get_by_id(self, task_id: str) -> Optional[Task]:
        """根据ID获取任务"""
        stmt = select(Task).where(
            Task.id == task_id,
            Task.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, task_ids: List[str]) -> List[Task]:
        """根据ID列表获取任务"""
        query = select(Task).where(
            Task.id.in_(task_ids),
            Task.is_deleted == False
        ).order_by(Task.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(self, page: int = 1, size: int = 20, 
                      task_name: str = None, map_id: str = None, robot_id: str = None,
                      sort_by: str = "task_order", sort_order: str = "asc") -> tuple[List[Task], int]:
        """获取任务列表"""
        # 计算偏移量
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [Task.is_deleted == False]
        
        if task_name:
            conditions.append(Task.task_name.like(f"%{task_name}%"))
        if map_id:
            conditions.append(Task.map_id == map_id)
        if robot_id:
            conditions.append(Task.robot_id == robot_id)
        
        # 查询总数
        count_stmt = select(func.count(Task.id)).where(*conditions)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # 构建排序
        order_column = getattr(Task, sort_by, Task.task_order)
        if sort_order == "desc":
            order_column = order_column.desc()
        
        # 查询数据
        stmt = (select(Task)
                .where(*conditions)
                .order_by(order_column, Task.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(stmt)
        tasks = result.scalars().all()
        
        return list(tasks), total
    
    async def get_by_user_id(self, user_id: str, page: int = 1, size: int = 20,
                             task_name: str = None, sort_by: str = "task_order", sort_order: str = "asc") -> tuple[List[Task], int]:
        """根据用户ID获取任务列表（通过地图关联）"""
        # 计算偏移量
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [
            Task.is_deleted == False,
            Map.user_id == user_id,
            Map.is_deleted == False
        ]
        
        if task_name:
            conditions.append(Task.task_name.like(f"%{task_name}%"))
        
        # 查询总数
        count_stmt = (select(func.count(Task.id))
                     .join(Map, Task.map_id == Map.id)
                     .where(*conditions))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # 构建排序
        order_column = getattr(Task, sort_by, Task.task_order)
        if sort_order == "desc":
            order_column = order_column.desc()
        
        # 查询数据
        stmt = (select(Task)
                .join(Map, Task.map_id == Map.id)
                .where(*conditions)
                .order_by(order_column, Task.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(stmt)
        tasks = result.scalars().all()
        
        return list(tasks), total
    
    async def get_all(self, page: int = 1, size: int = 20, task_name: str = None, 
                     map_id: str = None, robot_id: str = None, 
                     sort_by: str = "task_order", sort_order: str = "asc") -> Tuple[List[Task], int]:
        """获取所有任务列表"""
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [Task.is_deleted == False]
        if task_name:
            conditions.append(Task.task_name.like(f"%{task_name}%"))
        if map_id:
            conditions.append(Task.map_id == map_id)
        if robot_id:
            conditions.append(Task.robot_id == robot_id)
        
        # 查询总数
        count_stmt = select(func.count(Task.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # 构建排序
        order_column = getattr(Task, sort_by, Task.task_order)
        if sort_order == "desc":
            order_column = order_column.desc()
        
        # 查询数据
        stmt = (select(Task)
                .where(and_(*conditions))
                .order_by(order_column, Task.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(stmt)
        tasks = result.scalars().all()
        
        return list(tasks), total
    
    async def update(self, task_id: str, data: Dict[str, Any]) -> Optional[Task]:
        """更新任务"""
        task = await self.get_by_id(task_id)
        if not task:
            raise ResourceNotFoundError(f"任务ID '{task_id}' 不存在")
        
        for key, value in data.items():
            setattr(task, key, value)
        
        await self.db.commit()
        await self.db.refresh(task)
        return task
    
    async def soft_delete(self, task_id: str) -> bool:
        """软删除任务"""
        task = await self.get_by_id(task_id)
        if not task:
            raise ResourceNotFoundError(f"任务ID '{task_id}' 不存在")
        
        task.is_deleted = True
        await self.db.commit()
        return True
    
    async def check_task_access(self, task_id: str, user_id: str) -> bool:
        """检查用户是否有权限访问该任务（通过地图权限检查）"""
        stmt = select(func.count(Task.id)).join(Map).where(
            Task.id == task_id,
            Map.user_id == user_id,
            Task.is_deleted == False,
            Map.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one() > 0
