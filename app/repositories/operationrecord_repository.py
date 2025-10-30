"""
操作记录数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime

from ..models.operationrecord import OperationRecord


class OperationRecordRepository:
    """操作记录数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> OperationRecord:
        """创建操作记录"""
        operation_record = OperationRecord(**data)
        self.db.add(operation_record)
        await self.db.commit()
        await self.db.refresh(operation_record)
        return operation_record

    async def get_by_id(self, record_id: str) -> Optional[OperationRecord]:
        """根据ID获取操作记录"""
        stmt = select(OperationRecord).where(
            and_(
                OperationRecord.id == record_id,
                OperationRecord.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, record_ids: List[str]) -> List[OperationRecord]:
        """根据ID列表获取操作记录"""
        stmt = select(OperationRecord).where(
            and_(
                OperationRecord.id.in_(record_ids),
                OperationRecord.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, record_id: str, data: Dict[str, Any]) -> Optional[OperationRecord]:
        """更新操作记录"""
        stmt = select(OperationRecord).where(
            and_(
                OperationRecord.id == record_id,
                OperationRecord.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        operation_record = result.scalar_one_or_none()
        
        if operation_record:
            for key, value in data.items():
                setattr(operation_record, key, value)
            await self.db.commit()
            await self.db.refresh(operation_record)
        
        return operation_record

    async def soft_delete(self, record_id: str, updated_by: str) -> bool:
        """软删除操作记录"""
        stmt = select(OperationRecord).where(
            and_(
                OperationRecord.id == record_id,
                OperationRecord.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        operation_record = result.scalar_one_or_none()
        
        if operation_record:
            operation_record.is_deleted = True
            operation_record.updated_by = updated_by
            await self.db.commit()
            return True
        
        return False

    async def get_all(self, page: int = 1, size: int = 20,
                     user_id: str = None, username: str = None,
                     start_time: datetime = None, end_time: datetime = None) -> Tuple[List[OperationRecord], int]:
        """获取操作记录列表
        
        Args:
            page: 页码
            size: 每页数量
            user_id: 用户ID筛选
            username: 用户名筛选
            start_time: 开始时间筛选
            end_time: 结束时间筛选
            
        Returns:
            Tuple[List[OperationRecord], int]: 记录列表和总数
        """
        # 构建查询条件
        conditions = [OperationRecord.is_deleted == False]
        
        if user_id:
            conditions.append(OperationRecord.user_id == user_id)
        
        if username:
            conditions.append(OperationRecord.username.like(f"%{username}%"))
        
        if start_time:
            conditions.append(OperationRecord.operation_time >= start_time)
        
        if end_time:
            conditions.append(OperationRecord.operation_time <= end_time)

        # 查询总数
        count_stmt = select(OperationRecord).where(and_(*conditions))
        count_result = await self.db.execute(count_stmt)
        total = len(count_result.scalars().all())

        # 查询数据
        stmt = (
            select(OperationRecord)
            .where(and_(*conditions))
            .order_by(OperationRecord.operation_time.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        
        result = await self.db.execute(stmt)
        records = result.scalars().all()
        
        return list(records), total

    async def get_by_user_id(self, user_id: str) -> List[OperationRecord]:
        """根据用户ID获取操作记录"""
        stmt = (
            select(OperationRecord)
            .where(and_(
                OperationRecord.user_id == user_id,
                OperationRecord.is_deleted == False
            ))
            .order_by(OperationRecord.operation_time.desc())
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_time_range(self, start_time: datetime, end_time: datetime) -> List[OperationRecord]:
        """根据时间范围获取操作记录"""
        stmt = (
            select(OperationRecord)
            .where(and_(
                OperationRecord.operation_time >= start_time,
                OperationRecord.operation_time <= end_time,
                OperationRecord.is_deleted == False
            ))
            .order_by(OperationRecord.operation_time.desc())
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_stats(self) -> Dict[str, Any]:
        """获取操作记录统计信息"""
        # 总记录数
        total_stmt = select(OperationRecord).where(OperationRecord.is_deleted == False)
        total_result = await self.db.execute(total_stmt)
        total_count = len(total_result.scalars().all())

        # 今日记录数
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_stmt = select(OperationRecord).where(
            and_(
                OperationRecord.operation_time >= today,
                OperationRecord.is_deleted == False
            )
        )
        today_result = await self.db.execute(today_stmt)
        today_count = len(today_result.scalars().all())

        return {
            "total_count": total_count,
            "today_count": today_count
        }
