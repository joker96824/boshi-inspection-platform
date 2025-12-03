"""
深度相机配置数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.depthcamera import DepthCamera
from ..core.exceptions import ResourceNotFoundError


class DepthCameraRepository:
    """深度相机配置数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> DepthCamera:
        """创建深度相机配置"""
        depth_camera = DepthCamera(**data)
        self.db.add(depth_camera)
        await self.db.commit()
        await self.db.refresh(depth_camera)
        return depth_camera

    async def get_by_id(self, camera_id: str) -> Optional[DepthCamera]:
        """根据ID获取深度相机配置"""
        stmt = select(DepthCamera).where(
            DepthCamera.id == camera_id,
            DepthCamera.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, page: int = 1, size: int = 20, 
                      serial_port_id: int = None, camera_mode: str = None) -> Tuple[List[DepthCamera], int]:
        """获取深度相机配置列表"""
        skip = (page - 1) * size
        conditions = [DepthCamera.is_deleted == False]
        
        if serial_port_id is not None:
            conditions.append(DepthCamera.serial_port_id == serial_port_id)
        if camera_mode is not None:
            conditions.append(DepthCamera.camera_mode == camera_mode)
        
        # 查询总数
        count_query = select(func.count(DepthCamera.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(DepthCamera)
                .where(and_(*conditions))
                .order_by(DepthCamera.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        depth_cameras = list(result.scalars().all())
        return depth_cameras, total

    async def get_by_ids(self, camera_ids: List[str]) -> List[DepthCamera]:
        """根据ID列表获取深度相机配置"""
        stmt = select(DepthCamera).where(
            DepthCamera.id.in_(camera_ids),
            DepthCamera.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_robot_id(self, robot_id: str) -> Optional[DepthCamera]:
        """根据机器人ID获取深度相机配置（单个，兼容旧接口）"""
        stmt = select(DepthCamera).where(
            DepthCamera.robot_id == robot_id,
            DepthCamera.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_by_robot_id(self, robot_id: str) -> List[DepthCamera]:
        """根据机器人ID获取所有深度相机配置（列表）"""
        stmt = select(DepthCamera).where(
            DepthCamera.robot_id == robot_id,
            DepthCamera.is_deleted == False
        ).order_by(DepthCamera.created_at.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, camera_id: str, data: Dict[str, Any]) -> Optional[DepthCamera]:
        """更新深度相机配置"""
        stmt = select(DepthCamera).where(
            DepthCamera.id == camera_id,
            DepthCamera.is_deleted == False
        )
        result = await self.db.execute(stmt)
        depth_camera = result.scalar_one_or_none()
        
        if not depth_camera:
            return None
        
        for key, value in data.items():
            if hasattr(depth_camera, key):
                setattr(depth_camera, key, value)
        
        await self.db.commit()
        await self.db.refresh(depth_camera)
        return depth_camera

    async def soft_delete(self, camera_id: str, updated_by: str) -> bool:
        """软删除深度相机配置"""
        stmt = select(DepthCamera).where(
            DepthCamera.id == camera_id,
            DepthCamera.is_deleted == False
        )
        result = await self.db.execute(stmt)
        depth_camera = result.scalar_one_or_none()
        
        if not depth_camera:
            return False
        
        depth_camera.is_deleted = True
        depth_camera.updated_by = updated_by
        await self.db.commit()
        return True
    
    async def hard_delete_by_robot_id(self, robot_id: str) -> int:
        """真删除指定机器人的所有深度相机配置（返回删除数量）"""
        from sqlalchemy import delete
        stmt = delete(DepthCamera).where(
            DepthCamera.robot_id == robot_id
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def get_stats(self) -> Dict[str, Any]:
        """获取深度相机配置统计信息"""
        # 总数统计
        total_stmt = select(func.count(DepthCamera.id)).where(DepthCamera.is_deleted == False)
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar() or 0
        
        # 按串口ID统计
        serial_port_stmt = select(
            DepthCamera.serial_port_id,
            func.count(DepthCamera.id).label('count')
        ).where(DepthCamera.is_deleted == False).group_by(DepthCamera.serial_port_id)
        serial_port_result = await self.db.execute(serial_port_stmt)
        serial_port_stats = {row.serial_port_id: row.count for row in serial_port_result}
        
        # 按图像翻转统计
        image_flip_stmt = select(
            DepthCamera.image_flip,
            func.count(DepthCamera.id).label('count')
        ).where(DepthCamera.is_deleted == False).group_by(DepthCamera.image_flip)
        image_flip_result = await self.db.execute(image_flip_stmt)
        image_flip_stats = {row.image_flip: row.count for row in image_flip_result if row.image_flip}
        
        return {
            "total": total,
            "serial_port_stats": serial_port_stats,
            "image_flip_stats": image_flip_stats
        }

