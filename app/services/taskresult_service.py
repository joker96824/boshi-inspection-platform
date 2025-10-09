"""
任务结果业务逻辑服务
"""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.taskresult_repository import TaskResultRepository
from ..repositories.taskhistory_repository import TaskHistoryRepository
from ..schemas.taskresult import TaskResultCreate, TaskResultUpdate, TaskResultQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class TaskResultService:
    """任务结果业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.taskresult_repo = TaskResultRepository(db)
        self.taskhistory_repo = TaskHistoryRepository(db)

    async def create_taskresult(self, taskresult_data: TaskResultCreate, user: dict) -> Dict[str, Any]:
        """创建任务结果"""
        try:
            # 验证任务记录是否存在
            taskhistory = await self.taskhistory_repo.get_by_id(taskresult_data.taskhistory_id)
            if not taskhistory:
                raise ResourceNotFoundError(f"任务记录ID '{taskresult_data.taskhistory_id}' 不存在")

            # 验证1对1关系：该任务记录是否已有结果
            if await self.taskresult_repo.exists_by_taskhistory_id(taskresult_data.taskhistory_id):
                raise BusinessError(f"任务记录 '{taskresult_data.taskhistory_id}' 已存在结果记录")

            # 验证record_batch是否与任务记录一致
            if taskresult_data.record_batch != taskhistory.record_batch:
                raise BusinessError(f"任务批次 '{taskresult_data.record_batch}' 与任务记录批次 '{taskhistory.record_batch}' 不一致")

            create_data = taskresult_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]

            taskresult = await self.taskresult_repo.create(create_data)

            log_user_action(
                user["username"],
                "create_taskresult",
                "success",
                f"创建任务结果成功，ID: {taskresult.id}"
            )

            return ApiResponse.success(
                data=self._format_taskresult_response(taskresult),
                message="创建任务结果成功"
            )

        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建任务结果失败: {e}")
            raise
        except Exception as e:
            logger.error(f"创建任务结果失败: {e}")
            raise HTTPException(status_code=500, detail="创建任务结果失败")

    async def get_taskresult_by_id(self, taskresult_id: str, user: dict) -> Dict[str, Any]:
        """根据ID获取任务结果"""
        try:
            taskresult = await self.taskresult_repo.get_by_id(taskresult_id)
            if not taskresult:
                raise ResourceNotFoundError(f"任务结果ID '{taskresult_id}' 不存在")

            return ApiResponse.success(
                data=self._format_taskresult_response(taskresult),
                message="获取任务结果成功"
            )

        except ResourceNotFoundError as e:
            logger.warning(f"获取任务结果失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取任务结果失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务结果失败")

    async def get_taskresults_by_ids(self, taskresult_ids: List[str], user: dict) -> Dict[str, Any]:
        """根据ID列表获取任务结果"""
        try:
            taskresults = await self.taskresult_repo.get_by_ids(taskresult_ids)
            
            items_data = [self._format_taskresult_response(taskresult) for taskresult in taskresults]

            return ApiResponse.success(
                data={"items": items_data, "total": len(items_data)},
                message="获取任务结果列表成功"
            )

        except Exception as e:
            logger.error(f"获取任务结果列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务结果列表失败")

    async def get_taskresults(self, query: TaskResultQuery, user: dict) -> Dict[str, Any]:
        """获取任务结果列表（分页）"""
        try:
            taskresults, total = await self.taskresult_repo.get_all(
                page=query.page,
                size=query.size
            )

            items_data = [self._format_taskresult_response(taskresult) for taskresult in taskresults]

            return ApiResponse.paginated(
                items=items_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取任务结果列表成功"
            )

        except Exception as e:
            logger.error(f"获取任务结果列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务结果列表失败")

    async def update_taskresult(self, taskresult_id: str, taskresult_data: TaskResultUpdate, user: dict) -> Dict[str, Any]:
        """更新任务结果"""
        try:
            existing_taskresult = await self.taskresult_repo.get_by_id(taskresult_id)
            if not existing_taskresult:
                raise ResourceNotFoundError(f"任务结果ID '{taskresult_id}' 不存在")

            # 如果要更新任务记录ID，验证新的任务记录是否存在
            if taskresult_data.taskhistory_id:
                taskhistory = await self.taskhistory_repo.get_by_id(taskresult_data.taskhistory_id)
                if not taskhistory:
                    raise ResourceNotFoundError(f"任务记录ID '{taskresult_data.taskhistory_id}' 不存在")

                # 验证1对1关系
                if await self.taskresult_repo.exists_by_taskhistory_id(
                    taskresult_data.taskhistory_id,
                    taskresult_id
                ):
                    raise BusinessError(f"任务记录 '{taskresult_data.taskhistory_id}' 已存在结果记录")

                # 验证record_batch是否与任务记录一致
                record_batch = taskresult_data.record_batch if taskresult_data.record_batch is not None else existing_taskresult.record_batch
                if record_batch != taskhistory.record_batch:
                    raise BusinessError(f"任务批次 '{record_batch}' 与任务记录批次 '{taskhistory.record_batch}' 不一致")

            update_data = taskresult_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]

            updated_taskresult = await self.taskresult_repo.update(taskresult_id, update_data)

            log_user_action(
                user["username"],
                "update_taskresult",
                "success",
                f"更新任务结果成功，ID: {taskresult_id}"
            )

            return ApiResponse.success(
                data=self._format_taskresult_response(updated_taskresult),
                message="更新任务结果成功"
            )

        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"更新任务结果失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新任务结果失败: {e}")
            raise HTTPException(status_code=500, detail="更新任务结果失败")

    async def delete_taskresult(self, taskresult_id: str, user: dict) -> Dict[str, Any]:
        """删除任务结果（软删除）"""
        try:
            existing_taskresult = await self.taskresult_repo.get_by_id(taskresult_id)
            if not existing_taskresult:
                raise ResourceNotFoundError(f"任务结果ID '{taskresult_id}' 不存在")

            success = await self.taskresult_repo.delete(taskresult_id)

            if success:
                log_user_action(
                    user["username"],
                    "delete_taskresult",
                    "success",
                    f"删除任务结果成功，ID: {taskresult_id}"
                )

                return ApiResponse.success(message="删除任务结果成功")
            else:
                raise HTTPException(status_code=500, detail="删除任务结果失败")

        except ResourceNotFoundError as e:
            logger.warning(f"删除任务结果失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除任务结果失败: {e}")
            raise HTTPException(status_code=500, detail="删除任务结果失败")

    async def get_taskresult_stats(self, user: dict) -> Dict[str, Any]:
        """获取任务结果统计信息"""
        try:
            total_count = await self.taskresult_repo.count_all()

            stats = {
                "total_taskresults": total_count
            }

            return ApiResponse.success(
                data=stats,
                message="获取任务结果统计成功"
            )

        except Exception as e:
            logger.error(f"获取任务结果统计失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务结果统计失败")

    def _format_taskresult_response(self, taskresult) -> Dict[str, Any]:
        """格式化任务结果响应数据"""
        return {
            "id": taskresult.id,
            "taskhistory_id": taskresult.taskhistory_id,
            "record_batch": taskresult.record_batch,
            "result_point_id": taskresult.result_point_id,
            "result_item_id": taskresult.result_item_id,
            "result_file_url": taskresult.result_file_url,
            "result_collect_time": taskresult.result_collect_time.strftime("%Y-%m-%dT%H:%M:%S") if taskresult.result_collect_time else None,
            "created_at": taskresult.created_at.strftime("%Y-%m-%dT%H:%M:%S") if taskresult.created_at else None,
            "updated_at": taskresult.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if taskresult.updated_at else None,
            "created_by": taskresult.created_by,
            "updated_by": taskresult.updated_by,
        }
