"""
云台巡检记录Pydantic模式
"""

from typing import Any, Dict, List, Optional

from pydantic import Field, validator

from .base import BaseResponse, BaseSchema


class GimbalHistoryBase(BaseSchema):
    """云台巡检记录基础模式"""

    project_preset_point_id: str = Field(..., description="关联云台巡检项目-预设点关联ID")
    record_data: Optional[Dict[str, Any]] = Field(None, description="记录数据")
    media_url: Optional[str] = Field(None, max_length=500, description="图像/视频链接")
    view_status: Optional[str] = Field(None, description="查看状态：pending-未查看, viewed-已查看, processed-已处理（有报警信息时使用，无异常时为空）")
    inspection_result_status: Optional[str] = Field(None, description="巡检结果状态：null-尚未结束（任务进行中）, normal-正常（任务完成且无异常）, warning-预警报警, critical-严重报警, emergency-危机报警")
    
    @validator('view_status')
    def validate_view_status(cls, v):
        """验证查看状态值"""
        if v is not None and v.strip():
            valid_statuses = ['pending', 'viewed', 'processed']
            if v not in valid_statuses:
                raise ValueError(f'查看状态必须是以下值之一: {", ".join(valid_statuses)}')
        return v
    
    @validator('inspection_result_status')
    def validate_inspection_result_status(cls, v):
        """验证巡检结果状态值"""
        if v is not None and v.strip():
            valid_statuses = ['normal', 'warning', 'critical', 'emergency']
            if v not in valid_statuses:
                raise ValueError(f'巡检结果状态必须是以下值之一: {", ".join(valid_statuses)}')
        return v


class GimbalHistoryCreate(GimbalHistoryBase):
    """云台巡检记录创建模式"""


class GimbalHistoryUpdate(BaseSchema):
    """云台巡检记录更新模式"""

    project_preset_point_id: Optional[str] = Field(
        None, description="关联云台巡检项目-预设点关联ID"
    )
    record_data: Optional[Dict[str, Any]] = Field(None, description="记录数据")
    media_url: Optional[str] = Field(None, max_length=500, description="图像/视频链接")
    view_status: Optional[str] = Field(None, description="查看状态：pending-未查看, viewed-已查看, processed-已处理（有报警信息时使用，无异常时为空）")
    inspection_result_status: Optional[str] = Field(None, description="巡检结果状态：null-尚未结束（任务进行中）, normal-正常（任务完成且无异常）, warning-预警报警, critical-严重报警, emergency-危机报警")
    
    @validator('view_status')
    def validate_view_status(cls, v):
        """验证查看状态值"""
        if v is not None and v.strip():
            valid_statuses = ['pending', 'viewed', 'processed']
            if v not in valid_statuses:
                raise ValueError(f'查看状态必须是以下值之一: {", ".join(valid_statuses)}')
        return v
    
    @validator('inspection_result_status')
    def validate_inspection_result_status(cls, v):
        """验证巡检结果状态值"""
        if v is not None and v.strip():
            valid_statuses = ['normal', 'warning', 'critical', 'emergency']
            if v not in valid_statuses:
                raise ValueError(f'巡检结果状态必须是以下值之一: {", ".join(valid_statuses)}')
        return v


class GimbalHistoryResponse(BaseResponse):
    """云台巡检记录响应模式"""

    id: str = Field(..., description="云台记录ID")
    project_preset_point_id: str = Field(..., description="关联云台巡检项目-预设点关联ID")
    inspection_project_id: Optional[str] = Field(None, description="关联云台巡检项目ID（从关联表获取）")
    preset_point_id: Optional[str] = Field(None, description="关联预设点ID（从关联表获取）")
    preset_point_name: Optional[str] = Field(None, description="预设点名称（从关联表获取）")
    detection_type: Optional[str] = Field(None, description="检测类型（从关联表获取）")
    record_data: Optional[Dict[str, Any]] = Field(None, description="记录数据")
    media_url: Optional[str] = Field(None, description="图像/视频链接")
    view_status: Optional[str] = Field(None, description="查看状态：pending-未查看, viewed-已查看, processed-已处理（有报警信息时使用，无异常时为空）")
    inspection_result_status: Optional[str] = Field(None, description="巡检结果状态：null-尚未结束（任务进行中）, normal-正常（任务完成且无异常）, warning-预警报警, critical-严重报警, emergency-危机报警")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class GimbalHistoryQuery(BaseSchema):
    """云台巡检记录查询模式"""

    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    inspection_project_id: Optional[str] = Field(
        None, description="云台巡检项目ID筛选"
    )
    view_status: Optional[str] = Field(None, description="查看状态：pending-未查看, viewed-已查看, processed-已处理")
    inspection_result_status: Optional[str] = Field(None, description="巡检结果状态：null-尚未结束（任务进行中）, normal-正常（任务完成且无异常）, warning-预警报警, critical-严重报警, emergency-危机报警")


class GimbalHistoryListResponse(BaseSchema):
    """云台巡检记录列表响应模式"""

    items: List[GimbalHistoryResponse] = Field(..., description="云台巡检记录列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")
