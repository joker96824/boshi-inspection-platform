"""
云台巡检项目Pydantic模式
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from .base import BaseResponse, BaseSchema


class GimbalInspectionProjectBase(BaseSchema):
    """云台巡检项目基础模式"""

    task_name: str = Field(..., min_length=1, max_length=100, description="巡检项目名称")
    gimbaltask_id: str = Field(..., description="关联云台任务ID")
    sort_order: Optional[int] = Field(
        None, ge=0, description="排序值，数字越小越靠前"
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


class PresetPointLinkResponse(BaseModel):
    """预设点关联响应模式（用于巡检项目中的预设点）"""
    id: str = Field(..., description="预设点ID")
    preset_name: str = Field(..., description="预设点名称")
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
    detection_type: str = Field(..., description="检测类型")
    video_duration: Optional[int] = Field(None, description="拍摄时长（秒）")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")


class GimbalInspectionProjectResponse(BaseResponse):
    """云台巡检项目响应模式"""

    id: str = Field(..., description="巡检项目ID")
    task_name: str = Field(..., description="巡检项目名称")
    gimbaltask_id: str = Field(..., description="关联云台任务ID")
    sort_order: int = Field(..., ge=0, description="排序值，数字越小越靠前")
    preset_points: List[PresetPointLinkResponse] = Field(default_factory=list, description="关联的预设点列表")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class GimbalInspectionProjectQuery(BaseSchema):
    """云台巡检项目查询模式"""

    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    task_name: Optional[str] = Field(None, description="巡检项目名称（模糊查询）")
    gimbaltask_id: Optional[str] = Field(None, description="云台任务ID筛选")
    gimbal_id: Optional[str] = Field(None, description="云台ID筛选（通过云台任务）")
    map_id: Optional[str] = Field(None, description="地图ID筛选（通过关联云台）")


class GimbalInspectionProjectListResponse(BaseSchema):
    """云台巡检项目列表响应模式"""

    items: List[GimbalInspectionProjectResponse] = Field(
        ..., description="云台巡检项目列表"
    )
    pagination: Dict[str, Any] = Field(..., description="分页信息")

