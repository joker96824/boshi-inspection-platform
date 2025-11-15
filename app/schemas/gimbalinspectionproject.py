"""
云台巡检项目Pydantic模式
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import Field

from .base import BaseResponse, BaseSchema


class GimbalInspectionProjectBase(BaseSchema):
    """云台巡检项目基础模式"""

    task_name: str = Field(..., min_length=1, max_length=100, description="巡检项目名称")
    gimbaltask_id: str = Field(..., description="关联云台任务ID")
    sort_order: Optional[int] = Field(
        None, ge=0, description="排序值，数字越小越靠前"
    )
    x_coordinate: Optional[float] = Field(None, description="镜头X轴旋转参数")
    y_coordinate: Optional[float] = Field(None, description="镜头Y轴旋转参数")
    zoom_level: Optional[float] = Field(None, description="倍率")
    focus: Optional[float] = Field(None, description="聚焦")
    aperture: Optional[int] = Field(None, ge=0, le=100, description="光圈（0-100）")
    shutter: Optional[int] = Field(None, ge=1, description="快门分母")
    backlight_compensation: bool = Field(False, description="背光补偿")
    wide_dynamic: bool = Field(False, description="宽动态")
    strong_light_suppression: bool = Field(False, description="强光抑制")
    fill_light: bool = Field(False, description="补光")
    detection_type: Literal["可见光视频", "可见光图片", "热成像图片", "热成像视频"] = Field(
        ..., description="检测类型"
    )


class GimbalInspectionProjectCreate(GimbalInspectionProjectBase):
    """云台巡检项目创建模式"""


class GimbalInspectionProjectUpdate(BaseSchema):
    """云台巡检项目更新模式"""

    task_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="巡检项目名称"
    )
    gimbaltask_id: Optional[str] = Field(None, description="关联云台任务ID")
    sort_order: Optional[int] = Field(
        None, ge=0, description="排序值，数字越小越靠前"
    )
    x_coordinate: Optional[float] = Field(None, description="镜头X轴旋转参数")
    y_coordinate: Optional[float] = Field(None, description="镜头Y轴旋转参数")
    zoom_level: Optional[float] = Field(None, description="倍率")
    focus: Optional[float] = Field(None, description="聚焦")
    aperture: Optional[int] = Field(None, ge=0, le=100, description="光圈（0-100）")
    shutter: Optional[int] = Field(None, ge=1, description="快门分母")
    backlight_compensation: Optional[bool] = Field(None, description="背光补偿")
    wide_dynamic: Optional[bool] = Field(None, description="宽动态")
    strong_light_suppression: Optional[bool] = Field(None, description="强光抑制")
    fill_light: Optional[bool] = Field(None, description="补光")
    detection_type: Optional[Literal["可见光视频", "可见光图片", "热成像图片", "热成像视频"]] = Field(
        None, description="检测类型"
    )


class GimbalInspectionProjectResponse(BaseResponse):
    """云台巡检项目响应模式"""

    id: str = Field(..., description="巡检项目ID")
    task_name: str = Field(..., description="巡检项目名称")
    gimbaltask_id: str = Field(..., description="关联云台任务ID")
    zoom_level: Optional[float] = Field(None, description="倍率")
    x_coordinate: Optional[float] = Field(None, description="镜头X轴旋转参数")
    y_coordinate: Optional[float] = Field(None, description="镜头Y轴旋转参数")
    sort_order: int = Field(..., ge=0, description="排序值，数字越小越靠前")
    focus: Optional[float] = Field(None, description="聚焦")
    aperture: Optional[int] = Field(None, description="光圈（0-100）")
    shutter: Optional[int] = Field(None, description="快门分母")
    backlight_compensation: bool = Field(..., description="背光补偿")
    wide_dynamic: bool = Field(..., description="宽动态")
    strong_light_suppression: bool = Field(..., description="强光抑制")
    fill_light: bool = Field(..., description="补光")
    detection_type: str = Field(..., description="检测类型")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class GimbalInspectionProjectQuery(BaseSchema):
    """云台巡检项目查询模式"""

    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    task_name: Optional[str] = Field(None, description="巡检项目名称（模糊查询）")
    detection_type: Optional[Literal["可见光视频", "可见光图片", "热成像图片", "热成像视频"]] = Field(
        None, description="检测类型筛选"
    )
    gimbaltask_id: Optional[str] = Field(None, description="云台任务ID筛选")
    gimbal_id: Optional[str] = Field(None, description="云台ID筛选（通过云台任务）")
    map_id: Optional[str] = Field(None, description="地图ID筛选（通过关联云台）")


class GimbalInspectionProjectListResponse(BaseSchema):
    """云台巡检项目列表响应模式"""

    items: List[GimbalInspectionProjectResponse] = Field(
        ..., description="云台巡检项目列表"
    )
    pagination: Dict[str, Any] = Field(..., description="分页信息")

