"""
云台预设点Pydantic模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseResponse


class GimbalPresetPointBase(BaseSchema):
    """云台预设点基础模式"""
    preset_name: str = Field(..., min_length=1, max_length=100, description="预设点名称")
    gimbal_id: str = Field(..., description="关联云台ID")
    p_coordinate: Optional[float] = Field(None, description="P坐标（水平旋转）")
    t_coordinate: Optional[float] = Field(None, description="T坐标（垂直旋转）")
    z_coordinate: Optional[float] = Field(None, description="Z坐标（变焦）")
    f_coordinate: Optional[float] = Field(None, description="F坐标（聚焦）")
    aperture: Optional[int] = Field(None, ge=0, le=100, description="光圈（0-100）")
    shutter: Optional[int] = Field(None, description="快门分母")
    backlight_compensation: bool = Field(False, description="背光补偿")
    wide_dynamic: bool = Field(False, description="宽动态")
    strong_light_suppression: bool = Field(False, description="强光抑制")
    fill_light: bool = Field(False, description="补光")
    image_url: Optional[str] = Field(None, max_length=500, description="图片链接")


class GimbalPresetPointCreate(GimbalPresetPointBase):
    """云台预设点创建模式"""
    pass


class GimbalPresetPointUpdate(BaseSchema):
    """云台预设点更新模式"""
    preset_name: Optional[str] = Field(None, min_length=1, max_length=100, description="预设点名称")
    p_coordinate: Optional[float] = Field(None, description="P坐标（水平旋转）")
    t_coordinate: Optional[float] = Field(None, description="T坐标（垂直旋转）")
    z_coordinate: Optional[float] = Field(None, description="Z坐标（变焦）")
    f_coordinate: Optional[float] = Field(None, description="F坐标（聚焦）")
    aperture: Optional[int] = Field(None, ge=0, le=100, description="光圈（0-100）")
    shutter: Optional[int] = Field(None, description="快门分母")
    backlight_compensation: Optional[bool] = Field(None, description="背光补偿")
    wide_dynamic: Optional[bool] = Field(None, description="宽动态")
    strong_light_suppression: Optional[bool] = Field(None, description="强光抑制")
    fill_light: Optional[bool] = Field(None, description="补光")
    image_url: Optional[str] = Field(None, max_length=500, description="图片链接")


class GimbalPresetPointResponse(BaseResponse):
    """云台预设点响应模式"""
    id: str = Field(..., description="预设点ID")
    preset_name: str = Field(..., description="预设点名称")
    gimbal_id: str = Field(..., description="关联云台ID")
    p_coordinate: Optional[float] = Field(None, description="P坐标（水平旋转）")
    t_coordinate: Optional[float] = Field(None, description="T坐标（垂直旋转）")
    z_coordinate: Optional[float] = Field(None, description="Z坐标（变焦）")
    f_coordinate: Optional[float] = Field(None, description="F坐标（聚焦）")
    aperture: Optional[int] = Field(None, description="光圈（0-100）")
    shutter: Optional[int] = Field(None, description="快门分母")
    backlight_compensation: bool = Field(..., description="背光补偿")
    wide_dynamic: bool = Field(..., description="宽动态")
    strong_light_suppression: bool = Field(..., description="强光抑制")
    fill_light: bool = Field(..., description="补光")
    image_url: Optional[str] = Field(None, description="图片链接")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class GimbalPresetPointQuery(BaseSchema):
    """云台预设点查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    preset_name: Optional[str] = Field(None, description="预设点名称（模糊查询）")
    gimbal_id: Optional[str] = Field(None, description="云台ID筛选")
    sort_by: str = Field("created_at", description="排序字段：created_at/preset_name/updated_at")
    sort_order: str = Field("desc", description="排序方向：asc/desc")


class GimbalPresetPointListResponse(BaseSchema):
    """云台预设点列表响应模式"""
    items: List[GimbalPresetPointResponse] = Field(..., description="预设点列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")

