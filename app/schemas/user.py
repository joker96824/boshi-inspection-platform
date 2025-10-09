"""
用户相关Pydantic模式
"""

from datetime import datetime
from typing import Optional, List
from pydantic import Field, validator
from .base import BaseResponse, BaseSchema
from ..utils.validators import validate_mobile, validate_email


class UserBase(BaseResponse):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    mobile: Optional[str] = Field(None, description="手机号（11位数字）")
    email: Optional[str] = Field(None, description="邮箱（格式：*@*.com）")
    role: str = Field("user", description="角色: super_admin/admin/operator/viewer/user")

    @validator('mobile')
    def validate_mobile_format(cls, v):
        if v is not None and v != '' and not validate_mobile(v):
            raise ValueError('手机号必须为11位数字')
        return v

    @validator('email')
    def validate_email_format(cls, v):
        if v is not None and v != '' and not validate_email(v):
            raise ValueError('邮箱格式必须为 *@*.com')
        return v


class UserCreate(BaseSchema):
    """用户创建模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    mobile: str = Field(..., description="手机号（11位数字）")
    email: Optional[str] = Field(None, description="邮箱（格式：*@*.com）")

    @validator('mobile')
    def validate_mobile_format(cls, v):
        # mobile是必填字段，不允许为空
        if not validate_mobile(v):
            raise ValueError('手机号必须为11位数字')
        return v

    @validator('email')
    def validate_email_format(cls, v):
        if v is not None and v != '' and not validate_email(v):
            raise ValueError('邮箱格式必须为 *@*.com')
        return v


class UserUpdate(BaseSchema):
    """用户更新模式"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="新用户名")
    mobile: Optional[str] = Field(None, description="手机号（11位数字）")
    email: Optional[str] = Field(None, description="邮箱（格式：*@*.com）")
    role: Optional[str] = Field(None, description="角色")
    new_password: Optional[str] = Field(None, min_length=6, max_length=100, description="新密码（无需旧密码）")

    @validator('mobile')
    def validate_mobile_format(cls, v):
        if v is not None and v != '' and not validate_mobile(v):
            raise ValueError('手机号必须为11位数字')
        return v

    @validator('email')
    def validate_email_format(cls, v):
        if v is not None and v != '' and not validate_email(v):
            raise ValueError('邮箱格式必须为 *@*.com')
        return v


class UserPasswordUpdate(BaseSchema):
    """用户自己修改密码模式"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


class UserResponse(UserBase):
    """用户响应模式"""
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")


class UserLogin(BaseSchema):
    """用户登录模式"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")




class UserListResponse(BaseSchema):
    """用户列表响应模式"""
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    items: List[UserResponse] = Field(..., description="用户列表")