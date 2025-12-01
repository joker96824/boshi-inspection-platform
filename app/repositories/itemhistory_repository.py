"""
巡检记录数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from ..models.itemhistory import ItemHistory
from ..models.taskhistory import TaskHistory
from ..models.item import Item
from ..core.exceptions import ResourceNotFoundError


class ItemHistoryRepository:
    """巡检记录数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> ItemHistory:
        """创建巡检记录"""
        itemhistory = ItemHistory(**data)
        self.db.add(itemhistory)
        await self.db.commit()
        await self.db.refresh(itemhistory)
        return itemhistory
    
    async def get_by_id(self, itemhistory_id: str) -> Optional[ItemHistory]:
        """根据ID获取巡检记录"""
        query = select(ItemHistory).where(ItemHistory.id == itemhistory_id, ItemHistory.is_deleted == False)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_taskhistory_ids(self, taskhistory_ids: List[str]) -> List[ItemHistory]:
        """根据任务记录ID列表获取记录（预加载 item、device、point、detection_type 关系）"""
        if not taskhistory_ids:
            return []
        
        from ..models.item import Item
        from ..models.device import Device
        from ..models.point import Point
        from ..models.detectiontype import DetectionType
        
        query = (select(ItemHistory)
                .options(
                    selectinload(ItemHistory.item).selectinload(Item.device).selectinload(Device.point),
                    selectinload(ItemHistory.item).selectinload(Item.detection_type)
                )
                .where(ItemHistory.taskhistory_id.in_(taskhistory_ids), ItemHistory.is_deleted == False)
                .order_by(ItemHistory.taskhistory_id, ItemHistory.created_at))
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_item_ids(self, item_ids: List[str]) -> List[ItemHistory]:
        """根据巡检项目ID列表获取记录"""
        if not item_ids:
            return []
        
        query = (select(ItemHistory)
                .where(ItemHistory.item_id.in_(item_ids), ItemHistory.is_deleted == False)
                .order_by(ItemHistory.item_id, ItemHistory.created_at))
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(self, page: int = 1, size: int = 20, 
                     taskhistory_id: str = None, item_id: str = None,
                     taskhistory_ids: List[str] = None, item_ids: List[str] = None) -> Tuple[List[ItemHistory], int]:
        """获取巡检记录列表"""
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [ItemHistory.is_deleted == False]
        
        if taskhistory_id:
            conditions.append(ItemHistory.taskhistory_id == taskhistory_id)
        
        if item_id:
            conditions.append(ItemHistory.item_id == item_id)
        
        if taskhistory_ids:
            conditions.append(ItemHistory.taskhistory_id.in_(taskhistory_ids))
        
        if item_ids:
            conditions.append(ItemHistory.item_id.in_(item_ids))
        
        # 查询总数
        count_query = select(func.count(ItemHistory.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(ItemHistory)
                .where(and_(*conditions))
                .order_by(ItemHistory.taskhistory_id, ItemHistory.created_at)
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        itemhistories = list(result.scalars().all())
        
        return itemhistories, total
    
    async def get_with_taskhistory_details(self, page: int = 1, size: int = 20, 
                                          taskhistory_ids: List[str] = None) -> Tuple[List[Dict[str, Any]], int]:
        """通过任务记录查询，返回带巡检项目详情的记录列表"""
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [ItemHistory.is_deleted == False]
        
        if taskhistory_ids:
            conditions.append(ItemHistory.taskhistory_id.in_(taskhistory_ids))
        
        # 查询总数
        count_query = select(func.count(ItemHistory.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据（带巡检项目详情）
        query = (select(ItemHistory, TaskHistory, Item)
                .join(TaskHistory, ItemHistory.taskhistory_id == TaskHistory.id)
                .join(Item, ItemHistory.item_id == Item.id)
                .where(and_(*conditions))
                .order_by(ItemHistory.taskhistory_id, ItemHistory.created_at)
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        rows = result.all()
        
        # 格式化结果
        itemhistories_with_details = []
        for itemhistory, taskhistory, item in rows:
            itemhistories_with_details.append({
                "id": itemhistory.id,
                "taskhistory_id": itemhistory.taskhistory_id,
                "item_id": itemhistory.item_id,
                "item_result": itemhistory.item_result,
                "task_name": taskhistory.task_id,  # 这里可能需要根据实际需求调整
                "item_name": item.item_name,
                "item_info": item.item_info,
                "created_at": itemhistory.created_at,
                "updated_at": itemhistory.updated_at,
                "created_by": itemhistory.created_by,
                "updated_by": itemhistory.updated_by,
            })
        
        return itemhistories_with_details, total

    async def get_with_item_details(self, page: int = 1, size: int = 20, 
                                   item_ids: List[str] = None) -> Tuple[List[Dict[str, Any]], int]:
        """通过巡检项目查询，返回带任务记录详情的记录列表"""
        from ..models.device import Device
        from ..models.point import Point
        from ..models.task import Task
        from ..models.robot import Robot
        
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [ItemHistory.is_deleted == False]
        
        if item_ids:
            conditions.append(ItemHistory.item_id.in_(item_ids))
        
        # 查询总数
        count_query = select(func.count(ItemHistory.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据（带任务记录详情和相关关联数据）
        query = (select(ItemHistory, TaskHistory, Item, Device, Point, Task, Robot)
                .join(TaskHistory, ItemHistory.taskhistory_id == TaskHistory.id)
                .join(Item, ItemHistory.item_id == Item.id)
                .join(Device, Item.device_id == Device.id)
                .join(Point, Device.point_id == Point.id)
                .join(Task, TaskHistory.task_id == Task.id)
                .join(Robot, Task.robot_id == Robot.id)
                .where(and_(*conditions))
                .order_by(ItemHistory.item_id, ItemHistory.created_at)
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        rows = result.all()
        
        # 格式化结果
        itemhistories_with_details = []
        for itemhistory, taskhistory, item, device, point, task, robot in rows:
            itemhistories_with_details.append({
                "id": itemhistory.id,
                "taskhistory_id": itemhistory.taskhistory_id,
                "item_id": itemhistory.item_id,
                "item_result": itemhistory.item_result,
                "process_status": itemhistory.process_status,  # 处理状态
                "point_name": point.point_name if point else None,  # 巡检点名称
                "robot_name": robot.robot_name if robot else None,  # 机器人名称
                "record_start_time": taskhistory.record_start_time.strftime("%Y-%m-%dT%H:%M:%S") if taskhistory.record_start_time else None,  # 开始时间
                "record_end_time": taskhistory.record_end_time.strftime("%Y-%m-%dT%H:%M:%S") if taskhistory.record_end_time else None,  # 结束时间
                "task_name": task.task_name if task else None,  # 任务名称
                "item_name": item.item_name,
                "item_info": item.item_info,
                "created_at": itemhistory.created_at,
                "updated_at": itemhistory.updated_at,
                "created_by": itemhistory.created_by,
                "updated_by": itemhistory.updated_by,
            })
        
        return itemhistories_with_details, total
    
    async def update(self, itemhistory_id: str, data: Dict[str, Any]) -> Optional[ItemHistory]:
        """更新巡检记录"""
        itemhistory = await self.get_by_id(itemhistory_id)
        if not itemhistory:
            raise ResourceNotFoundError(f"巡检记录ID '{itemhistory_id}' 不存在")
        
        for key, value in data.items():
            setattr(itemhistory, key, value)
        
        await self.db.commit()
        await self.db.refresh(itemhistory)
        return itemhistory
    
    async def delete(self, itemhistory_id: str) -> bool:
        """真删除巡检记录"""
        itemhistory = await self.get_by_id(itemhistory_id)
        if not itemhistory:
            raise ResourceNotFoundError(f"巡检记录ID '{itemhistory_id}' 不存在")
        
        await self.db.delete(itemhistory)
        await self.db.commit()
        return True

    async def delete_by_taskhistory_id(self, taskhistory_id: str) -> int:
        """根据任务记录ID删除所有关联记录（真删除）"""
        stmt = select(ItemHistory).where(ItemHistory.taskhistory_id == taskhistory_id, ItemHistory.is_deleted == False)
        result = await self.db.execute(stmt)
        itemhistories = result.scalars().all()
        
        deleted_count = 0
        for itemhistory in itemhistories:
            await self.db.delete(itemhistory)
            deleted_count += 1
        
        await self.db.commit()
        return deleted_count

    async def exists_by_taskhistory_item(self, taskhistory_id: str, item_id: str, exclude_id: str = None) -> bool:
        """检查任务记录和巡检项目的关联是否已存在"""
        conditions = [
            ItemHistory.taskhistory_id == taskhistory_id,
            ItemHistory.item_id == item_id,
            ItemHistory.is_deleted == False
        ]
        if exclude_id:
            conditions.append(ItemHistory.id != exclude_id)
        
        query = select(ItemHistory).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def count_by_taskhistory(self, taskhistory_id: str) -> int:
        """统计任务记录的巡检项目数量"""
        stmt = select(func.count(ItemHistory.id)).where(
            ItemHistory.taskhistory_id == taskhistory_id,
            ItemHistory.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def count_by_item(self, item_id: str) -> int:
        """统计巡检项目的使用次数"""
        stmt = select(func.count(ItemHistory.id)).where(
            ItemHistory.item_id == item_id,
            ItemHistory.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def count_all(self) -> int:
        """统计所有巡检记录数量"""
        stmt = select(func.count(ItemHistory.id)).where(ItemHistory.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar() or 0
