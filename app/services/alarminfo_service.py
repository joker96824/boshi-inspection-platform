"""
报警信息业务逻辑服务
"""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.alarminfo_repository import AlarmInfoRepository
from ..repositories.alarmrule_repository import AlarmRuleRepository
from ..schemas.alarminfo import AlarmInfoCreate, AlarmInfoUpdate, AlarmInfoQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class AlarmInfoService:
    """报警信息业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.alarminfo_repo = AlarmInfoRepository(db)
        self.alarmrule_repo = AlarmRuleRepository(db)

    async def get_alarminfo_by_id(self, alarminfo_id: str, user: dict) -> Dict[str, Any]:
        """根据ID获取报警信息"""
        try:
            alarminfo = await self.alarminfo_repo.get_by_id(alarminfo_id)
            if not alarminfo:
                raise ResourceNotFoundError(f"报警信息ID '{alarminfo_id}' 不存在")

            return ApiResponse.success(
                data=self._format_alarminfo_response(alarminfo),
                message="获取报警信息成功"
            )

        except ResourceNotFoundError as e:
            logger.warning(f"获取报警信息失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取报警信息失败: {e}", exc_info=True)
            raise BusinessError(f"获取报警信息失败: {str(e)}")

    async def get_alarminfos(self, query: AlarmInfoQuery, user: dict) -> Dict[str, Any]:
        """获取报警信息列表（分页）"""
        try:
            alarminfos, total = await self.alarminfo_repo.get_all(
                page=query.page,
                size=query.size,
                alarm_rule_id=query.alarm_rule_id,
                alarm_category=query.alarm_category,
                alarm_level=query.alarm_level,
                alarm_status=query.alarm_status,
                source_type=query.source_type,
                relation_type=query.relation_type,
                relation_id=query.relation_id,
                trigger_item_id=query.trigger_item_id,
                trigger_project_id=query.trigger_project_id
            )

            items_data = [self._format_alarminfo_response(alarminfo) for alarminfo in alarminfos]

            return ApiResponse.paginated(
                items=items_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取报警信息列表成功"
            )

        except Exception as e:
            logger.error(f"获取报警信息列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取报警信息列表失败: {str(e)}")

    async def update_alarm_status(self, alarminfo_id: str, alarm_status: str, user: dict) -> Dict[str, Any]:
        """更新报警状态"""
        try:
            alarminfo = await self.alarminfo_repo.get_by_id(alarminfo_id)
            if not alarminfo:
                raise ResourceNotFoundError(f"报警信息ID '{alarminfo_id}' 不存在")

            update_data = {
                "alarm_status": alarm_status,
                "updated_by": user["username"]
            }
            updated_alarminfo = await self.alarminfo_repo.update(alarminfo_id, update_data)

            return ApiResponse.success(
                data=self._format_alarminfo_response(updated_alarminfo),
                message="更新报警状态成功"
            )

        except ResourceNotFoundError as e:
            logger.warning(f"更新报警状态失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新报警状态失败: {e}", exc_info=True)
            raise BusinessError(f"更新报警状态失败: {str(e)}")

    async def process_alarm(self, alarminfo_id: str, process_remark: str, user: dict) -> Dict[str, Any]:
        """处理报警"""
        try:
            from datetime import datetime

            alarminfo = await self.alarminfo_repo.get_by_id(alarminfo_id)
            if not alarminfo:
                raise ResourceNotFoundError(f"报警信息ID '{alarminfo_id}' 不存在")

            update_data = {
                "alarm_status": "processed",
                "processed_by": user["username"],
                "processed_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "process_remark": process_remark,
                "updated_by": user["username"]
            }
            updated_alarminfo = await self.alarminfo_repo.update(alarminfo_id, update_data)

            log_user_action(
                user["username"],
                "process_alarm",
                "success",
                f"处理报警成功，ID: {alarminfo_id}"
            )

            return ApiResponse.success(
                data=self._format_alarminfo_response(updated_alarminfo),
                message="处理报警成功"
            )

        except ResourceNotFoundError as e:
            logger.warning(f"处理报警失败: {e}")
            raise
        except Exception as e:
            logger.error(f"处理报警失败: {e}", exc_info=True)
            raise BusinessError(f"处理报警失败: {str(e)}")

    async def delete_alarminfo(self, alarminfo_id: str, user: dict) -> Dict[str, Any]:
        """删除报警信息（软删除）"""
        try:
            alarminfo = await self.alarminfo_repo.get_by_id(alarminfo_id)
            if not alarminfo:
                raise ResourceNotFoundError(f"报警信息ID '{alarminfo_id}' 不存在")

            success = await self.alarminfo_repo.delete(alarminfo_id)

            if success:
                log_user_action(
                    user["username"],
                    "delete_alarminfo",
                    "success",
                    f"删除报警信息成功，ID: {alarminfo_id}"
                )

                return ApiResponse.success(
                    data={"id": alarminfo_id},
                    message="删除报警信息成功"
                )
            else:
                raise BusinessError("删除报警信息失败")

        except ResourceNotFoundError as e:
            logger.warning(f"删除报警信息失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除报警信息失败: {e}", exc_info=True)
            raise BusinessError(f"删除报警信息失败: {str(e)}")

    async def get_alarm_stats(self, user: dict) -> Dict[str, Any]:
        """获取报警统计信息"""
        try:
            total_count = await self.alarminfo_repo.count_all()

            # 按分类统计
            inspection_list, _ = await self.alarminfo_repo.get_all(
                page=None, size=None, alarm_category='inspection'
            )
            gimbal_list, _ = await self.alarminfo_repo.get_all(
                page=None, size=None, alarm_category='gimbal'
            )
            sensor_list, _ = await self.alarminfo_repo.get_all(
                page=None, size=None, alarm_category='sensor'
            )
            robot_list, _ = await self.alarminfo_repo.get_all(
                page=None, size=None, alarm_category='robot'
            )

            # 按状态统计
            unviewed_list, _ = await self.alarminfo_repo.get_all(
                page=None, size=None, alarm_status='unviewed'
            )
            unprocessed_list, _ = await self.alarminfo_repo.get_all(
                page=None, size=None, alarm_status='unprocessed'
            )
            processed_list, _ = await self.alarminfo_repo.get_all(
                page=None, size=None, alarm_status='processed'
            )

            stats = {
                "total": total_count,
                "by_category": {
                    "inspection": len(inspection_list),
                    "gimbal": len(gimbal_list),
                    "sensor": len(sensor_list),
                    "robot": len(robot_list),
                    "other": total_count - len(inspection_list) - len(gimbal_list) - len(sensor_list) - len(robot_list)
                },
                "by_status": {
                    "unviewed": len(unviewed_list),
                    "unprocessed": len(unprocessed_list),
                    "processed": len(processed_list)
                }
            }

            return ApiResponse.success(
                data=stats,
                message="获取报警统计成功"
            )

        except Exception as e:
            logger.error(f"获取报警统计失败: {e}", exc_info=True)
            raise BusinessError(f"获取报警统计失败: {str(e)}")

    def _format_alarminfo_response(self, alarminfo) -> Dict[str, Any]:
        """格式化报警信息响应数据"""
        return {
            "id": alarminfo.id,
            "alarm_rule_id": alarminfo.alarm_rule_id,
            "alarm_category": alarminfo.alarm_category,
            "alarm_level": alarminfo.alarm_level,
            "alarm_status": alarminfo.alarm_status,
            "source_type": alarminfo.source_type,
            "source_ids": alarminfo.source_ids if isinstance(alarminfo.source_ids, list) else [],
            "relation_type": alarminfo.relation_type,
            "relation_ids": alarminfo.relation_ids if isinstance(alarminfo.relation_ids, list) else [],
            "trigger_item_ids": alarminfo.trigger_item_ids if isinstance(alarminfo.trigger_item_ids, list) else [],
            "trigger_project_ids": alarminfo.trigger_project_ids if isinstance(alarminfo.trigger_project_ids, list) else [],
            "trigger_data": alarminfo.trigger_data,
            "calculated_value": alarminfo.calculated_value,
            "alarm_message": alarminfo.alarm_message,
            "processed_by": alarminfo.processed_by,
            "processed_at": alarminfo.processed_at,
            "process_remark": alarminfo.process_remark,
            "created_at": alarminfo.created_at.strftime("%Y-%m-%dT%H:%M:%S") if alarminfo.created_at else None,
            "updated_at": alarminfo.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if alarminfo.updated_at else None,
            "created_by": alarminfo.created_by,
            "updated_by": alarminfo.updated_by,
        }
