"""
机械臂状态配置业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.robotarm_repository import RobotArmRepository
from ..schemas.robotarm import RobotArmCreate, RobotArmUpdate, RobotArmQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class RobotArmService:
    """机械臂状态配置业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RobotArmRepository(db)

    async def create_robot_arm(self, data: RobotArmCreate, user: dict) -> Dict[str, Any]:
        """创建机械臂状态配置"""
        try:
            # 准备创建数据
            create_data = {
                **data.dict(),
                "created_by": user["username"],
                "updated_by": user["username"]
            }

            # 创建机械臂状态配置
            robot_arm = await self.repo.create(create_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "create_robot_arm",
                f"创建机械臂状态配置: IP{robot_arm.robot_arm_ip}, 端口{robot_arm.robot_arm_port}",
                extra={"arm_id": robot_arm.id, "robot_arm_ip": robot_arm.robot_arm_ip, "robot_arm_port": robot_arm.robot_arm_port}
            )

            return ApiResponse.success(
                data=self._format_arm_response(robot_arm),
                message="机械臂状态配置创建成功"
            )

        except Exception as e:
            logger.error(f"创建机械臂状态配置失败: {e}", exc_info=True)
            raise BusinessError(f"创建机械臂状态配置失败: {str(e)}")

    async def get_robot_arm_by_id(self, arm_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取机械臂状态配置"""
        try:
            robot_arm = await self.repo.get_by_id(arm_id)
            if not robot_arm:
                raise ResourceNotFoundError(f"机械臂状态配置ID '{arm_id}' 不存在")

            return ApiResponse.success(
                data=self._format_arm_response(robot_arm),
                message="获取机械臂状态配置成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取机械臂状态配置失败: {e}", exc_info=True)
            raise BusinessError(f"获取机械臂状态配置失败: {str(e)}")

    async def get_robot_arms_by_ids(self, robotarm_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取机械臂状态配置"""
        try:
            robot_arms = await self.repo.get_by_ids(robotarm_ids)
            if not robot_arms:
                raise ResourceNotFoundError("未找到任何机械臂状态配置")

            return ApiResponse.success(
                data=[self._format_arm_response(arm) for arm in robot_arms],
                message=f"成功获取 {len(robot_arms)} 个机械臂状态配置"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"批量获取机械臂状态配置失败: {e}", exc_info=True)
            raise BusinessError(f"批量获取机械臂状态配置失败: {str(e)}")

    async def get_robot_arms(self, query: RobotArmQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取机械臂状态配置列表"""
        try:
            robot_arms, total = await self.repo.get_all(
                page=query.page,
                size=query.size,
                robot_arm_ip=query.robot_arm_ip,
                robot_arm_port=query.robot_arm_port,
                operating_speed=query.operating_speed,
                collision_detection_level=query.collision_detection_level
            )

            return ApiResponse.paginated(
                items=[self._format_arm_response(arm) for arm in robot_arms],
                total=total,
                page=query.page,
                size=query.size,
                message="获取机械臂状态配置列表成功"
            )

        except Exception as e:
            logger.error(f"获取机械臂状态配置列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取机械臂状态配置列表失败: {str(e)}")

    async def update_robot_arm(self, arm_id: str, data: RobotArmUpdate, user: dict) -> Dict[str, Any]:
        """更新机械臂状态配置"""
        try:
            # 检查机械臂状态配置是否存在
            existing_arm = await self.repo.get_by_id(arm_id)
            if not existing_arm:
                raise ResourceNotFoundError(f"机械臂状态配置ID '{arm_id}' 不存在")

            # 准备更新数据
            update_data = {k: v for k, v in data.dict().items() if v is not None}
            update_data["updated_by"] = user["username"]

            # 更新机械臂状态配置
            robot_arm = await self.repo.update(arm_id, update_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "update_robot_arm",
                f"更新机械臂状态配置: IP{robot_arm.robot_arm_ip}, 端口{robot_arm.robot_arm_port}",
                extra={"arm_id": robot_arm.id, "robot_arm_ip": robot_arm.robot_arm_ip, "robot_arm_port": robot_arm.robot_arm_port}
            )

            return ApiResponse.success(
                data=self._format_arm_response(robot_arm),
                message="机械臂状态配置更新成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"更新机械臂状态配置失败: {e}", exc_info=True)
            raise BusinessError(f"更新机械臂状态配置失败: {str(e)}")

    async def delete_robot_arm(self, arm_id: str, user: dict) -> Dict[str, Any]:
        """删除机械臂状态配置"""
        try:
            # 检查机械臂状态配置是否存在
            existing_arm = await self.repo.get_by_id(arm_id)
            if not existing_arm:
                raise ResourceNotFoundError(f"机械臂状态配置ID '{arm_id}' 不存在")

            # 软删除机械臂状态配置
            success = await self.repo.soft_delete(arm_id, user["username"])
            if not success:
                raise BusinessError(f"删除机械臂状态配置失败: 软删除操作返回失败")
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "delete_robot_arm",
                f"删除机械臂状态配置: IP{existing_arm.robot_arm_ip}, 端口{existing_arm.robot_arm_port}",
                extra={"arm_id": arm_id, "robot_arm_ip": existing_arm.robot_arm_ip, "robot_arm_port": existing_arm.robot_arm_port}
            )

            return ApiResponse.success(
                data={"id": arm_id},
                message="机械臂状态配置删除成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"删除机械臂状态配置失败: {e}", exc_info=True)
            raise BusinessError(f"删除机械臂状态配置失败: {str(e)}")

    async def get_robot_arm_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取机械臂状态配置统计信息"""
        try:
            stats = await self.repo.get_stats()
            return ApiResponse.success(
                data=stats,
                message="获取机械臂状态配置统计信息成功"
            )

        except Exception as e:
            logger.error(f"获取机械臂状态配置统计信息失败: {e}", exc_info=True)
            raise BusinessError(f"获取机械臂状态配置统计信息失败: {str(e)}")

    def _format_arm_response(self, robot_arm) -> Dict[str, Any]:
        """格式化机械臂状态配置响应数据"""
        return {
            "id": robot_arm.id,
            "robot_arm_ip": robot_arm.robot_arm_ip,
            "subnet_mask": robot_arm.subnet_mask,
            "gateway": robot_arm.gateway,
            "robot_arm_port": robot_arm.robot_arm_port,
            "operating_speed": robot_arm.operating_speed,
            "origin_coordinates": robot_arm.origin_coordinates,
            "plane_coordinates": robot_arm.plane_coordinates,
            "load_size": float(robot_arm.load_size) if robot_arm.load_size else 0.0,
            "end_coordinates": robot_arm.end_coordinates,
            "tool_io": robot_arm.tool_io,
            "collision_detection_level": robot_arm.collision_detection_level,
            "created_at": robot_arm.created_at.strftime("%Y-%m-%dT%H:%M:%S") if robot_arm.created_at else None,
            "updated_at": robot_arm.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if robot_arm.updated_at else None,
            "created_by": robot_arm.created_by,
            "updated_by": robot_arm.updated_by,
        }
