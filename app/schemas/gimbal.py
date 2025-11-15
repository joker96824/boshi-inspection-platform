"""
云台Pydantic模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, IPvAnyAddress
from .base import BaseSchema, BaseResponse


class GimbalBase(BaseSchema):
    """云台基础模式"""
    gimbal_name: str = Field(..., min_length=1, max_length=100, description="云台名称")
    map_id: Optional[str] = Field(None, description="地图ID")
    ip_address: IPvAnyAddress = Field(..., description="云台IP地址")
    port: int = Field(..., ge=1, le=65535, description="云台端口")
    username: str = Field(..., min_length=1, max_length=100, description="登录用户名")
    password: str = Field(..., min_length=1, max_length=255, description="登录密码")
    rtsp_main_url: str = Field(..., min_length=1, max_length=255, description="RTSP主码流地址")
    rtsp_sub_url: Optional[str] = Field(None, max_length=255, description="RTSP子码流地址")
    channel: int = Field(1, ge=1, le=2, description="通道号：1或2")
    x_coordinate: Optional[float] = Field(None, description="X坐标（地图横坐标）")
    y_coordinate: Optional[float] = Field(None, description="Y坐标（地图纵坐标）")
    p_coordinate: Optional[float] = Field(None, description="P坐标")
    t_coordinate: Optional[float] = Field(None, description="T坐标")
    z_coordinate: Optional[float] = Field(None, description="Z坐标")
    f_coordinate: Optional[float] = Field(None, description="F坐标")


class GimbalCreate(GimbalBase):
    """云台创建模式"""
    pass


class GimbalUpdate(BaseSchema):
    """云台更新模式"""
    gimbal_name: Optional[str] = Field(None, min_length=1, max_length=100, description="云台名称")
    map_id: Optional[str] = Field(None, description="地图ID")
    ip_address: Optional[IPvAnyAddress] = Field(None, description="云台IP地址")
    port: Optional[int] = Field(None, ge=1, le=65535, description="云台端口")
    username: Optional[str] = Field(None, min_length=1, max_length=100, description="登录用户名")
    password: Optional[str] = Field(None, min_length=1, max_length=255, description="登录密码")
    rtsp_main_url: Optional[str] = Field(None, min_length=1, max_length=255, description="RTSP主码流地址")
    rtsp_sub_url: Optional[str] = Field(None, max_length=255, description="RTSP子码流地址")
    channel: Optional[int] = Field(None, ge=1, le=2, description="通道号：1或2")
    x_coordinate: Optional[float] = Field(None, description="X坐标（地图横坐标）")
    y_coordinate: Optional[float] = Field(None, description="Y坐标（地图纵坐标）")
    p_coordinate: Optional[float] = Field(None, description="P坐标")
    t_coordinate: Optional[float] = Field(None, description="T坐标")
    z_coordinate: Optional[float] = Field(None, description="Z坐标")
    f_coordinate: Optional[float] = Field(None, description="F坐标")


class GimbalResponse(BaseResponse):
    """云台响应模式"""
    id: str = Field(..., description="云台ID")
    gimbal_name: str = Field(..., description="云台名称")
    map_id: Optional[str] = Field(None, description="地图ID")
    ip_address: str = Field(..., description="云台IP地址")
    port: int = Field(..., description="云台端口")
    username: str = Field(..., description="登录用户名")
    password: str = Field(..., description="登录密码")
    rtsp_main_url: str = Field(..., description="RTSP主码流地址")
    rtsp_sub_url: Optional[str] = Field(None, description="RTSP子码流地址")
    channel: int = Field(..., description="通道号")
    x_coordinate: Optional[float] = Field(None, description="X坐标（地图横坐标）")
    y_coordinate: Optional[float] = Field(None, description="Y坐标（地图纵坐标）")
    p_coordinate: Optional[float] = Field(None, description="P坐标")
    t_coordinate: Optional[float] = Field(None, description="T坐标")
    z_coordinate: Optional[float] = Field(None, description="Z坐标")
    f_coordinate: Optional[float] = Field(None, description="F坐标")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class GimbalQuery(BaseSchema):
    """云台查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    gimbal_name: Optional[str] = Field(None, description="云台名称（模糊查询）")
    map_id: Optional[str] = Field(None, description="地图ID筛选")
    sort_by: str = Field("created_at", description="排序字段：created_at/gimbal_name/updated_at")
    sort_order: str = Field("desc", description="排序方向：asc/desc")


class GimbalListResponse(BaseSchema):
    """云台列表响应模式"""
    items: List[GimbalResponse] = Field(..., description="云台列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")

