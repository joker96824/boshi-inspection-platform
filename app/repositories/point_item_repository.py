"""
巡检中间表数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
import uuid

from ..models.point_item import PointItem
from ..models.point import Point
from ..models.item import Item
from ..core.exceptions import ResourceNotFoundError


class PointItemRepository:
    """巡检中间表数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> PointItem:
        """创建巡检中间表记录"""
        point_item = PointItem(**data)
        self.db.add(point_item)
        await self.db.commit()
        await self.db.refresh(point_item)
        return point_item
    
    async def get_by_id(self, point_item_id: str) -> Optional[PointItem]:
        """根据ID获取巡检中间表记录"""
        query = select(PointItem).where(PointItem.id == point_item_id, PointItem.is_deleted == False)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_point_ids(self, point_ids: List[str]) -> List[PointItem]:
        """根据巡检点ID列表获取记录"""
        if not point_ids:
            return []
        
        query = (select(PointItem)
                .where(PointItem.point_id.in_(point_ids), PointItem.is_deleted == False)
                .order_by(PointItem.point_id, PointItem.created_at))
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_item_ids(self, item_ids: List[str]) -> List[PointItem]:
        """根据巡检项目ID列表获取记录"""
        if not item_ids:
            return []
        
        query = (select(PointItem)
                .where(PointItem.item_id.in_(item_ids), PointItem.is_deleted == False)
                .order_by(PointItem.item_id, PointItem.created_at))
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(self, page: int = 1, size: int = 20, 
                     point_ids: List[str] = None, item_ids: List[str] = None) -> Tuple[List[PointItem], int]:
        """获取巡检中间表记录列表"""
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [PointItem.is_deleted == False]
        
        if point_ids:
            conditions.append(PointItem.point_id.in_(point_ids))
        
        if item_ids:
            conditions.append(PointItem.item_id.in_(item_ids))
        
        # 查询总数
        count_query = select(func.count(PointItem.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(PointItem)
                .where(and_(*conditions))
                .order_by(PointItem.point_id, PointItem.created_at)
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        point_items = list(result.scalars().all())
        
        return point_items, total
    
    async def get_with_item_details(self, page: int = 1, size: int = 20, 
                                   point_ids: List[str] = None) -> Tuple[List[Dict[str, Any]], int]:
        """通过巡检点查询，返回带巡检项目详情的记录列表"""
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [PointItem.is_deleted == False]
        
        if point_ids:
            conditions.append(PointItem.point_id.in_(point_ids))
        
        # 查询总数
        count_query = select(func.count(PointItem.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据（带巡检项目详情）
        query = (select(PointItem, Point, Item)
                .join(Point, PointItem.point_id == Point.id)
                .join(Item, PointItem.item_id == Item.id)
                .where(and_(*conditions))
                .order_by(PointItem.point_id, PointItem.created_at)
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        rows = result.all()
        
        # 格式化结果
        point_items_with_details = []
        for point_item, point, item in rows:
            point_items_with_details.append({
                "id": point_item.id,
                "point_id": point_item.point_id,
                "item_id": point_item.item_id,
                "point_name": point.point_name,
                "item_name": item.item_name,
                "item_info": item.item_info,
                "created_at": point_item.created_at,
                "updated_at": point_item.updated_at,
                "created_by": point_item.created_by,
                "updated_by": point_item.updated_by,
            })
        
        return point_items_with_details, total
    
    async def get_with_point_details(self, page: int = 1, size: int = 20, 
                                    item_ids: List[str] = None) -> Tuple[List[Dict[str, Any]], int]:
        """通过巡检项目查询，返回带巡检点详情的记录列表"""
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [PointItem.is_deleted == False]
        
        if item_ids:
            conditions.append(PointItem.item_id.in_(item_ids))
        
        # 查询总数
        count_query = select(func.count(PointItem.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据（带巡检点详情）
        query = (select(PointItem, Point, Item)
                .join(Point, PointItem.point_id == Point.id)
                .join(Item, PointItem.item_id == Item.id)
                .where(and_(*conditions))
                .order_by(PointItem.item_id, PointItem.created_at)
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        rows = result.all()
        
        # 格式化结果
        point_items_with_details = []
        for point_item, point, item in rows:
            point_items_with_details.append({
                "id": point_item.id,
                "point_id": point_item.point_id,
                "item_id": point_item.item_id,
                "point_name": point.point_name,
                "point_actions": point.point_actions,
                "item_name": item.item_name,
                "created_at": point_item.created_at,
                "updated_at": point_item.updated_at,
                "created_by": point_item.created_by,
                "updated_by": point_item.updated_by,
            })
        
        return point_items_with_details, total
    
    async def update(self, point_item_id: str, data: Dict[str, Any]) -> Optional[PointItem]:
        """更新巡检中间表记录"""
        point_item = await self.get_by_id(point_item_id)
        if not point_item:
            raise ResourceNotFoundError(f"巡检中间表记录ID '{point_item_id}' 不存在")
        
        for key, value in data.items():
            setattr(point_item, key, value)
        
        await self.db.commit()
        await self.db.refresh(point_item)
        return point_item
    
    async def delete(self, point_item_id: str) -> bool:
        """真删除巡检中间表记录"""
        point_item = await self.get_by_id(point_item_id)
        if not point_item:
            raise ResourceNotFoundError(f"巡检中间表记录ID '{point_item_id}' 不存在")
        
        await self.db.delete(point_item)
        await self.db.commit()
        return True

    async def delete_by_item_id(self, item_id: str) -> int:
        """根据巡检项目ID删除所有关联记录（真删除）"""
        stmt = select(PointItem).where(PointItem.item_id == item_id, PointItem.is_deleted == False)
        result = await self.db.execute(stmt)
        point_items = result.scalars().all()
        
        deleted_count = 0
        for point_item in point_items:
            await self.db.delete(point_item)
            deleted_count += 1
        
        await self.db.commit()
        return deleted_count

    async def delete_by_point_id(self, point_id: str) -> int:
        """根据巡检点ID删除所有关联记录（真删除）"""
        stmt = select(PointItem).where(PointItem.point_id == point_id, PointItem.is_deleted == False)
        result = await self.db.execute(stmt)
        point_items = result.scalars().all()
        
        deleted_count = 0
        for point_item in point_items:
            await self.db.delete(point_item)
            deleted_count += 1
        
        await self.db.commit()
        return deleted_count

    async def batch_create_by_item(self, item_id: str, point_ids: List[str], user: dict) -> List[PointItem]:
        """为巡检项目批量创建关联记录"""
        point_items = []
        for point_id in point_ids:
            point_item = PointItem(
                id=str(uuid.uuid4()),
                point_id=point_id,
                item_id=item_id,
                created_by=user["username"],
                updated_by=user["username"]
            )
            point_items.append(point_item)
            self.db.add(point_item)
        
        await self.db.commit()
        return point_items

    async def batch_create_by_point(self, point_id: str, item_ids: List[str], user: dict) -> List[PointItem]:
        """为巡检点批量创建关联记录"""
        point_items = []
        for item_id in item_ids:
            point_item = PointItem(
                id=str(uuid.uuid4()),
                point_id=point_id,
                item_id=item_id,
                created_by=user["username"],
                updated_by=user["username"]
            )
            point_items.append(point_item)
            self.db.add(point_item)
        
        await self.db.commit()
        return point_items
    
    async def exists_by_point_item(self, point_id: str, item_id: str, exclude_id: str = None) -> bool:
        """检查巡检点和巡检项目的关联是否已存在"""
        conditions = [
            PointItem.point_id == point_id,
            PointItem.item_id == item_id,
            PointItem.is_deleted == False
        ]
        if exclude_id:
            conditions.append(PointItem.id != exclude_id)
        
        query = select(PointItem).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def count_by_point(self, point_id: str) -> int:
        """统计巡检点的项目数量"""
        stmt = select(func.count(PointItem.id)).where(
            PointItem.point_id == point_id,
            PointItem.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def count_by_item(self, item_id: str) -> int:
        """统计巡检项目的使用次数"""
        stmt = select(func.count(PointItem.id)).where(
            PointItem.item_id == item_id,
            PointItem.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
