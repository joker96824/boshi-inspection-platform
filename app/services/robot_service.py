"""
机器人业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.robot_repository import RobotRepository
from ..repositories.robotmap_repository import RobotMapRepository
from ..schemas.robot import RobotCreate, RobotUpdate, RobotResponse, RobotListResponse
from ..core.exceptions import ResourceNotFoundError, PermissionDeniedError
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class RobotService:
    """机器人业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.robot_repo = RobotRepository(db)
        self.robotmap_repo = RobotMapRepository(db)
    
    def _format_robot_response(self, robot) -> Dict[str, Any]:
        """格式化机器人响应数据"""
        # 获取关联的地图列表
        maps = []
        if hasattr(robot, 'maps') and robot.maps:
            maps = [
                {
                    "id": rm.map.id if rm.map else None,
                    "map_name": rm.map.map_name if rm.map else None,
                }
                for rm in robot.maps
                if not rm.is_deleted and rm.map and not rm.map.is_deleted
            ]
        
        return {
            "id": robot.id,
            "robot_name": robot.robot_name,
            "robot_info": robot.robot_info,
            "factory_id": robot.factory_id,
            "maps": maps,
            "created_at": robot.created_at.strftime("%Y-%m-%dT%H:%M:%S") if robot.created_at else None,
            "updated_at": robot.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if robot.updated_at else None,
            "created_by": robot.created_by,
            "updated_by": robot.updated_by,
        }
    
    async def create_robot(self, robot_data: RobotCreate, user: dict) -> Dict[str, Any]:
        """创建机器人"""
        try:
            create_data = {
                "robot_name": robot_data.robot_name,
                "robot_info": robot_data.robot_info,
                "factory_id": robot_data.factory_id,
                "created_by": user["username"],
                "updated_by": user["username"]
            }
            
            robot = await self.robot_repo.create(create_data)
            
            # 创建机器人-地图关联
            if robot_data.map_ids:
                for map_id in robot_data.map_ids:
                    await self.robotmap_repo.create({
                        "robot_id": robot.id,
                        "map_id": map_id,
                        "created_by": user["username"],
                        "updated_by": user["username"]
                    })
            
            # 重新加载机器人以获取关联数据
            robot = await self.robot_repo.get_by_id(robot.id)
            
            # 记录操作日志
            log_user_action(
                user["username"],
                "create_robot",
                "success",
                f"创建机器人成功，ID: {robot.id}"
            )
            
            return ApiResponse.success(
                data=self._format_robot_response(robot),
                message="创建机器人成功"
            )
            
        except Exception as e:
            logger.error(f"创建机器人失败: {e}")
            log_user_action(
                user["username"],
                "create_robot",
                "failed",
                f"创建机器人失败: {str(e)}"
            )
            raise HTTPException(status_code=500, detail="创建机器人失败")
    
    async def get_robot_by_id(self, robot_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取机器人"""
        robot = await self.robot_repo.get_by_id(robot_id)
        if not robot:
            raise ResourceNotFoundError(f"机器人 '{robot_id}' 不存在")
        
        return ApiResponse.success(
            data=self._format_robot_response(robot),
            message="获取机器人成功"
        )
    
    async def get_robots_by_ids(self, robot_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取机器人"""
        try:
            robots = await self.robot_repo.get_by_ids(robot_ids)
            
            items_data = [self._format_robot_response(robot) for robot in robots]
            
            return ApiResponse.success(
                data={"items": items_data, "total": len(items_data)},
                message="获取机器人列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取机器人列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取机器人列表失败")
    
    async def get_user_robots(self, user: Optional[dict], page: int = 1, size: int = 20, robot_name: str = None, factory_id: str = None, map_id: str = None) -> Dict[str, Any]:
        """获取所有机器人列表"""
        try:
            robots, total = await self.robot_repo.get_all(page, size, robot_name, factory_id, map_id)
            
            # 格式化响应数据
            items = [self._format_robot_response(robot) for robot in robots]
            
            return ApiResponse.paginated(
                items=items,
                total=total,
                page=page,
                size=size,
                message="获取机器人列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取机器人列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取机器人列表失败")
    
    async def update_robot(self, robot_id: str, robot_data: RobotUpdate, user: dict) -> Dict[str, Any]:
        """更新机器人"""
        # 检查机器人是否存在
        robot = await self.robot_repo.get_by_id(robot_id)
        if not robot:
            raise ResourceNotFoundError(f"机器人 '{robot_id}' 不存在")
        
        
        try:
            # 准备更新数据
            update_data = {}
            if robot_data.robot_name is not None:
                update_data["robot_name"] = robot_data.robot_name
            if robot_data.robot_info is not None:
                update_data["robot_info"] = robot_data.robot_info
            if robot_data.factory_id is not None:
                update_data["factory_id"] = robot_data.factory_id
            update_data["updated_by"] = user["username"]
            
            # 更新机器人
            updated_robot = await self.robot_repo.update(robot_id, update_data)
            
            # 更新机器人-地图关联
            if robot_data.map_ids is not None:
                # 删除现有关联
                await self.robotmap_repo.delete_by_robot_id(robot_id)
                # 创建新关联
                for map_id in robot_data.map_ids:
                    await self.robotmap_repo.create({
                        "robot_id": robot_id,
                        "map_id": map_id,
                        "created_by": user["username"],
                        "updated_by": user["username"]
                    })
            
            # 重新加载机器人以获取关联数据
            updated_robot = await self.robot_repo.get_by_id(robot_id)
            
            # 记录操作日志
            log_user_action(
                user["username"],
                "update_robot",
                "success",
                f"更新机器人成功，ID: {robot_id}"
            )
            
            return ApiResponse.success(
                data=self._format_robot_response(updated_robot),
                message="更新机器人成功"
            )
            
        except Exception as e:
            logger.error(f"更新机器人失败: {e}")
            log_user_action(
                user["username"],
                "update_robot",
                "failed",
                f"更新机器人失败: {str(e)}"
            )
            raise HTTPException(status_code=500, detail="更新机器人失败")
    
    async def delete_robot(self, robot_id: str, user: dict) -> Dict[str, Any]:
        """删除机器人"""
        # 检查机器人是否存在
        robot = await self.robot_repo.get_by_id(robot_id)
        if not robot:
            raise ResourceNotFoundError(f"机器人 '{robot_id}' 不存在")
        
        
        try:
            # 软删除机器人
            success = await self.robot_repo.soft_delete(robot_id)
            if not success:
                raise HTTPException(status_code=500, detail="删除机器人失败")
            
            # 记录操作日志
            log_user_action(
                user["username"],
                "delete_robot",
                "success",
                f"删除机器人成功，ID: {robot_id}"
            )
            
            return ApiResponse.success(
                data={"id": robot_id},
                message="删除机器人成功"
            )
            
        except Exception as e:
            logger.error(f"删除机器人失败: {e}")
            log_user_action(
                user["username"],
                "delete_robot",
                "failed",
                f"删除机器人失败: {str(e)}"
            )
            raise HTTPException(status_code=500, detail="删除机器人失败")
    
    async def get_robot_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取机器人统计信息"""
        try:
            total_count = await self.robot_repo.count_all()
            
            stats = {
                "total_robots": total_count
            }
            
            return ApiResponse.success(
                data=stats,
                message="获取机器人统计成功"
            )
            
        except Exception as e:
            logger.error(f"获取机器人统计失败: {e}")
            raise HTTPException(status_code=500, detail="获取机器人统计失败")
