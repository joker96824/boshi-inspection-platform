"""
云台任务Pydantic模式
"""

from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import BaseResponse, BaseSchema


class GimbalTaskBase(BaseSchema):
    """云台任务基础模式"""

    task_name: str = Field(..., min_length=1, max_length=100, description="云台任务名称")
    gimbal_id: str = Field(..., description="所属云台ID")


class GimbalTaskCreate(GimbalTaskBase):
    """云台任务创建模式"""


class GimbalTaskUpdate(BaseSchema):
    """云台任务更新模式"""

    task_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="云台任务名称"
    )
    gimbal_id: Optional[str] = Field(None, description="所属云台ID")
    inspection_project_orders: Optional[
        List["InspectionProjectOrderUpdate"]
    ] = Field(None, description="巡检项目排序配置")


class InspectionProjectOrderUpdate(BaseSchema):
    """巡检项目排序更新模式"""

    inspection_project_id: str = Field(..., description="巡检项目ID")
    sort_order: int = Field(..., ge=0, description="排序值，数字越小越靠前")


class GimbalTaskSummary(BaseSchema):
    """云台任务简要模式（用于嵌套展示）"""

    id: str = Field(..., description="云台任务ID")
    task_name: str = Field(..., description="云台任务名称")


class GimbalInspectionProjectSummary(BaseSchema):
    """云台巡检项目简要模式"""

    id: str = Field(..., description="巡检项目ID")
    task_name: str = Field(..., description="巡检项目名称")
    detection_type: str = Field(..., description="检测类型")
    sort_order: int = Field(..., ge=0, description="排序值，数字越小越靠前")


class GimbalTaskResponse(BaseResponse):
    """云台任务响应模式"""

    id: str = Field(..., description="云台任务ID")
    task_name: str = Field(..., description="云台任务名称")
    gimbal_id: str = Field(..., description="所属云台ID")
    inspection_project_count: int = Field(
        ..., description="关联的云台巡检项目数量"
    )
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")
    inspection_projects: Optional[List["GimbalInspectionProjectSummary"]] = Field(
        None, description="关联的云台巡检项目列表（精简信息）"
    )
    schedule_count: int = Field(..., description="关联的云台日程数量")
    schedules: Optional[List[Dict[str, Any]]] = Field(
        None, description="关联的云台日程信息"
    )


class GimbalTaskQuery(BaseSchema):
    """云台任务查询模式"""

    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    task_name: Optional[str] = Field(None, description="云台任务名称（模糊查询）")
    gimbal_id: Optional[str] = Field(None, description="云台ID筛选")
    map_id: Optional[str] = Field(None, description="地图ID筛选（通过关联云台）")


class GimbalTaskListResponse(BaseSchema):
    """云台任务列表响应模式"""

    items: List[GimbalTaskResponse] = Field(..., description="云台任务列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")


GimbalTaskUpdate.model_rebuild()
GimbalTaskResponse.model_rebuild()
GimbalTaskListResponse.model_rebuild()

