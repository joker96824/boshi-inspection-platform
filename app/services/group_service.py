"""
分组业务逻辑服务
"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.group_repository import GroupRepository
from ..schemas.group import GroupCreate, GroupUpdate
from ..core.exceptions import (
    BusinessError,
    ResourceNotFoundError,
)
from ..utils.response import ApiResponse


class GroupService:
    """分组业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = GroupRepository(db)
    
    async def create_group(self, data: GroupCreate, user: dict) -> Dict[str, Any]:
        """创建分组"""
        # 检查名称是否已存在
        if await self.repo.exists_by_name(data.group_name):
            raise BusinessError(f"分组名称 '{data.group_name}' 已存在")
        
        # 创建数据
        create_data = {
            **data.dict(),
            "created_by": user.get("username"),
            "updated_by": user.get("username"),
        }
        
        group = await self.repo.create(create_data)
        return ApiResponse.success(
            data=self._format_group_response(group),
            message="分组创建成功"
        )
    
    async def get_groups(
        self,
        page: Optional[int] = None,
        size: Optional[int] = None,
        group_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """获取分组列表"""
        items, total = await self.repo.get_all(
            page=page,
            size=size,
            group_name=group_name,
        )
        
        formatted_items = [self._format_group_response(item) for item in items]
        
        if page is not None and size is not None:
            return ApiResponse.paginated(
                items=formatted_items,
                total=total,
                page=page,
                size=size
            )
        else:
            return ApiResponse.success(data=formatted_items, message="获取成功")
    
    async def get_group_by_id(self, group_id: str) -> Dict[str, Any]:
        """根据ID获取分组"""
        group = await self.repo.get_by_id(group_id)
        if not group:
            raise ResourceNotFoundError(f"分组 '{group_id}' 不存在")
        
        return ApiResponse.success(
            data=self._format_group_response(group),
            message="获取成功"
        )
    
    async def update_group(
        self,
        group_id: str,
        data: GroupUpdate,
        user: dict
    ) -> Dict[str, Any]:
        """更新分组"""
        group = await self.repo.get_by_id(group_id)
        if not group:
            raise ResourceNotFoundError(f"分组 '{group_id}' 不存在")
        
        update_data = data.dict(exclude_unset=True)
        
        # 检查名称是否已存在（排除自己）
        if "group_name" in update_data:
            if await self.repo.exists_by_name(update_data["group_name"], exclude_id=group_id):
                raise BusinessError(f"分组名称 '{update_data['group_name']}' 已存在")
        
        update_data["updated_by"] = user.get("username")
        updated = await self.repo.update(group_id, update_data)
        
        if not updated:
            raise ResourceNotFoundError(f"分组 '{group_id}' 不存在")
        
        return ApiResponse.success(
            data=self._format_group_response(updated),
            message="分组更新成功"
        )
    
    async def delete_group(self, group_id: str, user: dict) -> Dict[str, Any]:
        """删除分组"""
        group = await self.repo.get_by_id(group_id)
        if not group:
            raise ResourceNotFoundError(f"分组 '{group_id}' 不存在")
        
        # 删除分组前，先更新所有关联的机器人/云台/智能传感器的 group_id 为 NULL
        from ..repositories.robot_repository import RobotRepository
        from ..repositories.gimbal_repository import GimbalRepository
        from ..repositories.sensor_repository import SensorRepository
        
        robot_repo = RobotRepository(self.db)
        gimbal_repo = GimbalRepository(self.db)
        sensor_repo = SensorRepository(self.db)
        
        # 查询所有关联的实体
        from sqlalchemy import select
        from ..models.robot import Robot
        from ..models.gimbal import Gimbal
        from ..models.sensor import Sensor
        
        # 查询关联的机器人
        robot_query = select(Robot.id).where(
            Robot.group_id == group_id,
            Robot.is_deleted == False
        )
        robot_result = await self.db.execute(robot_query)
        robot_ids = [row[0] for row in robot_result.all()]
        
        # 查询关联的云台
        gimbal_query = select(Gimbal.id).where(
            Gimbal.group_id == group_id,
            Gimbal.is_deleted == False
        )
        gimbal_result = await self.db.execute(gimbal_query)
        gimbal_ids = [row[0] for row in gimbal_result.all()]
        
        # 查询关联的智能传感器
        sensor_query = select(Sensor.id).where(
            Sensor.group_id == group_id,
            Sensor.is_deleted == False
        )
        sensor_result = await self.db.execute(sensor_query)
        sensor_ids = [row[0] for row in sensor_result.all()]
        
        # 批量更新 group_id 为 NULL
        username = user.get("username", "system")
        if robot_ids:
            await robot_repo.batch_update_group(robot_ids, None, username)
        if gimbal_ids:
            await gimbal_repo.batch_update_group(gimbal_ids, None, username)
        if sensor_ids:
            await sensor_repo.batch_update_group(sensor_ids, None, username)
        
        # 删除分组
        success = await self.repo.delete(group_id, user)
        if not success:
            raise ResourceNotFoundError(f"分组 '{group_id}' 不存在")
        
        return ApiResponse.success(message="分组删除成功")
    
    def _format_group_response(self, group) -> Dict[str, Any]:
        """格式化分组响应数据"""
        return {
            "id": group.id,
            "group_name": group.group_name,
            "group_description": group.group_description,
            "created_at": group.created_at.strftime("%Y-%m-%dT%H:%M:%S") if group.created_at else None,
            "updated_at": group.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if group.updated_at else None,
            "created_by": group.created_by,
            "updated_by": group.updated_by,
        }

