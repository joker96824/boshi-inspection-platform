"""
任务Pydantic模式
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from .base import BaseSchema, BaseResponse


class TaskBase(BaseSchema):
    """任务基础模式"""
    task_name: str = Field(..., min_length=1, max_length=100, description="任务名称")
    robot_id: str = Field(..., description="执行机器人ID")
    task_items: Optional[List[str]] = Field(None, description="任务巡检项目ID列表")
    task_order: int = Field(0, ge=0, description="任务执行顺序")
    task_res_prior: int = Field(1, ge=1, le=10, description="响应优先级 (1-10)")
    task_int_prior: int = Field(1, ge=1, le=10, description="打断优先级 (1-10)")


class TaskCreate(TaskBase):
    """任务创建模式"""
    pass


class TaskUpdate(BaseSchema):
    """任务更新模式"""
    task_name: Optional[str] = Field(None, min_length=1, max_length=100, description="任务名称")
    task_items: Optional[List[str]] = Field(None, description="任务巡检项目ID列表")
    task_order: Optional[int] = Field(None, ge=0, description="任务执行顺序")
    task_res_prior: Optional[int] = Field(None, ge=1, le=10, description="响应优先级 (1-10)")
    task_int_prior: Optional[int] = Field(None, ge=1, le=10, description="打断优先级 (1-10)")


class TaskItemResponse(BaseModel):
    """任务巡检项目响应模式"""
    id: str = Field(..., description="巡检项目ID")
    item_name: str = Field(..., description="巡检项目名称")
    item_info: Dict[str, Any] = Field(..., description="巡检参数信息")
    device_id: str = Field(..., description="设备ID")
    device_name: Optional[str] = Field(None, description="设备名称")
    point_id: Optional[str] = Field(None, description="巡检点ID")
    point_name: Optional[str] = Field(None, description="巡检点名称")
    enabled: bool = Field(..., description="巡检项目本身的启用状态")
    executable: bool = Field(..., description="是否可执行（考虑上级启用状态：Item、Device、Point都必须启用）")
    disabled_reason: Optional[str] = Field(None, description="不可执行的原因（当executable为false时）")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class TaskResponse(BaseResponse):
    """任务响应模式"""
    task_name: str = Field(..., description="任务名称")
    robot_id: str = Field(..., description="执行机器人ID")
    robot_name: Optional[str] = Field(None, description="机器人名称")
    task_items: Optional[List[TaskItemResponse]] = Field(None, description="任务巡检项目列表（包含执行状态）")
    task_order: int = Field(..., description="任务执行顺序")
    task_res_prior: int = Field(..., description="响应优先级")
    task_int_prior: int = Field(..., description="打断优先级")


class TaskQuery(BaseSchema):
    """任务查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    task_name: Optional[str] = Field(None, description="任务名称（模糊匹配）")
    robot_id: Optional[str] = Field(None, description="机器人ID")
    map_id: Optional[str] = Field(None, description="地图ID（通过机器人-地图关联筛选）")
    sort_by: Optional[str] = Field("task_order", description="排序字段: task_order, task_res_prior, task_int_prior")
    sort_order: Optional[str] = Field("asc", description="排序顺序: asc(正序), desc(反序)")
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        if v and v not in ['task_order', 'task_res_prior', 'task_int_prior']:
            raise ValueError('sort_by 必须是 task_order, task_res_prior 或 task_int_prior 之一')
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v and v not in ['asc', 'desc']:
            raise ValueError('sort_order 必须是 asc 或 desc 之一')
        return v


class TaskListResponse(BaseSchema):
    """任务列表响应模式"""
    items: List[TaskResponse] = Field(..., description="任务列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")