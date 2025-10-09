"""
机器人业务逻辑服务
"""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.robot_repository import RobotRepository
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
    
    def _format_robot_response(self, robot) -> Dict[str, Any]:
        """格式化机器人响应数据"""
        return {
            "id": robot.id,
            "user_id": robot.user_id,
            "robot_name": robot.robot_name,
            "robot_info": robot.robot_info,
            "created_at": robot.created_at.strftime("%Y-%m-%dT%H:%M:%S") if robot.created_at else None,
            "updated_at": robot.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if robot.updated_at else None,
            "created_by": robot.created_by,
            "updated_by": robot.updated_by,
        }
    
    async def create_robot(self, robot_data: RobotCreate, user: dict) -> Dict[str, Any]:
        """创建机器人"""
        try:
            create_data = {
                "user_id": user["id"],
                "robot_name": robot_data.robot_name,
                "robot_info": robot_data.robot_info,
                "created_by": user["username"],
                "updated_by": user["username"]
            }
            
            robot = await self.robot_repo.create(create_data)
            
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
    
    async def get_robot_by_id(self, robot_id: str, user: dict) -> Dict[str, Any]:
        """根据ID获取机器人"""
        robot = await self.robot_repo.get_by_id(robot_id)
        if not robot:
            raise ResourceNotFoundError(f"机器人 '{robot_id}' 不存在")
        
        return ApiResponse.success(
            data=self._format_robot_response(robot),
            message="获取机器人成功"
        )
    
    async def get_user_robots(self, user: dict, page: int = 1, size: int = 20, robot_name: str = None) -> Dict[str, Any]:
        """获取所有机器人列表"""
        try:
            robots, total = await self.robot_repo.get_all(page, size, robot_name)
            
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
            update_data["updated_by"] = user["username"]
            
            # 更新机器人
            updated_robot = await self.robot_repo.update(robot_id, update_data)
            
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
            
            return ApiResponse.success(message="删除机器人成功")
            
        except Exception as e:
            logger.error(f"删除机器人失败: {e}")
            log_user_action(
                user["username"],
                "delete_robot",
                "failed",
                f"删除机器人失败: {str(e)}"
            )
            raise HTTPException(status_code=500, detail="删除机器人失败")
    
    async def get_robot_stats(self, user: dict) -> Dict[str, Any]:
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
