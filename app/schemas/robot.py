"""
机器人相关模式
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseResponse


class RobotBase(BaseSchema):
    """机器人基础模式"""
    robot_name: str = Field(..., min_length=1, max_length=100, description="机器人名称")
    robot_info: Optional[Dict[str, Any]] = Field(None, description="机器人信息")
    factory_id: Optional[str] = Field(None, description="厂区ID")
    map_ids: Optional[List[str]] = Field(None, description="关联地图ID列表")


class RobotCreate(RobotBase):
    """机器人创建模式"""
    pass


class RobotUpdate(BaseSchema):
    """机器人更新模式"""
    robot_name: Optional[str] = Field(None, min_length=1, max_length=100, description="机器人名称")
    robot_info: Optional[Dict[str, Any]] = Field(None, description="机器人信息")
    factory_id: Optional[str] = Field(None, description="厂区ID")
    map_ids: Optional[List[str]] = Field(None, description="关联地图ID列表")


class RobotResponse(BaseResponse):
    """机器人响应模式"""
    user_id: str = Field(..., description="所属用户ID")
    robot_name: str = Field(..., description="机器人名称")
    robot_info: Optional[Dict[str, Any]] = Field(None, description="机器人信息")


class RobotQuery(BaseSchema):
    """机器人查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    robot_name: Optional[str] = Field(None, description="机器人名称（模糊匹配）")
    factory_id: Optional[str] = Field(None, description="厂区ID筛选")
    map_id: Optional[str] = Field(None, description="地图ID筛选（通过中间表）")


class RobotListResponse(BaseSchema):
    """机器人列表响应模式"""
    items: List[RobotResponse] = Field(..., description="机器人列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")
