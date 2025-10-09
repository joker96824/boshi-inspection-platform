"""
日志相关Pydantic模式
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import Field, validator
from .base import BaseResponse, BaseSchema


class LogFileInfo(BaseResponse):
    """日志文件信息模式"""
    filename: str = Field(..., description="日志文件名")
    file_path: str = Field(..., description="文件路径")
    file_size: int = Field(..., description="文件大小（字节）")
    file_size_mb: float = Field(..., description="文件大小（MB）")
    created_at: datetime = Field(..., description="创建时间")
    modified_at: datetime = Field(..., description="修改时间")
    log_type: str = Field(..., description="日志类型: app/error/debug")


class LogQuery(BaseSchema):
    """日志查询请求模式"""
    start_date: Optional[date] = Field(None, description="开始日期 (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="结束日期 (YYYY-MM-DD)")
    log_type: Optional[str] = Field("app", description="日志类型: app/error/debug/all")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")

    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('结束日期不能早于开始日期')
        return v

    @validator('log_type')
    def validate_log_type(cls, v):
        valid_types = ['app', 'error', 'debug', 'all']
        if v not in valid_types:
            raise ValueError(f'日志类型必须是: {", ".join(valid_types)}')
        return v


class LogContentQuery(BaseSchema):
    """日志内容查询请求模式"""
    log_date: date = Field(..., description="日志日期 (YYYY-MM-DD)")
    log_type: str = Field("app", description="日志类型: app/error/debug")
    start_line: int = Field(1, ge=1, description="开始行号")
    limit: int = Field(100, ge=1, le=1000, description="读取行数")
    search_keyword: Optional[str] = Field(None, description="搜索关键词")

    @validator('log_type')
    def validate_log_type(cls, v):
        valid_types = ['app', 'error', 'debug']
        if v not in valid_types:
            raise ValueError(f'日志类型必须是: {", ".join(valid_types)}')
        return v


class LogDownloadRequest(BaseSchema):
    """日志下载请求模式"""
    log_date: date = Field(..., description="日志日期 (YYYY-MM-DD)")
    log_type: str = Field("app", description="日志类型: app/error/debug")

    @validator('log_type')
    def validate_log_type(cls, v):
        valid_types = ['app', 'error', 'debug']
        if v not in valid_types:
            raise ValueError(f'日志类型必须是: {", ".join(valid_types)}')
        return v


class LogContent(BaseResponse):
    """日志内容响应模式"""
    content: List[str] = Field(..., description="日志内容行列表")
    total_lines: int = Field(..., description="文件总行数")
    current_start: int = Field(..., description="当前开始行号")
    current_end: int = Field(..., description="当前结束行号")
    has_more: bool = Field(..., description="是否还有更多内容")


class LogFileListResponse(BaseSchema):
    """日志文件列表响应模式"""
    total: int = Field(..., description="总文件数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    items: List[LogFileInfo] = Field(..., description="日志文件列表")


class LogStatsResponse(BaseResponse):
    """日志统计响应模式"""
    total_dirs: int = Field(..., description="日志目录总数")
    total_size_mb: float = Field(..., description="总占用空间(MB)")
    date_range: dict = Field(..., description="日期范围")
    log_types: dict = Field(..., description="各类型日志统计")
