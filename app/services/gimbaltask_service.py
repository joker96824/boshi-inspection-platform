"""
云台任务业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from ..repositories.gimbaltask_repository import GimbalTaskRepository
from ..repositories.gimbal_repository import GimbalRepository
from ..schemas.gimbaltask import GimbalTaskCreate, GimbalTaskUpdate, GimbalTaskQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError, ValidationError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class GimbalTaskService:
    """云台任务业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.gimbal_task_repo = GimbalTaskRepository(db)
        self.gimbal_repo = GimbalRepository(db)
    
    async def create_gimbal_task(self, task_data: GimbalTaskCreate, user: dict) -> Dict[str, Any]:
        """创建云台任务"""
        try:
            # 检查云台任务名是否已存在
            if await self.gimbal_task_repo.exists_by_name(task_data.task_name):
                raise BusinessError(f"云台任务名称 '{task_data.task_name}' 已存在")
            
            # 验证任务类型
            if task_data.task_type not in ['image', 'video']:
                raise ValidationError("任务类别必须是 'image' 或 'video'")
            
            # 验证云台ID是否存在
            if task_data.gimbal_id:
                gimbal = await self.gimbal_repo.get_by_id(task_data.gimbal_id)
                if not gimbal:
                    raise ResourceNotFoundError(f"云台ID '{task_data.gimbal_id}' 不存在")
            
            create_data = task_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            task = await self.gimbal_task_repo.create(create_data)
            
            log_user_action(
                user["username"],
                "create_gimbal_task",
                "success",
                f"创建云台任务成功，ID: {task.id}"
            )
            
            return ApiResponse.success(
                data=self._format_gimbal_task_response(task),
                message="创建云台任务成功"
            )
            
        except (ResourceNotFoundError, BusinessError, ValidationError) as e:
            logger.warning(f"创建云台任务失败: {e}")
            raise
        except IntegrityError as e:
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if "foreign key constraint" in error_msg.lower() or "1452" in error_msg:
                logger.error(f"创建云台任务失败-外键约束错误: {error_msg}")
                raise BusinessError("关联的云台不存在，请检查云台ID是否正确")
            elif "Duplicate entry" in error_msg or "1062" in error_msg:
                logger.error(f"创建云台任务失败-唯一性约束错误: {error_msg}")
                raise BusinessError(f"云台任务名称 '{task_data.task_name}' 已存在")
            else:
                logger.error(f"创建云台任务失败-数据库完整性错误: {error_msg}")
                raise BusinessError(f"数据完整性验证失败")
        except Exception as e:
            logger.error(f"创建云台任务失败: {e}", exc_info=True)
            raise BusinessError(f"创建云台任务失败: {str(e)}")
    
    async def get_gimbal_task_by_id(self, task_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取云台任务"""
        try:
            task = await self.gimbal_task_repo.get_by_id(task_id)
            if not task:
                raise ResourceNotFoundError(f"云台任务ID '{task_id}' 不存在")
            
            return ApiResponse.success(
                data=self._format_gimbal_task_response(task),
                message="获取云台任务成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"获取云台任务失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取云台任务失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台任务失败: {str(e)}")
    
    async def get_gimbal_tasks_by_ids(self, gimbaltask_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取云台任务"""
        try:
            tasks = await self.gimbal_task_repo.get_by_ids(gimbaltask_ids)
            
            tasks_data = [self._format_gimbal_task_response(task) for task in tasks]
            
            return ApiResponse.success(
                data={"gimbal_tasks": tasks_data, "total": len(tasks_data)},
                message="获取云台任务列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取云台任务列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台任务列表失败: {str(e)}")
    
    async def get_gimbal_tasks(self, query: GimbalTaskQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取云台任务列表"""
        try:
            tasks, total = await self.gimbal_task_repo.get_all(
                page=query.page,
                size=query.size,
                task_name=query.task_name,
                task_type=query.task_type,
                gimbal_id=query.gimbal_id
            )
            
            # 格式化响应数据
            tasks_data = [self._format_gimbal_task_response(task) for task in tasks]
            
            return ApiResponse.paginated(
                items=tasks_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取云台任务列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取云台任务列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台任务列表失败: {str(e)}")
    
    async def update_gimbal_task(self, task_id: str, task_data: GimbalTaskUpdate, user: dict) -> Dict[str, Any]:
        """更新云台任务"""
        try:
            # 检查云台任务是否存在
            existing_task = await self.gimbal_task_repo.get_by_id(task_id)
            if not existing_task:
                raise ResourceNotFoundError(f"云台任务ID '{task_id}' 不存在")
            
            # 如果更新了名称，检查是否重复
            if (task_data.task_name and 
                task_data.task_name != existing_task.task_name and
                await self.gimbal_task_repo.exists_by_name(task_data.task_name, task_id)):
                raise BusinessError(f"云台任务名称 '{task_data.task_name}' 已存在")
            
            # 验证任务类型
            if task_data.task_type and task_data.task_type not in ['image', 'video']:
                raise BusinessError("任务类别必须是 'image' 或 'video'")
            
            update_data = task_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]
            
            updated_task = await self.gimbal_task_repo.update(task_id, update_data)
            
            log_user_action(
                user["username"],
                "update_gimbal_task",
                "success",
                f"更新云台任务成功，ID: {task_id}"
            )
            
            return ApiResponse.success(
                data=self._format_gimbal_task_response(updated_task),
                message="更新云台任务成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"更新云台任务失败: {e}")
            raise
        except IntegrityError as e:
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if "foreign key constraint" in error_msg.lower() or "1452" in error_msg:
                logger.error(f"更新云台任务失败-外键约束错误: {error_msg}")
                raise BusinessError("关联的云台不存在，请检查云台ID是否正确")
            else:
                logger.error(f"更新云台任务失败-数据库完整性错误: {error_msg}")
                raise BusinessError(f"数据完整性验证失败")
        except Exception as e:
            logger.error(f"更新云台任务失败: {e}", exc_info=True)
            raise BusinessError(f"更新云台任务失败: {str(e)}")
    
    async def delete_gimbal_task(self, task_id: str, user: dict) -> Dict[str, Any]:
        """删除云台任务"""
        try:
            # 检查云台任务是否存在
            existing_task = await self.gimbal_task_repo.get_by_id(task_id)
            if not existing_task:
                raise ResourceNotFoundError(f"云台任务ID '{task_id}' 不存在")
            
            # 删除云台任务
            success = await self.gimbal_task_repo.soft_delete(task_id, user["username"])
            
            if success:
                log_user_action(
                    user["username"],
                    "delete_gimbal_task",
                    "success",
                    f"删除云台任务成功，ID: {task_id}"
                )
                
                return ApiResponse.success(
                    data={"task_id": task_id},
                    message="删除云台任务成功"
                )
            else:
                raise BusinessError("删除云台任务失败")
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"删除云台任务失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除云台任务失败: {e}", exc_info=True)
            raise BusinessError(f"删除云台任务失败: {str(e)}")
    
    async def get_gimbal_task_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取云台任务统计信息"""
        try:
            total_count = await self.gimbal_task_repo.count_all()
            
            stats = {
                "total_gimbal_tasks": total_count
            }
            
            return ApiResponse.success(
                data=stats,
                message="获取云台任务统计成功"
            )
            
        except Exception as e:
            logger.error(f"获取云台任务统计失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台任务统计失败: {str(e)}")
    
    def _format_gimbal_task_response(self, task) -> Dict[str, Any]:
        """格式化云台任务响应数据"""
        return {
            "id": task.id,
            "task_name": task.task_name,
            "angle_params": task.angle_params,
            "task_type": task.task_type,
            "gimbal_id": task.gimbal_id,
            "created_at": task.created_at.strftime("%Y-%m-%dT%H:%M:%S") if task.created_at else None,
            "updated_at": task.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if task.updated_at else None,
            "created_by": task.created_by,
            "updated_by": task.updated_by,
        }
