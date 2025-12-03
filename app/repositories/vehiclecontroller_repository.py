"""
车体控制器数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.vehiclecontroller import VehicleController
from ..core.exceptions import ResourceNotFoundError


class VehicleControllerRepository:
    """车体控制器数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> VehicleController:
        """创建车体控制器"""
        vehicle_controller = VehicleController(**data)
        self.db.add(vehicle_controller)
        await self.db.commit()
        await self.db.refresh(vehicle_controller)
        return vehicle_controller

    async def get_by_id(self, controller_id: str) -> Optional[VehicleController]:
        """根据ID获取车体控制器"""
        stmt = select(VehicleController).where(
            VehicleController.id == controller_id,
            VehicleController.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, page: int = 1, size: int = 20, 
                      vehicle_model: str = None) -> Tuple[List[VehicleController], int]:
        """获取车体控制器列表"""
        skip = (page - 1) * size
        conditions = [VehicleController.is_deleted == False]
        
        if vehicle_model:
            conditions.append(VehicleController.vehicle_model == vehicle_model)
        
        # 查询总数
        count_query = select(func.count(VehicleController.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(VehicleController)
                .where(and_(*conditions))
                .order_by(VehicleController.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        controllers = list(result.scalars().all())
        return controllers, total

    async def get_by_ids(self, controller_ids: List[str]) -> List[VehicleController]:
        """根据ID列表获取车体控制器"""
        stmt = select(VehicleController).where(
            VehicleController.id.in_(controller_ids),
            VehicleController.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_robot_id(self, robot_id: str) -> Optional[VehicleController]:
        """根据机器人ID获取车体控制器"""
        stmt = select(VehicleController).where(
            VehicleController.robot_id == robot_id,
            VehicleController.is_deleted == False
        )
        result = await self.db.execute(stmt)
        controller = result.scalar_one_or_none()
        # 调试日志
        if controller is None:
            # 检查是否有数据但被软删除了
            check_stmt = select(VehicleController).where(
                VehicleController.robot_id == robot_id
            )
            check_result = await self.db.execute(check_stmt)
            all_controllers = check_result.scalars().all()
            if all_controllers:
                from ...config.logging import get_logger
                logger = get_logger(__name__)
                logger.warning(f"找到机器人 {robot_id} 的车体控制器，但 is_deleted={[c.is_deleted for c in all_controllers]}")
        return controller

    async def update(self, controller_id: str, data: Dict[str, Any]) -> Optional[VehicleController]:
        """更新车体控制器"""
        stmt = select(VehicleController).where(
            VehicleController.id == controller_id,
            VehicleController.is_deleted == False
        )
        result = await self.db.execute(stmt)
        controller = result.scalar_one_or_none()
        
        if not controller:
            return None
        
        for key, value in data.items():
            if hasattr(controller, key):
                setattr(controller, key, value)
        
        await self.db.commit()
        await self.db.refresh(controller)
        return controller

    async def soft_delete(self, controller_id: str, updated_by: str) -> bool:
        """软删除车体控制器"""
        stmt = select(VehicleController).where(
            VehicleController.id == controller_id,
            VehicleController.is_deleted == False
        )
        result = await self.db.execute(stmt)
        controller = result.scalar_one_or_none()
        
        if not controller:
            return False
        
        controller.is_deleted = True
        controller.updated_by = updated_by
        await self.db.commit()
        return True


    async def get_stats(self) -> Dict[str, Any]:
        """获取车体控制器统计信息"""
        # 总数统计
        total_stmt = select(func.count(VehicleController.id)).where(VehicleController.is_deleted == False)
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar() or 0
        
        # 按车体模型统计
        model_stmt = select(
            VehicleController.vehicle_model,
            func.count(VehicleController.id).label('count')
        ).where(VehicleController.is_deleted == False).group_by(VehicleController.vehicle_model)
        model_result = await self.db.execute(model_stmt)
        model_stats = {row.vehicle_model: row.count for row in model_result}
        
        # 按版本统计
        version_stmt = select(
            VehicleController.controller_version,
            func.count(VehicleController.id).label('count')
        ).where(VehicleController.is_deleted == False).group_by(VehicleController.controller_version)
        version_result = await self.db.execute(version_stmt)
        version_stats = {row.controller_version: row.count for row in version_result}
        
        return {
            "total": total,
            "model_stats": model_stats,
            "version_stats": version_stats
        }

