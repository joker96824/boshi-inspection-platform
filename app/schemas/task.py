"""
任务Pydantic模式
"""

from typing import Optional, Dict, Any, List
from pydantic import Field, validator
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


class TaskResponse(BaseResponse):
    """任务响应模式"""
    task_name: str = Field(..., description="任务名称")
    robot_id: str = Field(..., description="执行机器人ID")
    robot_name: Optional[str] = Field(None, description="机器人名称")
    task_items: Optional[List[str]] = Field(None, description="任务巡检项目ID列表")
    task_order: int = Field(..., description="任务执行顺序")
    task_res_prior: int = Field(..., description="响应优先级")
    task_int_prior: int = Field(..., description="打断优先级")


class TaskQuery(BaseSchema):
    """任务查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    task_name: Optional[str] = Field(None, description="任务名称（模糊匹配）")
    robot_id: Optional[str] = Field(None, description="机器人ID")
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