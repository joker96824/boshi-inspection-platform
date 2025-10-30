"""
手动操作记录数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime

from ..models.manualoperation import ManualOperation


class ManualOperationRepository:
    """手动操作记录数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> ManualOperation:
        """创建手动操作记录"""
        manual_operation = ManualOperation(**data)
        self.db.add(manual_operation)
        await self.db.commit()
        await self.db.refresh(manual_operation)
        return manual_operation

    async def get_by_id(self, operation_id: str) -> Optional[ManualOperation]:
        """根据ID获取手动操作记录"""
        stmt = select(ManualOperation).where(
            and_(
                ManualOperation.id == operation_id,
                ManualOperation.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, operation_ids: List[str]) -> List[ManualOperation]:
        """根据ID列表获取手动操作记录"""
        stmt = select(ManualOperation).where(
            and_(
                ManualOperation.id.in_(operation_ids),
                ManualOperation.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, operation_id: str, data: Dict[str, Any]) -> Optional[ManualOperation]:
        """更新手动操作记录"""
        stmt = select(ManualOperation).where(
            and_(
                ManualOperation.id == operation_id,
                ManualOperation.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        manual_operation = result.scalar_one_or_none()
        
        if manual_operation:
            for key, value in data.items():
                setattr(manual_operation, key, value)
            await self.db.commit()
            await self.db.refresh(manual_operation)
        
        return manual_operation

    async def soft_delete(self, operation_id: str, updated_by: str) -> bool:
        """软删除手动操作记录"""
        stmt = select(ManualOperation).where(
            and_(
                ManualOperation.id == operation_id,
                ManualOperation.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        manual_operation = result.scalar_one_or_none()
        
        if manual_operation:
            manual_operation.is_deleted = True
            manual_operation.updated_by = updated_by
            await self.db.commit()
            return True
        
        return False

    async def get_all(self, page: int = 1, size: int = 20,
                     user_id: str = None, username: str = None,
                     start_time: datetime = None, end_time: datetime = None) -> Tuple[List[ManualOperation], int]:
        """获取手动操作记录列表
        
        Args:
            page: 页码
            size: 每页数量
            user_id: 用户ID筛选
            username: 用户名筛选
            start_time: 开始时间筛选
            end_time: 结束时间筛选
            
        Returns:
            Tuple[List[ManualOperation], int]: 记录列表和总数
        """
        # 构建查询条件
        conditions = [ManualOperation.is_deleted == False]
        
        if user_id:
            conditions.append(ManualOperation.user_id == user_id)
        
        if username:
            conditions.append(ManualOperation.username.like(f"%{username}%"))
        
        if start_time:
            conditions.append(ManualOperation.operation_time >= start_time)
        
        if end_time:
            conditions.append(ManualOperation.operation_time <= end_time)

        # 查询总数
        count_stmt = select(ManualOperation).where(and_(*conditions))
        count_result = await self.db.execute(count_stmt)
        total = len(count_result.scalars().all())

        # 查询数据
        stmt = (
            select(ManualOperation)
            .where(and_(*conditions))
            .order_by(ManualOperation.operation_time.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        
        result = await self.db.execute(stmt)
        records = result.scalars().all()
        
        return list(records), total

    async def get_by_user_id(self, user_id: str) -> List[ManualOperation]:
        """根据用户ID获取手动操作记录"""
        stmt = (
            select(ManualOperation)
            .where(and_(
                ManualOperation.user_id == user_id,
                ManualOperation.is_deleted == False
            ))
            .order_by(ManualOperation.operation_time.desc())
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_time_range(self, start_time: datetime, end_time: datetime) -> List[ManualOperation]:
        """根据时间范围获取手动操作记录"""
        stmt = (
            select(ManualOperation)
            .where(and_(
                ManualOperation.operation_time >= start_time,
                ManualOperation.operation_time <= end_time,
                ManualOperation.is_deleted == False
            ))
            .order_by(ManualOperation.operation_time.desc())
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_stats(self) -> Dict[str, Any]:
        """获取手动操作记录统计信息"""
        # 总记录数
        total_stmt = select(ManualOperation).where(ManualOperation.is_deleted == False)
        total_result = await self.db.execute(total_stmt)
        total_count = len(total_result.scalars().all())

        # 今日记录数
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_stmt = select(ManualOperation).where(
            and_(
                ManualOperation.operation_time >= today,
                ManualOperation.is_deleted == False
            )
        )
        today_result = await self.db.execute(today_stmt)
        today_count = len(today_result.scalars().all())

        return {
            "total_count": total_count,
            "today_count": today_count
        }
