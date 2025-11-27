"""
检测类型数据验证模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseResponse


class DetectionTypeBase(BaseSchema):
    """检测类型基础模式"""
    type_name: str = Field(..., min_length=1, max_length=50, description="检测类型名称")
    type_code: str = Field(..., min_length=1, max_length=20, description="检测类型代码")
    description: Optional[str] = Field(None, max_length=200, description="检测类型描述")
    sort_order: int = Field(0, description="排序顺序")
    enabled: bool = Field(True, description="启用状态：True-启用，False-禁用")


class DetectionTypeCreate(DetectionTypeBase):
    """检测类型创建模式"""
    pass


class DetectionTypeUpdate(BaseSchema):
    """检测类型更新模式"""
    type_name: Optional[str] = Field(None, min_length=1, max_length=50, description="检测类型名称")
    type_code: Optional[str] = Field(None, min_length=1, max_length=20, description="检测类型代码")
    description: Optional[str] = Field(None, max_length=200, description="检测类型描述")
    sort_order: Optional[int] = Field(None, description="排序顺序")
    enabled: Optional[bool] = Field(None, description="启用状态：True-启用，False-禁用")


class DetectionTypeResponse(BaseResponse):
    """检测类型响应模式"""
    id: str = Field(..., description="检测类型ID")
    type_name: str = Field(..., description="检测类型名称")
    type_code: str = Field(..., description="检测类型代码")
    description: Optional[str] = Field(None, description="检测类型描述")
    sort_order: int = Field(..., description="排序顺序")
    enabled: bool = Field(..., description="启用状态：True-启用，False-禁用")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class DetectionTypeQuery(BaseSchema):
    """检测类型查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    type_name: Optional[str] = Field(None, description="检测类型名称（模糊查询）")
    type_code: Optional[str] = Field(None, description="检测类型代码（精确查询）")
    enabled: Optional[bool] = Field(None, description="启用状态（筛选）")


class DetectionTypeListResponse(BaseSchema):
    """检测类型列表响应模式"""
    items: List[DetectionTypeResponse] = Field(..., description="检测类型列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")

