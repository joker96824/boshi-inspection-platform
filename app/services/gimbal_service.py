"""
云台业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.gimbal_repository import GimbalRepository
from ..schemas.gimbal import GimbalCreate, GimbalUpdate, GimbalQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class GimbalService:
    """云台业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.gimbal_repo = GimbalRepository(db)
    
    async def create_gimbal(self, gimbal_data: GimbalCreate, user: dict) -> Dict[str, Any]:
        """创建云台"""
        try:
            # 检查云台名是否已存在
            if await self.gimbal_repo.exists_by_name(gimbal_data.gimbal_name):
                raise BusinessError(f"云台名称 '{gimbal_data.gimbal_name}' 已存在")
            
            create_data = gimbal_data.dict()
            if create_data.get("ip_address") is not None:
                create_data["ip_address"] = str(create_data["ip_address"])
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            gimbal = await self.gimbal_repo.create(create_data)
            
            log_user_action(
                user["username"],
                "create_gimbal",
                "success",
                f"创建云台成功，ID: {gimbal.id}"
            )
            
            return ApiResponse.success(
                data=self._format_gimbal_response(gimbal),
                message="创建云台成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建云台失败: {e}")
            raise
        except Exception as e:
            logger.error(f"创建云台失败: {e}", exc_info=True)
            raise BusinessError(f"创建云台失败: {str(e)}")
    
    async def get_gimbal_by_id(self, gimbal_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取云台"""
        try:
            gimbal = await self.gimbal_repo.get_by_id(gimbal_id)
            if not gimbal:
                raise ResourceNotFoundError(f"云台ID '{gimbal_id}' 不存在")
            
            return ApiResponse.success(
                data=self._format_gimbal_response(gimbal),
                message="获取云台成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"获取云台失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取云台失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台失败: {str(e)}")
    
    async def get_gimbals_by_ids(self, gimbal_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取云台"""
        try:
            gimbals = await self.gimbal_repo.get_by_ids(gimbal_ids)
            
            gimbals_data = [self._format_gimbal_response(gimbal) for gimbal in gimbals]
            
            return ApiResponse.success(
                data={"gimbals": gimbals_data, "total": len(gimbals_data)},
                message="获取云台列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取云台列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台列表失败: {str(e)}")
    
    async def get_gimbals(self, query: GimbalQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取云台列表"""
        try:
            # 如果未提供分页参数，返回所有数据
            if query.page is None or query.size is None:
                gimbals, total = await self.gimbal_repo.get_all(
                    page=None,
                    size=None,
                    gimbal_name=query.gimbal_name,
                    map_id=query.map_id,
                    sort_by=query.sort_by,
                    sort_order=query.sort_order
                )
                gimbals_data = [self._format_gimbal_response(gimbal) for gimbal in gimbals]
                return ApiResponse.success(
                    data={"items": gimbals_data, "total": total},
                    message="获取云台列表成功"
                )
            
            gimbals, total = await self.gimbal_repo.get_all(
                page=query.page,
                size=query.size,
                gimbal_name=query.gimbal_name,
                map_id=query.map_id,
                sort_by=query.sort_by,
                sort_order=query.sort_order
            )
            
            # 格式化响应数据
            gimbals_data = [self._format_gimbal_response(gimbal) for gimbal in gimbals]
            
            return ApiResponse.paginated(
                items=gimbals_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取云台列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取云台列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台列表失败: {str(e)}")
    
    async def update_gimbal(self, gimbal_id: str, gimbal_data: GimbalUpdate, user: dict) -> Dict[str, Any]:
        """更新云台"""
        try:
            # 检查云台是否存在
            existing_gimbal = await self.gimbal_repo.get_by_id(gimbal_id)
            if not existing_gimbal:
                raise ResourceNotFoundError(f"云台ID '{gimbal_id}' 不存在")
            
            # 如果更新了名称，检查是否重复
            if (gimbal_data.gimbal_name and 
                gimbal_data.gimbal_name != existing_gimbal.gimbal_name and
                await self.gimbal_repo.exists_by_name(gimbal_data.gimbal_name, gimbal_id)):
                raise BusinessError(f"云台名称 '{gimbal_data.gimbal_name}' 已存在")
            
            update_data = gimbal_data.dict(exclude_unset=True)
            if update_data.get("ip_address") is not None:
                update_data["ip_address"] = str(update_data["ip_address"])
            update_data["updated_by"] = user["username"]
            
            updated_gimbal = await self.gimbal_repo.update(gimbal_id, update_data)
            
            log_user_action(
                user["username"],
                "update_gimbal",
                "success",
                f"更新云台成功，ID: {gimbal_id}"
            )
            
            return ApiResponse.success(
                data=self._format_gimbal_response(updated_gimbal),
                message="更新云台成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"更新云台失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新云台失败: {e}", exc_info=True)
            raise BusinessError(f"更新云台失败: {str(e)}")
    
    async def delete_gimbal(self, gimbal_id: str, user: dict) -> Dict[str, Any]:
        """删除云台"""
        try:
            # 检查云台是否存在
            existing_gimbal = await self.gimbal_repo.get_by_id(gimbal_id)
            if not existing_gimbal:
                raise ResourceNotFoundError(f"云台ID '{gimbal_id}' 不存在")
            
            # 删除云台
            success = await self.gimbal_repo.soft_delete(gimbal_id, user["username"])
            
            if success:
                log_user_action(
                    user["username"],
                    "delete_gimbal",
                    "success",
                    f"删除云台成功，ID: {gimbal_id}"
                )
                
                return ApiResponse.success(
                    data={"id": gimbal_id},
                    message="删除云台成功"
                )
            else:
                raise BusinessError("删除云台失败")
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"删除云台失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除云台失败: {e}", exc_info=True)
            raise BusinessError(f"删除云台失败: {str(e)}")
    
    async def get_gimbal_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取云台统计信息"""
        try:
            total_count = await self.gimbal_repo.count_all()
            
            stats = {
                "total_gimbals": total_count
            }
            
            return ApiResponse.success(
                data=stats,
                message="获取云台统计成功"
            )
            
        except Exception as e:
            logger.error(f"获取云台统计失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台统计失败: {str(e)}")
    
    def _format_preset_points_response(self, preset_points) -> List[Dict[str, Any]]:
        """格式化预设点列表响应数据"""
        if not preset_points:
            return []
        
        preset_points_info = []
        active_preset_points = [pp for pp in preset_points if not pp.is_deleted]
        for preset_point in active_preset_points:
            preset_points_info.append({
                "id": preset_point.id,
                "preset_name": preset_point.preset_name,
                "gimbal_id": preset_point.gimbal_id,
                "p_coordinate": preset_point.p_coordinate,
                "t_coordinate": preset_point.t_coordinate,
                "z_coordinate": preset_point.z_coordinate,
                "f_coordinate": preset_point.f_coordinate,
                "aperture": preset_point.aperture,
                "shutter": preset_point.shutter,
                "backlight_compensation": preset_point.backlight_compensation,
                "wide_dynamic": preset_point.wide_dynamic,
                "strong_light_suppression": preset_point.strong_light_suppression,
                "fill_light": preset_point.fill_light,
                "image_url": preset_point.image_url,
                "created_at": preset_point.created_at.strftime("%Y-%m-%dT%H:%M:%S") if preset_point.created_at else None,
                "updated_at": preset_point.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if preset_point.updated_at else None,
                "created_by": preset_point.created_by,
                "updated_by": preset_point.updated_by,
            })
        
        return preset_points_info
    
    def _format_gimbal_response(self, gimbal) -> Dict[str, Any]:
        """格式化云台响应数据（包含任务和日程列表）"""
        # 格式化任务列表（包含日程）
        gimbal_tasks_info = []
        if gimbal.gimbal_tasks:
            active_tasks = [t for t in gimbal.gimbal_tasks if not t.is_deleted]
            for task in active_tasks:
                schedules_info = []
                if task.schedules:
                    active_schedules = [s for s in task.schedules if not s.is_deleted]
                    for schedule in active_schedules:
                        time_display_start_str = (
                            schedule.time_display_start.strftime("%H:%M")
                            if schedule.time_display_start
                            else None
                        )
                        time_display_end_str = (
                            schedule.time_display_end.strftime("%H:%M")
                            if schedule.time_display_end
                            else None
                        )
                        
                        # 动态计算周期显示文本
                        cycle_display = self._calculate_cycle_display(schedule.cycle_type, schedule.cycle_config)

                        schedules_info.append(
                            {
                                "id": schedule.id,
                                "gimbaltask_id": schedule.gimbaltask_id,
                                "schedule_name": schedule.schedule_name,
                                "start_date": schedule.start_date.strftime("%Y-%m-%d")
                                if schedule.start_date
                                else None,
                                "end_date": schedule.end_date.strftime("%Y-%m-%d")
                                if schedule.end_date
                                else None,
                                "enabled": schedule.enabled,
                                "cycle_type": schedule.cycle_type,
                                "cycle_config": schedule.cycle_config,
                                "time_mode": schedule.time_mode,
                                "time_config": schedule.time_config,
                                "cycle_display": cycle_display,
                                "time_display_start": time_display_start_str,
                                "time_display_end": time_display_end_str,
                                "created_at": schedule.created_at.strftime(
                                    "%Y-%m-%dT%H:%M:%S"
                                )
                                if schedule.created_at
                                else None,
                                "updated_at": schedule.updated_at.strftime(
                                    "%Y-%m-%dT%H:%M:%S"
                                )
                                if schedule.updated_at
                                else None,
                            }
                        )

                inspection_projects_info = []
                if task.inspection_projects:
                    active_projects = sorted(
                        [p for p in task.inspection_projects if not p.is_deleted],
                        key=lambda project: project.sort_order,
                    )
                    for project in active_projects:
                        # 格式化预设点关联信息
                        preset_points_info = []
                        if hasattr(project, 'preset_points') and project.preset_points:
                            for pp_link in project.preset_points:
                                preset_point = pp_link.preset_point if hasattr(pp_link, 'preset_point') else None
                                if preset_point and not preset_point.is_deleted:
                                    preset_points_info.append({
                                        "id": preset_point.id,
                                        "preset_name": preset_point.preset_name,
                                        "p_coordinate": preset_point.p_coordinate,
                                        "t_coordinate": preset_point.t_coordinate,
                                        "z_coordinate": preset_point.z_coordinate,
                                        "f_coordinate": preset_point.f_coordinate,
                                        "aperture": preset_point.aperture,
                                        "shutter": preset_point.shutter,
                                        "backlight_compensation": preset_point.backlight_compensation,
                                        "wide_dynamic": preset_point.wide_dynamic,
                                        "strong_light_suppression": preset_point.strong_light_suppression,
                                        "fill_light": preset_point.fill_light,
                                        "image_url": preset_point.image_url,
                                        "detection_type": pp_link.detection_type,
                                        "video_duration": pp_link.video_duration,
                                        "created_at": preset_point.created_at.strftime("%Y-%m-%dT%H:%M:%S") if preset_point.created_at else None,
                                        "updated_at": preset_point.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if preset_point.updated_at else None,
                                    })
                        
                        inspection_projects_info.append(
                            {
                                "id": project.id,
                                "task_name": project.task_name,
                                "sort_order": project.sort_order,
                                "preset_points": preset_points_info,
                                "created_at": project.created_at.strftime(
                                    "%Y-%m-%dT%H:%M:%S"
                                )
                                if project.created_at
                                else None,
                                "updated_at": project.updated_at.strftime(
                                    "%Y-%m-%dT%H:%M:%S"
                                )
                                if project.updated_at
                                else None,
                            }
                        )

                gimbal_tasks_info.append(
                    {
                        "id": task.id,
                        "task_name": task.task_name,
                        "gimbal_id": task.gimbal_id,
                        "inspection_project_count": len(inspection_projects_info),
                        "inspection_projects": inspection_projects_info,
                        "schedule_count": len(schedules_info),
                        "schedules": schedules_info,
                        "created_at": task.created_at.strftime("%Y-%m-%dT%H:%M:%S")
                        if task.created_at
                        else None,
                        "updated_at": task.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
                        if task.updated_at
                        else None,
                    }
                )

        return {
            "id": gimbal.id,
            "gimbal_name": gimbal.gimbal_name,
            "map_id": gimbal.map_id,
            "enabled": gimbal.enabled,
            "ip_address": str(gimbal.ip_address) if gimbal.ip_address else None,
            "port": gimbal.port,
            "username": gimbal.username,
            "password": gimbal.password,
            "rtsp_main_url": gimbal.rtsp_main_url,
            "rtsp_sub_url": gimbal.rtsp_sub_url,
            "channel": gimbal.channel,
            "x_coordinate": gimbal.x_coordinate,
            "y_coordinate": gimbal.y_coordinate,
            "p_coordinate": gimbal.p_coordinate,
            "t_coordinate": gimbal.t_coordinate,
            "z_coordinate": gimbal.z_coordinate,
            "f_coordinate": gimbal.f_coordinate,
            "preview_url": gimbal.preview_url,
            "control_url": gimbal.control_url,
            "gimbal_tasks": gimbal_tasks_info,  # 添加任务列表（包含日程）
            "preset_points": self._format_preset_points_response(gimbal.preset_points) if hasattr(gimbal, 'preset_points') and gimbal.preset_points else [],  # 添加全部预设点列表
            "created_at": gimbal.created_at.strftime("%Y-%m-%dT%H:%M:%S") if gimbal.created_at else None,
            "updated_at": gimbal.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if gimbal.updated_at else None,
            "created_by": gimbal.created_by,
            "updated_by": gimbal.updated_by,
        }
    
    def _calculate_cycle_display(self, cycle_type: Optional[str], cycle_config: Optional[Dict[str, Any]]) -> str:
        """计算周期显示文本"""
        if not cycle_type:
            return ''
        
        if cycle_type == 'daily':
            return '每天'
        elif cycle_type == 'monthly_days' and cycle_config and 'selectedDays' in cycle_config:
            days = cycle_config['selectedDays']
            if days:
                days_str = '、'.join([str(d) for d in sorted(days)])
                return f'每月{days_str}日'
        elif cycle_type == 'weekly' and cycle_config and 'selectedWeeks' in cycle_config:
            week_names = ['一', '二', '三', '四', '五', '六', '日']
            weeks = [week_names[w-1] for w in sorted(cycle_config['selectedWeeks']) if 1 <= w <= 7]
            if weeks:
                weeks_str = '、'.join([f'周{w}' for w in weeks])
                return f'每{weeks_str}'
        
        return ''

