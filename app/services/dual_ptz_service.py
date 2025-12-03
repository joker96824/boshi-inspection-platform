"""
双光云台配置业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.dualptz_repository import DualPTZRepository
from ..schemas.dualptz import DualPTZCreate, DualPTZUpdate, DualPTZQuery, DualPTZBatchUpdate
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class DualPTZService:
    """双光云台配置业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DualPTZRepository(db)

    async def create_ptz_config(self, data: DualPTZCreate, user: dict) -> Dict[str, Any]:
        """创建双光云台配置"""
        try:
            # 准备创建数据
            create_data = {
                **data.dict(),
                "created_by": user["username"],
                "updated_by": user["username"]
            }

            # 创建双光云台配置
            ptz_config = await self.repo.create(create_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "create_dual_ptz_config",
                f"创建双光云台配置: IP{ptz_config.ptz_ip}, 速度{ptz_config.operating_speed}",
                extra={"ptz_id": ptz_config.id, "ptz_ip": ptz_config.ptz_ip, "operating_speed": ptz_config.operating_speed}
            )

            return ApiResponse.success(
                data=self._format_ptz_response(ptz_config),
                message="双光云台配置创建成功"
            )

        except Exception as e:
            logger.error(f"创建双光云台配置失败: {e}", exc_info=True)
            raise BusinessError(f"创建双光云台配置失败: {str(e)}")

    async def get_ptz_config_by_id(self, ptz_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取双光云台配置"""
        try:
            ptz_config = await self.repo.get_by_id(ptz_id)
            if not ptz_config:
                raise ResourceNotFoundError(f"双光云台配置ID '{ptz_id}' 不存在")

            return ApiResponse.success(
                data=self._format_ptz_response(ptz_config),
                message="获取双光云台配置成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取双光云台配置失败: {e}", exc_info=True)
            raise BusinessError(f"获取双光云台配置失败: {str(e)}")

    async def get_ptz_configs_by_ids(self, dualptz_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取双光云台配置"""
        try:
            ptz_configs = await self.repo.get_by_ids(dualptz_ids)
            if not ptz_configs:
                raise ResourceNotFoundError("未找到任何双光云台配置")

            return ApiResponse.success(
                data=[self._format_ptz_response(config) for config in ptz_configs],
                message=f"成功获取 {len(ptz_configs)} 个双光云台配置"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"批量获取双光云台配置失败: {e}", exc_info=True)
            raise BusinessError(f"批量获取双光云台配置失败: {str(e)}")

    async def get_ptz_configs(self, query: DualPTZQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取双光云台配置列表"""
        try:
            ptz_configs, total = await self.repo.get_all(
                page=query.page,
                size=query.size,
                ptz_ip=query.ptz_ip,
                operating_speed=query.operating_speed
            )

            return ApiResponse.paginated(
                items=[self._format_ptz_response(config) for config in ptz_configs],
                total=total,
                page=query.page,
                size=query.size,
                message="获取双光云台配置列表成功"
            )

        except Exception as e:
            logger.error(f"获取双光云台配置列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取双光云台配置列表失败: {str(e)}")

    async def update_ptz_config(self, ptz_id: str, data: DualPTZUpdate, user: dict) -> Dict[str, Any]:
        """更新双光云台配置（单个，兼容旧接口）"""
        try:
            # 检查双光云台配置是否存在
            existing_config = await self.repo.get_by_id(ptz_id)
            if not existing_config:
                raise ResourceNotFoundError(f"双光云台配置ID '{ptz_id}' 不存在")

            # 准备更新数据
            update_data = {k: v for k, v in data.dict().items() if v is not None}
            update_data["updated_by"] = user["username"]

            # 更新双光云台配置
            ptz_config = await self.repo.update(ptz_id, update_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "update_dual_ptz_config",
                f"更新双光云台配置: IP{ptz_config.ptz_ip}, 速度{ptz_config.operating_speed}",
                extra={"ptz_id": ptz_config.id, "ptz_ip": ptz_config.ptz_ip, "operating_speed": ptz_config.operating_speed}
            )

            return ApiResponse.success(
                data=self._format_ptz_response(ptz_config),
                message="双光云台配置更新成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"更新双光云台配置失败: {e}", exc_info=True)
            raise BusinessError(f"更新双光云台配置失败: {str(e)}")
    
    async def batch_update_ptz_configs_by_robot(self, robot_id: str, configs: List[DualPTZCreate], user: dict) -> Dict[str, Any]:
        """批量更新机器人的双光云台配置（真删除旧数据后重新添加）"""
        try:
            from ..repositories.robot_repository import RobotRepository
            # 检查机器人是否存在
            robot_repo = RobotRepository(self.db)
            robot = await robot_repo.get_by_id(robot_id)
            if not robot:
                raise ResourceNotFoundError(f"机器人ID '{robot_id}' 不存在")
            
            # 真删除该机器人的所有旧配置
            deleted_count = await self.repo.hard_delete_by_robot_id(robot_id)
            logger.info(f"删除机器人 {robot_id} 的 {deleted_count} 个旧双光云台配置")
            
            # 创建新配置
            created_configs = []
            for config_data in configs:
                create_data = {
                    **config_data.dict(),
                    "robot_id": robot_id,
                    "created_by": user["username"],
                    "updated_by": user["username"]
                }
                ptz_config = await self.repo.create(create_data)
                created_configs.append(ptz_config)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "batch_update_dual_ptz_configs",
                f"批量更新机器人 {robot_id} 的双光云台配置: 删除{deleted_count}个，新增{len(created_configs)}个",
                extra={"robot_id": robot_id, "deleted_count": deleted_count, "created_count": len(created_configs)}
            )

            return ApiResponse.success(
                data=[self._format_ptz_response(config) for config in created_configs],
                message=f"批量更新双光云台配置成功，删除{deleted_count}个，新增{len(created_configs)}个"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"批量更新双光云台配置失败: {e}", exc_info=True)
            raise BusinessError(f"批量更新双光云台配置失败: {str(e)}")

    async def delete_ptz_config(self, ptz_id: str, user: dict) -> Dict[str, Any]:
        """删除双光云台配置"""
        try:
            # 检查双光云台配置是否存在
            existing_config = await self.repo.get_by_id(ptz_id)
            if not existing_config:
                raise ResourceNotFoundError(f"双光云台配置ID '{ptz_id}' 不存在")

            # 软删除双光云台配置
            success = await self.repo.soft_delete(ptz_id, user["username"])
            if not success:
                raise BusinessError("删除双光云台配置失败")
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "delete_dual_ptz_config",
                f"删除双光云台配置: IP{existing_config.ptz_ip}, 速度{existing_config.operating_speed}",
                extra={"ptz_id": ptz_id, "ptz_ip": existing_config.ptz_ip, "operating_speed": existing_config.operating_speed}
            )

            return ApiResponse.success(
                data={"id": ptz_id},
                message="双光云台配置删除成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"删除双光云台配置失败: {e}", exc_info=True)
            raise BusinessError(f"删除双光云台配置失败: {str(e)}")

    async def get_ptz_config_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取双光云台配置统计信息"""
        try:
            stats = await self.repo.get_stats()
            return ApiResponse.success(
                data=stats,
                message="获取双光云台配置统计信息成功"
            )

        except Exception as e:
            logger.error(f"获取双光云台配置统计信息失败: {e}", exc_info=True)
            raise BusinessError(f"获取双光云台配置统计信息失败: {str(e)}")

    def _format_ptz_response(self, ptz_config) -> Dict[str, Any]:
        """格式化双光云台配置响应数据"""
        return {
            "id": ptz_config.id,
            "robot_id": ptz_config.robot_id,
            "ptz_ip": ptz_config.ptz_ip,
            "subnet_mask": ptz_config.subnet_mask,
            "gateway": ptz_config.gateway,
            "operating_speed": ptz_config.operating_speed,
            "fill_light_enabled": ptz_config.fill_light_enabled,
            "wiper_enabled": ptz_config.wiper_enabled,
            "auto_focus_enabled": ptz_config.auto_focus_enabled,
            "backlight_compensation_enabled": ptz_config.backlight_compensation_enabled,
            "created_at": ptz_config.created_at.strftime("%Y-%m-%dT%H:%M:%S") if ptz_config.created_at else None,
            "updated_at": ptz_config.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if ptz_config.updated_at else None,
            "created_by": ptz_config.created_by,
            "updated_by": ptz_config.updated_by,
        }
