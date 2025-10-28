"""
云台记录数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.gimbalhistory import GimbalHistory
from ..core.exceptions import ResourceNotFoundError


class GimbalHistoryRepository:
    """云台记录数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> GimbalHistory:
        """创建云台记录"""
        history = GimbalHistory(**data)
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history
    
    async def get_by_id(self, history_id: str) -> Optional[GimbalHistory]:
        """根据ID获取云台记录"""
        query = select(GimbalHistory).where(
            GimbalHistory.id == history_id,
            GimbalHistory.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, history_ids: List[str]) -> List[GimbalHistory]:
        """根据ID列表获取云台记录"""
        if not history_ids:
            return []
        
        query = select(GimbalHistory).where(
            GimbalHistory.id.in_(history_ids),
            GimbalHistory.is_deleted == False
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(self, page: int = 1, size: int = 20,
                     gimbaltask_id: str = None) -> Tuple[List[GimbalHistory], int]:
        """获取云台记录列表"""
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [GimbalHistory.is_deleted == False]
        
        if gimbaltask_id:
            conditions.append(GimbalHistory.gimbaltask_id == gimbaltask_id)
        
        # 查询总数
        count_query = select(func.count(GimbalHistory.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(GimbalHistory)
                .where(and_(*conditions))
                .order_by(GimbalHistory.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        histories = list(result.scalars().all())
        
        return histories, total
    
    async def update(self, history_id: str, data: Dict[str, Any]) -> Optional[GimbalHistory]:
        """更新云台记录"""
        history = await self.get_by_id(history_id)
        if not history:
            raise ResourceNotFoundError(f"云台记录ID '{history_id}' 不存在")
        
        for key, value in data.items():
            setattr(history, key, value)
        
        await self.db.commit()
        await self.db.refresh(history)
        return history
    
    async def soft_delete(self, history_id: str, deleted_by: str) -> bool:
        """软删除云台记录"""
        history = await self.get_by_id(history_id)
        if not history:
            return False
        
        history.is_deleted = True
        history.updated_by = deleted_by
        await self.db.commit()
        return True
    
    async def get_by_gimbaltask_id(self, gimbaltask_id: str) -> List[GimbalHistory]:
        """根据云台任务ID获取所有云台记录"""
        query = select(GimbalHistory).where(
            GimbalHistory.gimbaltask_id == gimbaltask_id,
            GimbalHistory.is_deleted == False
        ).order_by(GimbalHistory.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_all(self) -> int:
        """统计所有云台记录数量"""
        stmt = select(func.count(GimbalHistory.id)).where(GimbalHistory.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar() or 0
