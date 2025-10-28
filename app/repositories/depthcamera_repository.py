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
                      camera_type: str = None, protocol: str = None, 
                      frame_rate: int = None, camera_ip: str = None) -> Tuple[List[DepthCamera], int]:
        """获取深度相机配置列表"""
        skip = (page - 1) * size
        conditions = [DepthCamera.is_deleted == False]
        
        if camera_type is not None:
            conditions.append(DepthCamera.camera_type == camera_type)
        if protocol is not None:
            conditions.append(DepthCamera.protocol == protocol)
        if frame_rate is not None:
            conditions.append(DepthCamera.frame_rate == frame_rate)
        if camera_ip is not None:
            conditions.append(DepthCamera.camera_ip.like(f"%{camera_ip}%"))
        
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

    async def get_stats(self) -> Dict[str, Any]:
        """获取深度相机配置统计信息"""
        # 总数统计
        total_stmt = select(func.count(DepthCamera.id)).where(DepthCamera.is_deleted == False)
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar() or 0
        
        # 按相机类型统计
        type_stmt = select(
            DepthCamera.camera_type,
            func.count(DepthCamera.id).label('count')
        ).where(DepthCamera.is_deleted == False).group_by(DepthCamera.camera_type)
        type_result = await self.db.execute(type_stmt)
        type_stats = {row.camera_type: row.count for row in type_result}
        
        # 按连接协议统计
        protocol_stmt = select(
            DepthCamera.protocol,
            func.count(DepthCamera.id).label('count')
        ).where(DepthCamera.is_deleted == False).group_by(DepthCamera.protocol)
        protocol_result = await self.db.execute(protocol_stmt)
        protocol_stats = {row.protocol: row.count for row in protocol_result}
        
        # 按帧率统计
        frame_rate_stmt = select(
            DepthCamera.frame_rate,
            func.count(DepthCamera.id).label('count')
        ).where(DepthCamera.is_deleted == False).group_by(DepthCamera.frame_rate)
        frame_rate_result = await self.db.execute(frame_rate_stmt)
        frame_rate_stats = {row.frame_rate: row.count for row in frame_rate_result}
        
        # 深度范围统计
        depth_stats_stmt = select(
            func.avg(DepthCamera.depth_range_min).label('avg_min_depth'),
            func.min(DepthCamera.depth_range_min).label('min_min_depth'),
            func.max(DepthCamera.depth_range_min).label('max_min_depth'),
            func.avg(DepthCamera.depth_range_max).label('avg_max_depth'),
            func.min(DepthCamera.depth_range_max).label('min_max_depth'),
            func.max(DepthCamera.depth_range_max).label('max_max_depth'),
            func.avg(DepthCamera.depth_accuracy).label('avg_accuracy'),
            func.min(DepthCamera.depth_accuracy).label('min_accuracy'),
            func.max(DepthCamera.depth_accuracy).label('max_accuracy')
        ).where(DepthCamera.is_deleted == False)
        depth_result = await self.db.execute(depth_stats_stmt)
        depth_stats = depth_result.first()
        
        return {
            "total": total,
            "type_stats": type_stats,
            "protocol_stats": protocol_stats,
            "frame_rate_stats": frame_rate_stats,
            "depth_stats": {
                "avg_min_depth": float(depth_stats.avg_min_depth) if depth_stats.avg_min_depth else 0,
                "min_min_depth": float(depth_stats.min_min_depth) if depth_stats.min_min_depth else 0,
                "max_min_depth": float(depth_stats.max_min_depth) if depth_stats.max_min_depth else 0,
                "avg_max_depth": float(depth_stats.avg_max_depth) if depth_stats.avg_max_depth else 0,
                "min_max_depth": float(depth_stats.min_max_depth) if depth_stats.min_max_depth else 0,
                "max_max_depth": float(depth_stats.max_max_depth) if depth_stats.max_max_depth else 0,
                "avg_accuracy": float(depth_stats.avg_accuracy) if depth_stats.avg_accuracy else 0,
                "min_accuracy": float(depth_stats.min_accuracy) if depth_stats.min_accuracy else 0,
                "max_accuracy": float(depth_stats.max_accuracy) if depth_stats.max_accuracy else 0
            }
        }

