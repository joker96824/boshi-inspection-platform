"""
云台巡检记录业务逻辑服务
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.logging import get_logger, log_user_action
from ..core.exceptions import BusinessError, ResourceNotFoundError
from ..repositories.gimbalhistory_repository import GimbalHistoryRepository
from ..repositories.gimbalinspectionproject_repository import (
    GimbalInspectionProjectRepository,
)
from ..repositories.alarminfo_repository import AlarmInfoRepository
from ..schemas.gimbalhistory import (
    GimbalHistoryCreate,
    GimbalHistoryQuery,
    GimbalHistoryUpdate,
)
from ..utils.response import ApiResponse

logger = get_logger(__name__)


class GimbalHistoryService:
    """云台巡检记录业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.gimbal_history_repo = GimbalHistoryRepository(db)
        self.alarminfo_repo = AlarmInfoRepository(db)

    async def create_gimbal_history(
        self, history_data: GimbalHistoryCreate, user: dict
    ) -> Dict[str, Any]:
        """创建云台巡检记录"""
        try:
            # 验证关联ID是否存在（通过查询历史记录来验证外键约束）
            # 外键约束会在数据库层面验证，这里只需要创建数据
            create_data = history_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]

            history = await self.gimbal_history_repo.create(create_data)

            # 获取关联的报警信息（新创建的记录通常没有报警信息）
            alarminfos = await self.alarminfo_repo.get_by_gimbalhistory_id(history.id)

            log_user_action(
                user["username"],
                "create_gimbal_history",
                "success",
                f"创建云台巡检记录成功，ID: {history.id}",
            )

            return ApiResponse.success(
                data=self._format_gimbal_history_response(history, alarminfos),
                message="创建云台巡检记录成功",
            )

        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建云台巡检记录失败: {e}")
            raise
        except IntegrityError as e:
            error_msg = str(e.orig) if hasattr(e, "orig") else str(e)
            if "foreign key constraint" in error_msg.lower() or "1452" in error_msg:
                logger.error(f"创建云台巡检记录失败-外键约束错误: {error_msg}")
                raise BusinessError("关联的巡检项目-预设点关联不存在，请检查关联ID是否正确")
            else:
                logger.error(f"创建云台巡检记录失败-数据库完整性错误: {error_msg}")
                raise BusinessError("数据完整性验证失败")
        except Exception as e:
            logger.error(f"创建云台巡检记录失败: {e}", exc_info=True)
            raise BusinessError(f"创建云台巡检记录失败: {str(e)}")

    async def get_gimbal_history_by_id(
        self, history_id: str, user: Optional[dict]
    ) -> Dict[str, Any]:
        """根据ID获取云台巡检记录"""
        try:
            history = await self.gimbal_history_repo.get_by_id(history_id)
            if not history:
                raise ResourceNotFoundError(f"云台巡检记录ID '{history_id}' 不存在")

            # 获取关联的报警信息
            alarminfos = await self.alarminfo_repo.get_by_gimbalhistory_id(history_id)

            return ApiResponse.success(
                data=self._format_gimbal_history_response(history, alarminfos),
                message="获取云台巡检记录成功",
            )

        except ResourceNotFoundError as e:
            logger.warning(f"获取云台巡检记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取云台巡检记录失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台巡检记录失败: {str(e)}")

    async def get_gimbal_histories_by_ids(
        self, gimbalhistory_ids: List[str], user: Optional[dict]
    ) -> Dict[str, Any]:
        """根据ID列表获取云台巡检记录"""
        try:
            histories = await self.gimbal_history_repo.get_by_ids(gimbalhistory_ids)

            # 获取所有记录的报警信息
            history_ids = [h.id for h in histories]
            alarminfos_dict = await self.alarminfo_repo.get_by_gimbalhistory_ids(history_ids)
            
            histories_data = [
                self._format_gimbal_history_response(history, alarminfos_dict.get(history.id, [])) 
                for history in histories
            ]

            return ApiResponse.success(
                data={"gimbal_histories": histories_data, "total": len(histories_data)},
                message="获取云台巡检记录列表成功",
            )

        except Exception as e:
            logger.error(f"获取云台巡检记录列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台巡检记录列表失败: {str(e)}")

    async def get_gimbal_histories(
        self, query: GimbalHistoryQuery, user: Optional[dict]
    ) -> Dict[str, Any]:
        """获取云台巡检记录列表"""
        try:
            histories, total = await self.gimbal_history_repo.get_all(
                page=query.page,
                size=query.size,
                inspection_project_id=query.inspection_project_id,
                view_status=query.view_status,
                inspection_result_status=query.inspection_result_status,
            )

            # 获取所有记录的报警信息
            history_ids = [h.id for h in histories]
            alarminfos_dict = await self.alarminfo_repo.get_by_gimbalhistory_ids(history_ids)
            
            histories_data = [
                self._format_gimbal_history_response(history, alarminfos_dict.get(history.id, [])) 
                for history in histories
            ]

            return ApiResponse.paginated(
                items=histories_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取云台巡检记录列表成功",
            )

        except Exception as e:
            logger.error(f"获取云台巡检记录列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台巡检记录列表失败: {str(e)}")

    async def update_gimbal_history(
        self, history_id: str, history_data: GimbalHistoryUpdate, user: dict
    ) -> Dict[str, Any]:
        """更新云台巡检记录"""
        try:
            existing_history = await self.gimbal_history_repo.get_by_id(history_id)
            if not existing_history:
                raise ResourceNotFoundError(f"云台巡检记录ID '{history_id}' 不存在")

            # 如果更新了关联ID，外键约束会在数据库层面验证

            update_data = history_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]

            updated_history = await self.gimbal_history_repo.update(
                history_id, update_data
            )

            # 获取关联的报警信息
            alarminfos = await self.alarminfo_repo.get_by_gimbalhistory_id(history_id)

            log_user_action(
                user["username"],
                "update_gimbal_history",
                "success",
                f"更新云台巡检记录成功，ID: {history_id}",
            )

            return ApiResponse.success(
                data=self._format_gimbal_history_response(updated_history, alarminfos),
                message="更新云台巡检记录成功",
            )

        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"更新云台巡检记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新云台巡检记录失败: {e}", exc_info=True)
            raise BusinessError(f"更新云台巡检记录失败: {str(e)}")

    async def delete_gimbal_history(
        self, history_id: str, user: dict
    ) -> Dict[str, Any]:
        """删除云台巡检记录"""
        try:
            existing_history = await self.gimbal_history_repo.get_by_id(history_id)
            if not existing_history:
                raise ResourceNotFoundError(f"云台巡检记录ID '{history_id}' 不存在")

            success = await self.gimbal_history_repo.soft_delete(
                history_id, user["username"]
            )

            if not success:
                raise BusinessError("删除云台巡检记录失败")

            log_user_action(
                user["username"],
                "delete_gimbal_history",
                "success",
                f"删除云台巡检记录成功，ID: {history_id}",
            )

            return ApiResponse.success(
                data={"history_id": history_id}, message="删除云台巡检记录成功"
            )

        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"删除云台巡检记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除云台巡检记录失败: {e}", exc_info=True)
            raise BusinessError(f"删除云台巡检记录失败: {str(e)}")

    async def get_gimbal_history_stats(
        self, user: Optional[dict]
    ) -> Dict[str, Any]:
        """获取云台巡检记录统计信息"""
        try:
            total_count = await self.gimbal_history_repo.count_all()

            stats = {"total_histories": total_count}

            return ApiResponse.success(
                data=stats, message="获取云台巡检记录统计成功"
            )

        except Exception as e:
            logger.error(f"获取云台巡检记录统计失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台巡检记录统计失败: {str(e)}")

    def _format_gimbal_history_response(self, history, alarminfos: List = None) -> Dict[str, Any]:
        """格式化云台巡检记录响应数据"""
        # 从关联表中获取相关信息
        inspection_project_id = None
        preset_point_id = None
        preset_point_name = None
        detection_type = None
        
        if hasattr(history, 'project_preset_point') and history.project_preset_point:
            link = history.project_preset_point
            inspection_project_id = link.inspection_project_id if hasattr(link, 'inspection_project_id') else None
            preset_point_id = link.preset_point_id if hasattr(link, 'preset_point_id') else None
            detection_type = link.detection_type if hasattr(link, 'detection_type') else None
            
            # 获取预设点名称
            if hasattr(link, 'preset_point') and link.preset_point:
                preset_point_name = link.preset_point.preset_name if hasattr(link.preset_point, 'preset_name') else None
        
        # 格式化报警信息
        alarminfos_data = []
        if alarminfos:
            for alarminfo in alarminfos:
                alarminfos_data.append(self._format_alarminfo_response(alarminfo))
        
        return {
            "id": history.id,
            "project_preset_point_id": history.project_preset_point_id,
            "inspection_project_id": inspection_project_id,
            "preset_point_id": preset_point_id,
            "preset_point_name": preset_point_name,
            "detection_type": detection_type,
            "record_data": history.record_data,
            "media_url": history.media_url,
            "view_status": history.view_status,
            "inspection_result_status": history.inspection_result_status,
            "alarm_infos": alarminfos_data,
            "created_at": history.created_at.strftime("%Y-%m-%dT%H:%M:%S")
            if history.created_at
            else None,
            "updated_at": history.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
            if history.updated_at
            else None,
            "created_by": history.created_by,
            "updated_by": history.updated_by,
        }
    
    def _format_alarminfo_response(self, alarminfo) -> Dict[str, Any]:
        """格式化报警信息响应数据"""
        return {
            "id": alarminfo.id,
            "alarm_rule_id": alarminfo.alarm_rule_id,
            "alarm_category": alarminfo.alarm_category,
            "alarm_level": alarminfo.alarm_level,
            "alarm_status": alarminfo.alarm_status,
            "source_type": alarminfo.source_type,
            "source_ids": alarminfo.source_ids,
            "relation_type": alarminfo.relation_type,
            "relation_ids": alarminfo.relation_ids,
            "trigger_item_ids": alarminfo.trigger_item_ids,
            "trigger_project_ids": alarminfo.trigger_project_ids,
            "trigger_data": alarminfo.trigger_data,
            "calculated_value": alarminfo.calculated_value,
            "alarm_message": alarminfo.alarm_message,
            "processed_by": alarminfo.processed_by,
            "processed_at": alarminfo.processed_at.strftime("%Y-%m-%dT%H:%M:%S") if alarminfo.processed_at else None,
            "process_remark": alarminfo.process_remark,
            "created_at": alarminfo.created_at.strftime("%Y-%m-%dT%H:%M:%S") if alarminfo.created_at else None,
            "updated_at": alarminfo.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if alarminfo.updated_at else None,
        }

